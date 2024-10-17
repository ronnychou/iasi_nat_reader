"""
iasi_nat_reader: An enhanced library to read IASI L1C, L2, and PCC files
Copyright (C) 2024 Ronglian Zhou

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


New features made by ronglian zhou <961836102@qq.com> on <2024/10/17>:
- Added support to read IASI Level 2 products
"""

from typing import IO

from ...generic.record import BaseRecord
from ...generic.record_content import uninterpreted_content
from ...generic.grh import GRH
from ...generic.mphr import MPHR
from .giadr import GIADR


class Record(BaseRecord):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def read(cls: 'Record', f: IO):
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
            if grh.record_subclass == 1:
                content = GIADR.read(f, grh)
            else:
                data = f.read(grh.record_size - GRH.size)
                content = uninterpreted_content(data)
        else:
            data = f.read(grh.record_size - GRH.size)
            content = uninterpreted_content(data)
        return cls(grh, content)
