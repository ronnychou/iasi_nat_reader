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
- Added support to read IASI PCC products
"""

from typing import IO
import numpy as np

from ...generic.record_content import interpreted_content
from ...generic.grh import GRH
from ...generic.parameters import *
from ...generic.read import generic_read, u2

# giadr\.(\w+) = giadr\.(.(\w+)), offset = generic_read\(raw_data, offset, shape, dtype, scale\)
# giadr.$2, offset = generic_read(raw_data, offset, shape, dtype, scale)\n        giadr.$1 = giadr.$2


class GIADR(interpreted_content):
    def __init__(self):
        self.__raw: bytes
        self.NBS1P1 = self.NbrScoresBand1_Part1 = None
        self.NBS1P2 = self.NbrScoresBand1_Part2 = None
        self.NBS1P3 = self.NbrScoresBand1_Part3 = None
        self.NBS2P1 = self.NbrScoresBand2_Part1 = None
        self.NBS2P2 = self.NbrScoresBand2_Part2 = None
        self.NBS2P3 = self.NbrScoresBand2_Part3 = None
        self.NBS3P1 = self.NbrScoresBand3_Part1 = None
        self.NBS3P2 = self.NbrScoresBand3_Part2 = None
        self.NBS3P3 = self.NbrScoresBand3_Part3 = None
        self.FirstChannel: np.ndarray
        self.NbrChannels: np.ndarray
        self.ScoreQuantisationFactor: np.ndarray
        self.ResidualQuantisationFactor: np.ndarray

        # for prop in self.properties:
        # setattr(self, prop, None)
        # delattr(type(self), prop)

    @property
    def raw(self):
        return self.__raw

    @staticmethod
    def read(f: IO, grh: GRH):
        giadr = GIADR()

        raw_data = f.read(grh.record_size - GRH.size)
        giadr.__raw = raw_data

        offset = 0

        # NBSxP1 Number of PC scores, band x, 4 bytes
        # NBSxP2 Number of PC scores, band x, 2 bytes
        # NBSxP3 Number of PC scores, band x, 1 bytes

        shape = (1,)
        dtype = u2
        scale = None
        giadr.NbrScoresBand1_Part1, offset = generic_read(raw_data, offset, shape, dtype, scale)
        giadr.NBS1P1 = giadr.NbrScoresBand1_Part1
        # assert offset+_grh_offset == 22

        shape = (1,)
        dtype = u2
        scale = None
        giadr.NbrScoresBand1_Part2, offset = generic_read(raw_data, offset, shape, dtype, scale)
        giadr.NBS1P2 = giadr.NbrScoresBand1_Part2
        # assert offset+_grh_offset == 24

        shape = (1,)
        dtype = u2
        scale = None
        giadr.NbrScoresBand1_Part3, offset = generic_read(raw_data, offset, shape, dtype, scale)
        giadr.NBS1P3 = giadr.NbrScoresBand1_Part3
        # assert offset+_grh_offset == 26

        shape = (1,)
        dtype = u2
        scale = None
        giadr.NbrScoresBand2_Part1, offset = generic_read(raw_data, offset, shape, dtype, scale)
        giadr.NBS2P1 = giadr.NbrScoresBand2_Part1
        # assert offset+_grh_offset == 28

        shape = (1,)
        dtype = u2
        scale = None
        giadr.NbrScoresBand2_Part2, offset = generic_read(raw_data, offset, shape, dtype, scale)
        giadr.NBS2P2 = giadr.NbrScoresBand2_Part2
        # assert offset+_grh_offset == 30

        shape = (1,)
        dtype = u2
        scale = None
        giadr.NbrScoresBand2_Part3, offset = generic_read(raw_data, offset, shape, dtype, scale)
        giadr.NBS2P3 = giadr.NbrScoresBand2_Part3
        # assert offset+_grh_offset == 32

        shape = (1,)
        dtype = u2
        scale = None
        giadr.NbrScoresBand3_Part1, offset = generic_read(raw_data, offset, shape, dtype, scale)
        giadr.NBS3P1 = giadr.NbrScoresBand3_Part1
        # assert offset+_grh_offset == 34

        shape = (1,)
        dtype = u2
        scale = None
        giadr.NbrScoresBand3_Part2, offset = generic_read(raw_data, offset, shape, dtype, scale)
        giadr.NBS3P2 = giadr.NbrScoresBand3_Part2
        # assert offset+_grh_offset == 36

        shape = (1,)
        dtype = u2
        scale = None
        giadr.NbrScoresBand3_Part3, offset = generic_read(raw_data, offset, shape, dtype, scale)
        giadr.NBS3P3 = giadr.NbrScoresBand3_Part3
        # assert offset+_grh_offset == 38

        shape = (SB,)
        dtype = u2
        scale = None
        giadr.FirstChannel, offset = generic_read(raw_data, offset, shape, dtype, scale)
        giadr.FirstChannel = giadr.FirstChannel.squeeze()
        giadr.FirstChannel = giadr.FirstChannel - 1  # change to python index convention
        # assert offset+_grh_offset == 44

        shape = (SB,)
        dtype = u2
        scale = None
        giadr.NbrChannels, offset = generic_read(raw_data, offset, shape, dtype, scale)
        giadr.NbrChannels = giadr.NbrChannels.squeeze()
        # assert offset+_grh_offset == 50

        shape = (SB,)
        dtype = u2
        scale = 2
        giadr.ScoreQuantisationFactor, offset = generic_read(raw_data, offset, shape, dtype, scale)
        giadr.ScoreQuantisationFactor = giadr.ScoreQuantisationFactor.squeeze()
        # assert offset+_grh_offset == 56

        shape = (SB,)
        dtype = u2
        scale = 2
        giadr.ResidualQuantisationFactor, offset = generic_read(raw_data, offset, shape, dtype, scale)
        giadr.ResidualQuantisationFactor = giadr.ResidualQuantisationFactor.squeeze()
        # assert offset+_grh_offset == 62

        assert grh.record_size == offset + GRH.size

        return giadr

    def __str__(self):
        output = "========== IASI PC GIADR ==========\n"
        output += "NbrScoresBand1_Part1 = " + str(self.NbrScoresBand1_Part1) + "\n"
        output += "NbrScoresBand1_Part2 = " + str(self.NbrScoresBand1_Part2) + "\n"
        output += "NbrScoresBand1_Part3 = " + str(self.NbrScoresBand1_Part3) + "\n"
        output += "NbrScoresBand2_Part1 = " + str(self.NbrScoresBand2_Part1) + "\n"
        output += "NbrScoresBand2_Part2 = " + str(self.NbrScoresBand2_Part2) + "\n"
        output += "NbrScoresBand2_Part3 = " + str(self.NbrScoresBand2_Part3) + "\n"
        output += "NbrScoresBand3_Part1 = " + str(self.NbrScoresBand3_Part1) + "\n"
        output += "NbrScoresBand3_Part2 = " + str(self.NbrScoresBand3_Part2) + "\n"
        output += "NbrScoresBand3_Part3 = " + str(self.NbrScoresBand3_Part3) + "\n"
        output += "FirstChannel = " + str(self.FirstChannel) + "\n"
        output += "NbrChannels = " + str(self.NbrChannels) + "\n"
        output += "ScoreQuantisationFactor = " + str(self.ScoreQuantisationFactor) + "\n"
        output += "ResidualQuantisationFactor = " + str(self.ResidualQuantisationFactor)
        return output
