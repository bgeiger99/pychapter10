
from array import array
import struct

import datatypes


class Packet(object):
    """Reads header and associates a data type specific object."""

    # The attribute names for header fields.
    HEADER_KEYS = (
        'Sync Pattern',
        'Channel ID',
        'Packet Length',
        'Data Length',
        'Header Version',
        'Sequence Number',
        'Flags',
        'Data Type',
        'RTC Low',
        'RTC High',
        'Header Checksum'
    )

    def __init__(self, file):
        """Takes an open file object with its cursor at this packet."""

        # Mark our location in the file and read the header.
        self.file, self.pos = file, file.tell()
        header = file.read(24)

        if len(header) < 24:
            raise EOFError

        # Store the header sums (masked to be a consistent bit length).
        self.header_sums = sum(array('H', header)[:-1]) & 0xffff

        # Parse the header values.
        values = struct.unpack('HHIIBBBBIHH', header)
        for i, field in enumerate(self.HEADER_KEYS):
            setattr(self, '_'.join(field.split()).lower(), values[i])

        # Read the secondary header (if any).
        self.time = None
        self.secondary_sums, self.secondary_checksum = (None, None)
        if self.flags & (1 << 7):
            secondary = file.read(12)
            if len(secondary) < 12:
                raise EOFError

            # Store our sums for checking later on (masked for bit length).
            self.secondary_sums = sum(array('H', secondary)[:-1]) & 0xffff

            self.time, self.secondary_checksum = struct.unpack('qxxH',
                                                               secondary)

        # Parse the body based on type.
        datatype = datatypes.get_handler(self.data_type)
        self.body = datatype(self)

    def print_header(self):
        """Print out the header information."""

        print '-' * 80
        for name in self.HEADER_KEYS:
            attr = '_'.join(name.split()).lower()
            print name + str(getattr(self, attr)).rjust(80 - len(name), '.')
        print self.check() and '(valid)' or '(error)'
        print '-' * 80

    def raw(self):
        """Returns the entire packet as raw bytes."""

        pos = self.file.tell()
        self.file.seek(self.pos)
        raw = self.file.read(self.packet_length)
        self.file.seek(pos)

        return raw

    def check(self):
        """Validate the packet using checksums and verifying fields."""

        if self.header_sums != self.header_checksum:
            return False
        elif self.secondary_sums != self.secondary_checksum:
            return False
        elif self.sync_pattern != 0xeb25:
            return False
        return True

    def __len__(self):
        return self.packet_length
