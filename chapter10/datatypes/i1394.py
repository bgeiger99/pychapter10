
import struct

from .base import IterativeBase, Item


class I1394(IterativeBase):
    data_attrs = IterativeBase.data_attrs + (
        'pbt',
        'sy',
        'tc',
        'ipc',
        'reset',
    )

    def parse(self):
        IterativeBase.parse(self)

        if self.format > 1:
            raise NotImplementedError('IEEE-1394 format %s is reserved!'
                                      % self.format)

        data = self.data[:]

        offset = 0
        if self.format == 0:
            self.pbt = self.csdw[:-29].int    # Packet Body Type
            self.sy = self.csdw[-28:-25].int  # Synchronization Code
            self.tc = self.csdw[-15:].int     # Transaction Count

            # Bus Status
            if self.pbt == 0:
                self.reset = (self.data >> 31) & 0x1

            # Data Streaming
            elif self.pbt == 1:
                self.all.append(Item(self.data, 'IEEE-1394 Transaction'))

            # General Purpose
            elif self.pbt == 2:
                length = len(data) / self.tc

                for i in range(self.tc):
                    ipts = self.data[offset:offset + 8]
                    offset += 8

                    data = self.data[offset:offset + length - 8]
                    offset += (length - 8)
                    self.all.append(Item(data, 'IEEE-1394 Transaction',
                                         ipts=ipts))

        elif self.format == 1:
            self.ipc = self.csdw[-15:].int  # Intra Packet Count

            for i in range(self.ipc):
                attrs = {'ipts': self.data[offset:offset + 8]}
                offset += 8

                iph = struct.unpack('=I', self.data[offset:offset + 4])
                attrs.update({
                    'status': int(iph >> 24),
                    'speed': int(iph >> 21) & 0xf,
                    'trfovf': int((iph >> 18) & 0b11),
                    'lbo': iph >> 17,
                    'data_length': int(iph & 0xffff)})
                offset += 4

                data = self.data[offset:offset + iph['data_length']]
                offset += iph['data_length']
                self.all.append(Item(data, 'IEEE-1384 Transaction', **attrs))
