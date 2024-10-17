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
- Refactored classes.
"""

from typing import IO
from numpy import fromstring

from ...generic.record_content import interpreted_content
from ...generic.grh import GRH
from ...generic.read import generic_read, b, i2, i4, vi4
from ...generic.parameters import *


class GIADR_quality(interpreted_content):
    def __init__(self) -> None:
        self.__raw = None
        self.IDefPsfSondNbLin = None
        self.IDefPsfSondNbCol = None
        self.IDefPsfSondOverSampFactor = None
        self.IDefPsfSondY = None
        self.IDefPsfSondZ = None
        self.IDefPsfSondWgt = None
        self.IDefllSSrfNsfirst = None
        self.IDefllSSrfNslast = None
        self.IDefllSSrf = None
        self.IDefllSSrfDWn = None
        self.IDefIISNeDT = None
        self.IDefDptIISDeadPix = None

    @property
    def raw(self):
        return self.__raw

    @staticmethod
    def read(f: IO, grh: GRH):
        giadr = GIADR_quality()

        raw_data = f.read(grh.record_size - GRH.size)
        giadr.__raw = raw_data

        _grh_offset = 20
        offset = 0

        shape = (PN,)
        dtype = i4
        scale = None
        giadr.IDefPsfSondNbLin, offset = generic_read(raw_data, offset, shape, dtype, scale)
        assert offset + _grh_offset == 36

        shape = (PN,)
        dtype = i4
        scale = None
        giadr.IDefPsfSondNbCol, offset = generic_read(raw_data, offset, shape, dtype, scale)
        assert offset + _grh_offset == 52

        shape = (1,)
        dtype = vi4
        scale = None
        giadr.IDefPsfSondOverSampFactor, offset = generic_read(raw_data, offset, shape, dtype, scale)
        assert offset + _grh_offset == 57

        shape = (PN, 100)
        dtype = i4
        scale = 6
        giadr.IDefPsfSondY, offset = generic_read(raw_data, offset, shape, dtype, scale)
        assert offset + _grh_offset == 1657

        shape = (PN, 100)
        dtype = i4
        scale = 6
        giadr.IDefPsfSondZ, offset = generic_read(raw_data, offset, shape, dtype, scale)
        assert offset + _grh_offset == 3257

        shape = (PN, 100, 100)
        dtype = vi4
        scale = None
        giadr.IDefPsfSondWgt, offset = generic_read(raw_data, offset, shape, dtype, scale)
        assert offset + _grh_offset == 203257

        shape = (1,)
        dtype = i4
        scale = None
        giadr.IDefllSSrfNsfirst, offset = generic_read(raw_data, offset, shape, dtype, scale)
        assert offset + _grh_offset == 203261

        shape = (1,)
        dtype = i4
        scale = None
        giadr.IDefllSSrfNslast, offset = generic_read(raw_data, offset, shape, dtype, scale)
        assert offset + _grh_offset == 203265

        shape = (100,)
        dtype = vi4
        scale = None
        giadr.IDefllSSrf, offset = generic_read(raw_data, offset, shape, dtype, scale)
        assert offset + _grh_offset == 203765

        shape = (1,)
        dtype = vi4
        scale = None
        giadr.IDefllSSrfDWn, offset = generic_read(raw_data, offset, shape, dtype, scale)
        assert offset + _grh_offset == 203770

        shape = (IMLI, IMCO)
        dtype = vi4
        scale = None
        giadr.IDefIISNeDT, offset = generic_read(raw_data, offset, shape, dtype, scale)
        assert offset + _grh_offset == 224250

        shape = (IMLI, IMCO)
        dtype = b
        scale = None
        giadr.IDefDptIISDeadPix, offset = generic_read(raw_data, offset, shape, dtype, scale)
        assert offset + _grh_offset == 228346

        assert grh.record_size == offset + GRH.size
        return giadr

    def __str__(self):
        output = "========== IASI GIADR QUALITY ==========\n"
        output += "IDefPsfSondNbLin = " + str(self.IDefPsfSondNbLin) + "\n"
        output += "IDefPsfSondNbCol = " + str(self.IDefPsfSondNbCol) + "\n"
        output += "IDefPsfSondOverSampFactor = " + str(self.IDefPsfSondOverSampFactor) + "\n"
        output += "IDefPsfSondY =\n" + str(self.IDefPsfSondY) + "\n"
        output += "IDefPsfSondZ =\n" + str(self.IDefPsfSondZ) + "\n"
        output += "IDefPsfSondWgt =\n" + str(self.IDefPsfSondWgt) + "\n"
        output += "IDefllSSrfNsfirst = " + str(self.IDefllSSrfNsfirst) + "\n"
        output += "IDefllSSrfNslast = " + str(self.IDefllSSrfNslast) + "\n"
        output += "IDefllSSrf =\n" + str(self.IDefllSSrf) + "\n"
        output += "IDefllSSrfDWn = " + str(self.IDefllSSrfDWn) + "\n"
        output += "IDefIISNeDT =\n" + str(self.IDefIISNeDT) + "\n"
        output += "IDefDptIISDeadPix =\n" + str(self.IDefDptIISDeadPix)
        return output


class GIADR_scale_factors(interpreted_content):
    def __init__(self) -> None:
        self.__raw = None
        self.IDefScaleSondNbScale = None
        self.IDefScaleSondNsfirst = None
        self.IDefScaleSondNslast = None
        self.IDefScaleSondScaleFactor = None
        self.IDefScaleIISScaleFactor = None

    @property
    def raw(self):
        return self.__raw

    @staticmethod
    def read(f: IO, grh: GRH):
        giadr = GIADR_scale_factors()

        raw_data = f.read(grh.record_size - GRH.size)
        giadr.__raw = raw_data

        int_data = fromstring(raw_data, dtype=i2, count=32)

        giadr.IDefScaleSondNbScale = int_data[0]
        giadr.IDefScaleSondNsfirst = int_data[1:11]
        giadr.IDefScaleSondNslast = int_data[11:21]
        giadr.IDefScaleSondScaleFactor = int_data[21:31]
        giadr.IDefScaleIISScaleFactor = int_data[31]

        assert grh.record_size == 32 * 2 + GRH.size
        return giadr

    def __str__(self):
        output = "========== IASI GIADR SCALEFACTOR ==========\n"
        output += "IDefScaleSondNbScale =      " + str(self.IDefScaleSondNbScale) + "\n"
        output += "IDefScaleSondNsfirst =     " + str(self.IDefScaleSondNsfirst) + "\n"
        output += "IDefScaleSondNslast =      " + str(self.IDefScaleSondNslast) + "\n"
        output += "IDefScaleSondScaleFactor = " + str(self.IDefScaleSondScaleFactor) + "\n"
        output += "IDefScaleIISScaleFactor =   " + str(self.IDefScaleIISScaleFactor)
        return output
