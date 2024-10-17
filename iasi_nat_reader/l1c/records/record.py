"""
Piasi-reader: a library to read and convert the native IASI L1C files
Copyright (C) 2015  Stefano Piani

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 3.0 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA


Modifications made by ronglian zhou <961836102@qq.com> on <2024/10/17>:
- Moved the Record class from native_file.py to here.
- Refactored Record class and separated out the base attributes and functions
  to BaseRecord class in the record.py, generic package.
"""

from typing import IO

from ...generic.record import BaseRecord
from ...generic.record_content import interpreted_content, uninterpreted_content
from ...generic.grh import GRH
from ...generic.mphr import MPHR
from .giadr import GIADR_quality, GIADR_scale_factors


class Record(BaseRecord):
    def __init__(self, grh: GRH, content: interpreted_content | uninterpreted_content):
        super().__init__(grh, content)

    @classmethod
    def read(cls: 'Record', f: IO) -> 'Record':
        """
        Create a Record object starting from a file descriptor. If the
        record does not require other informations, it will also be
        interpreted (for example for the mphr record). Otherwise, it
        will be returned as not interpreted (this is expecially true for
        the mdr records which require a GIADR scalefactor record)

        Args:
            -*f*: A file descriptor

        Returns:
            A Record object
        """
        grh = GRH.read(f)
        if grh.record_class == 'MPHR':
            content = MPHR.read(f, grh)
        elif grh.record_class == 'GIADR':
            assert grh.record_subclass in (0, 1), f'subclass of GIADR({grh.record_subclass}) is different from 0,1'
            if grh.record_subclass == 0:
                content = GIADR_quality.read(f, grh)
            elif grh.record_subclass == 1:
                content = GIADR_scale_factors.read(f, grh)
            else:
                data = f.read(grh.record_size - GRH.size)
                content = uninterpreted_content(data)
        else:
            data = f.read(grh.record_size - GRH.size)
            content = uninterpreted_content(data)
        return cls(grh, content)
