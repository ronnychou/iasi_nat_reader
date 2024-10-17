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

from ...generic.record_content import interpreted_content
from ...generic.grh import GRH
from ...generic.read import generic_read, u1, u2, u4


class GIADR(interpreted_content):
    def __init__(self) -> None:
        self.__raw = None

        self.NLT = self.NUM_PRESSURE_LEVELS_TEMP = None
        self.PRESSURE_LEVELS_TEMP = None

        self.NLQ = self.NUM_PRESSURE_LEVELS_HUMIDITY = None
        self.PRESSURE_LEVELS_HUMIDITY = None

        self.NLO = self.NUM_PRESSURE_LEVELS_OZONE = None
        self.PRESSURE_LEVELS_OZONE = None

        self.NEW = self.NUM_SURFACE_EMISSIVITY_WAVELENGTHS = None
        self.SURFACE_EMISSIVITY_WAVELENGTHS = None

        self.NPCT = self.NUM_TEMPERATURE_PCS = None
        self.NPCW = self.NUM_WATER_VAPOUR_PCS = None
        self.NPCO = self.NUM_OZONE_PCS = None

        self.NL_CO = self.FORLI_NUM_LAYERS_CO = None
        self.FORLI_LAYER_HEIGHTS_CO = None

        self.NL_HNO3 = self.FORLI_NUM_LAYERS_HNO3 = None
        self.FORLI_LAYER_HEIGHTS_HNO3 = None

        self.NL_O3 = self.FORLI_NUM_LAYERS_O3 = None
        self.FORLI_LAYER_HEIGHTS_O3 = None

        self.NL_SO2 = self.BRESCIA_NUM_ALTITUDES_SO2 = None
        self.BRESCIA_ALTITUDES_SO2 = None

    @property
    def raw(self):
        return self.__raw

    @staticmethod
    def read(f: IO, grh: GRH):
        giadr = GIADR()

        raw_data = f.read(grh.record_size - GRH.size)
        giadr.__raw = raw_data

        _grh_offset = 20
        offset = 0

        shape = 1
        dtype = u1
        scale = None
        giadr.NUM_PRESSURE_LEVELS_TEMP, offset = generic_read(raw_data, offset, shape, dtype, scale)
        giadr.NLT = giadr.NUM_PRESSURE_LEVELS_TEMP
        assert offset + _grh_offset == 21

        shape = (giadr.NLT,)
        dtype = u4
        scale = 2 * 2  # the latter 2 changes units Pa to hPa
        giadr.PRESSURE_LEVELS_TEMP, offset = generic_read(raw_data, offset, shape, dtype, scale)
        assert offset + _grh_offset == 425

        shape = (1,)
        dtype = u1
        scale = None
        giadr.NUM_PRESSURE_LEVELS_HUMIDITY, offset = generic_read(raw_data, offset, shape, dtype, scale)
        giadr.NLQ = giadr.NUM_PRESSURE_LEVELS_HUMIDITY
        assert offset + _grh_offset == 426

        shape = (giadr.NLQ,)
        dtype = u4
        scale = 2 * 2
        giadr.PRESSURE_LEVELS_HUMIDITY, offset = generic_read(raw_data, offset, shape, dtype, scale)
        assert offset + _grh_offset == 830

        shape = (1,)
        dtype = u1
        scale = None
        giadr.NUM_PRESSURE_LEVELS_OZONE, offset = generic_read(raw_data, offset, shape, dtype, scale)
        giadr.NLO = giadr.NUM_PRESSURE_LEVELS_OZONE
        assert offset + _grh_offset == 831

        shape = (giadr.NLO,)
        dtype = u4
        scale = 2 * 2
        giadr.PRESSURE_LEVELS_OZONE, offset = generic_read(raw_data, offset, shape, dtype, scale)
        assert offset + _grh_offset == 1235

        shape = (1,)
        dtype = u1
        scale = None
        giadr.NUM_SURFACE_EMISSIVITY_WAVELENGTHS, offset = generic_read(raw_data, offset, shape, dtype, scale)
        giadr.NEW = giadr.NUM_SURFACE_EMISSIVITY_WAVELENGTHS
        assert offset + _grh_offset == 1236

        shape = (giadr.NEW,)
        dtype = u4
        scale = 2 * 2
        giadr.SURFACE_EMISSIVITY_WAVELENGTHS, offset = generic_read(raw_data, offset, shape, dtype, scale)
        assert offset + _grh_offset == 1284

        shape = (1,)
        dtype = u1
        scale = None
        giadr.NUM_TEMPERATURE_PCS, offset = generic_read(raw_data, offset, shape, dtype, scale)
        giadr.NPCT = giadr.NUM_TEMPERATURE_PCS

        assert offset + _grh_offset == 1285

        shape = (1,)
        dtype = u1
        scale = None
        giadr.NUM_WATER_VAPOUR_PCS, offset = generic_read(raw_data, offset, shape, dtype, scale)
        giadr.NPCW = giadr.NUM_WATER_VAPOUR_PCS
        assert offset + _grh_offset == 1286

        shape = (1,)
        dtype = u1
        scale = None
        giadr.NUM_OZONE_PCS, offset = generic_read(raw_data, offset, shape, dtype, scale)
        giadr.NPCO = giadr.NUM_OZONE_PCS
        assert offset + _grh_offset == 1287

        shape = (1,)
        dtype = u1
        scale = None
        giadr.FORLI_NUM_LAYERS_CO, offset = generic_read(raw_data, offset, shape, dtype, scale)
        giadr.NL_CO = giadr.FORLI_NUM_LAYERS_CO
        assert offset + _grh_offset == 1288

        shape = (giadr.NL_CO,)
        dtype = u2
        scale = None
        giadr.FORLI_LAYER_HEIGHTS_CO, offset = generic_read(raw_data, offset, shape, dtype, scale)
        assert offset + _grh_offset == 1326

        # FORLI_NUM_LAYERS_HNO3 in pfs is 19, but here is 41
        shape = (1,)
        dtype = u1
        scale = None
        giadr.FORLI_NUM_LAYERS_HNO3, offset = generic_read(raw_data, offset, shape, dtype, scale)
        giadr.NL_HNO3 = giadr.FORLI_NUM_LAYERS_HNO3
        assert offset + _grh_offset == 1327

        shape = (giadr.NL_HNO3,)
        dtype = u2
        scale = None
        giadr.FORLI_LAYER_HEIGHTS_HNO3, offset = generic_read(raw_data, offset, shape, dtype, scale)
        # assert offset+_grh_offset == 1365

        shape = (1,)
        dtype = u1
        scale = None
        giadr.FORLI_NUM_LAYERS_O3, offset = generic_read(raw_data, offset, shape, dtype, scale)
        giadr.NL_O3 = giadr.FORLI_NUM_LAYERS_O3
        # assert offset+_grh_offset == 1366

        shape = (giadr.NL_O3,)
        dtype = u2
        scale = None
        giadr.FORLI_LAYER_HEIGHTS_O3, offset = generic_read(raw_data, offset, shape, dtype, scale)
        # assert offset+_grh_offset == 1446

        shape = (1,)
        dtype = u1
        scale = None
        giadr.BRESCIA_NUM_ALTITUDES_SO2, offset = generic_read(raw_data, offset, shape, dtype, scale)
        giadr.NL_SO2 = giadr.BRESCIA_NUM_ALTITUDES_SO2
        # assert offset+_grh_offset == 1447

        shape = (giadr.NL_SO2,)
        dtype = u2
        scale = None
        giadr.BRESCIA_ALTITUDES_SO2, offset = generic_read(raw_data, offset, shape, dtype, scale)
        # assert offset+_grh_offset == 1457

        assert grh.record_size == offset + GRH.size
        return giadr

    def __str__(self):
        output = "========== IASI SND GIADR ==========\n"
        output += "NUM_PRESSURE_LEVELS_TEMP = " + str(self.NUM_PRESSURE_LEVELS_TEMP) + "\n"
        output += "PRESSURE_LEVELS_TEMP = " + str(self.PRESSURE_LEVELS_TEMP) + "\n"
        output += "NUM_PRESSURE_LEVELS_HUMIDITY = " + str(self.NUM_PRESSURE_LEVELS_HUMIDITY) + "\n"
        output += "PRESSURE_LEVELS_HUMIDITY = " + str(self.PRESSURE_LEVELS_HUMIDITY) + "\n"
        output += "NUM_PRESSURE_LEVELS_OZONE = " + str(self.NUM_PRESSURE_LEVELS_OZONE) + "\n"
        output += "PRESSURE_LEVELS_OZONE = " + str(self.PRESSURE_LEVELS_OZONE) + "\n"
        output += "NUM_SURFACE_EMISSIVITY_WAVELENGTHS = " + str(self.NUM_SURFACE_EMISSIVITY_WAVELENGTHS) + "\n"
        output += "SURFACE_EMISSIVITY_WAVELENGTHS = " + str(self.SURFACE_EMISSIVITY_WAVELENGTHS) + "\n"
        output += "NUM_TEMPERATURE_PCS = " + str(self.NUM_TEMPERATURE_PCS) + "\n"
        output += "NUM_WATER_VAPOUR_PCS = " + str(self.NUM_WATER_VAPOUR_PCS) + "\n"
        output += "NUM_OZONE_PCS = " + str(self.NUM_OZONE_PCS) + "\n"
        output += "FORLI_NUM_LAYERS_CO = " + str(self.FORLI_NUM_LAYERS_CO) + "\n"
        output += "FORLI_LAYER_HEIGHTS_CO = " + str(self.FORLI_LAYER_HEIGHTS_CO) + "\n"
        output += "FORLI_NUM_LAYERS_HNO3 = " + str(self.FORLI_NUM_LAYERS_HNO3) + "\n"
        output += "FORLI_LAYER_HEIGHTS_HNO3 = " + str(self.FORLI_LAYER_HEIGHTS_HNO3) + "\n"
        output += "FORLI_NUM_LAYERS_O3 = " + str(self.FORLI_NUM_LAYERS_O3) + "\n"
        output += "FORLI_LAYER_HEIGHTS_O3 = " + str(self.FORLI_LAYER_HEIGHTS_O3) + "\n"
        output += "BRESCIA_NUM_ALTITUDES_SO2 = " + str(self.BRESCIA_NUM_ALTITUDES_SO2) + "\n"
        output += "BRESCIA_ALTITUDES_SO2 = " + str(self.BRESCIA_ALTITUDES_SO2)
        return output
