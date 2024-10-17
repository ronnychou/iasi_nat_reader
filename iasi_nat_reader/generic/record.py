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
- Separated out the base attributes and functions in Record class to BaseRecord class.
"""

from .record_content import interpreted_content, uninterpreted_content
from .grh import GRH


class BaseRecord:
    """
    The BaseRecord is the unit of information of the IASI files. Every file is composed
    by one or more records. Every record is made of two elements:
      - a grh which contains some metadata about the record
      - a content, i.e. the real data

    While in principle it is possible to create a record calling the __init__ method
    and passing a gdr object and the content, usually a record is created by the read
    method starting from a file

    Args:
        - *grh*: a GRH object
        - *content*: a record_content object
    """

    def __init__(self, grh: GRH, content: interpreted_content | uninterpreted_content):
        self.__grh = grh
        self.__content = content

    @property
    def type(self):
        """
        The type of the record as string. It could be one of the following:
          - MPHR
          - SPHR
          - IPR
          - GEADR
          - GIADR
          - VEADR
          - VIADR
          - MDR
          - MDR (bad)
        """
        return self.__grh.record_class

    @property
    def size(self):
        """
        The dimension in bytes of the record. It also includes the dimension
        of the grh
        """
        return self.__grh.record_size

    @property
    def grh(self):
        """
        The grh of the record
        """
        return self.__grh

    @property
    def content(self):
        """
        The content of the record. If the record is interpreted, it is
        an object that store all the information read; if not, it is just
        a sequence of bytes.
        """
        return self.__content

    @property
    def interpreted(self):
        """
        A boolean value that is True if the record is interpreted.
        """
        return self.content.interpreted

    @property
    def raw(self):
        return self.grh.raw + self.content.raw
