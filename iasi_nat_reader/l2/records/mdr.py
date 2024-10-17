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

import io, cProfile, pstats
import numpy as np

from ...generic.record_content import interpreted_content
from ...generic.read import generic_read, b, i2, i4, u1, u2, u4
from .record import Record
from .giadr import GIADR

debug = False


class MDR(interpreted_content):
    def __init__(self) -> None:
        self.DEGRADED_INST_MDR = None
        self.DEGRADED_PROC_MDR = None
        self.FG_ATMOSPHERIC_TEMPERATURE = None
        self.FG_ATMOSPHERIC_WATER_VAPOUR = None
        self.FG_ATMOSPHERIC_OZONE = None
        self.FG_SURFACE_TEMPERATURE = None
        self.FG_QI_ATMOSPHERIC_TEMPERATURE = None
        self.FG_QI_ATMOSPHERIC_WATER_VAPOUR = None
        self.FG_QI_ATMOSPHERIC_OZONE = None
        self.FG_QI_SURFACE_TEMPERATURE = None
        self.ATMOSPHERIC_TEMPERATURE = None
        self.ATMOSPHERIC_WATER_VAPOUR = None
        self.ATMOSPHERIC_OZONE = None
        self.SURFACE_TEMPERATURE = None
        self.INTEGRATED_WATER_VAPOUR = None
        self.INTEGRATED_OZONE = None
        self.INTEGRATED_N2O = None
        self.INTEGRATED_CO = None
        self.INTEGRATED_CH4 = None
        self.INTEGRATED_CO2 = None
        self.SURFACE_EMISSIVITY = None
        self.NUMBER_CLOUD_FORMATIONS = None
        self.FRACTIONAL_CLOUD_COVER = None
        self.CLOUD_TOP_TEMPERATURE = None
        self.CLOUD_TOP_PRESSURE = None
        self.CLOUD_PHASE = None
        self.SURFACE_PRESSURE = None
        self.INSTRUMENT_MODE = None
        self.SPACECRAFT_ALTITUDE = None
        self.ANGULAR_RELATION = None
        self.EARTH_LOCATION = None
        self.FLG_AMSUBAD = None
        self.FLG_AVHRRBAD = None
        self.FLG_CLDFRM = None
        self.FLG_CLDNES = None
        self.FLG_CLDTST = None
        self.FLG_DAYNIT = None
        self.FLG_DUSTCLD = None
        self.FLG_FGCHECK = None
        self.FLG_IASIBAD = None
        self.FLG_INITIA = None
        self.FLG_ITCONV = None
        self.FLG_LANSEA = None
        self.FLG_MHSBAD = None
        self.FLG_NUMIT = None
        self.FLG_NWPBAD = None
        self.FLG_PHYSCHECK = None
        self.FLG_RETCHECK = None
        self.FLG_SATMAN = None
        self.FLG_SUNGLNT = None
        self.FLG_THICIR = None
        self.NERR = None
        self.ERROR_DATA_INDEX = None
        self.TEMPERATURE_ERROR = None
        self.WATER_VAPOUR_ERROR = None
        self.OZONE_ERROR = None
        self.SURFACE_Z = None

    @staticmethod
    def read(record: Record, giadr: GIADR):
        if debug:
            profile = cProfile.Profile()
            profile.enable()

        raw_data: bytes = record.content

        mdr = MDR()

        NLT = giadr.NLT
        NLQ = giadr.NLQ
        NLO = giadr.NLO
        NEW = giadr.NEW
        NPCT = giadr.NPCT
        NPCW = giadr.NPCW
        NPCO = giadr.NPCO
        NL_CO = giadr.NL_CO
        NL_HNO3 = giadr.NL_HNO3
        NL_O3 = giadr.NL_O3
        NL_SO2 = giadr.NL_SO2

        NEVA_CO = round(NL_CO / 2)
        NEVE_CO = NEVA_CO * NL_CO
        NEVA_HNO3 = round(NL_HNO3 / 2)
        NEVE_HNO3 = NEVA_HNO3 * NL_HNO3
        NEVA_O3 = round(NL_O3 / 2)
        NEVE_O3 = NEVA_O3 * NL_O3

        NERRT = int(NPCT * (NPCT + 1) / 2)
        NERRW = int(NPCW * (NPCW + 1) / 2)
        NERRO = int(NPCO * (NPCO + 1) / 2)

        _grh_offset = 20
        offset = 0

        shape = (1,)
        dtype = b
        scale = None
        mdr.DEGRADED_INST_MDR, offset = generic_read(raw_data, offset, shape, dtype, scale)
        # assert offset+_grh_offset == 21

        shape = (1,)
        dtype = b
        scale = None
        mdr.DEGRADED_PROC_MDR, offset = generic_read(raw_data, offset, shape, dtype, scale)
        # assert offset+_grh_offset == 22

        shape = (120, NLT)
        dtype = u2
        scale = 2
        mdr.FG_ATMOSPHERIC_TEMPERATURE, offset = generic_read(raw_data, offset, shape, dtype, scale)
        # assert offset+_grh_offset == 24262

        shape = (120, NLQ)
        dtype = u4
        scale = 7
        mdr.FG_ATMOSPHERIC_WATER_VAPOUR, offset = generic_read(raw_data, offset, shape, dtype, scale)
        # assert offset+_grh_offset == 72742

        shape = (120, NLO)
        dtype = u2
        scale = 8
        mdr.FG_ATMOSPHERIC_OZONE, offset = generic_read(raw_data, offset, shape, dtype, scale)
        # assert offset+_grh_offset == 96982

        shape = (120,)
        dtype = u2
        scale = 2
        mdr.FG_SURFACE_TEMPERATURE, offset = generic_read(raw_data, offset, shape, dtype, scale)
        # assert offset+_grh_offset == 97222

        shape = (120,)
        dtype = u1
        scale = 1
        mdr.FG_QI_ATMOSPHERIC_TEMPERATURE, offset = generic_read(raw_data, offset, shape, dtype, scale)
        # assert offset+_grh_offset == 97342

        shape = (120,)
        dtype = u1
        scale = 1
        mdr.FG_QI_ATMOSPHERIC_WATER_VAPOUR, offset = generic_read(raw_data, offset, shape, dtype, scale)
        # assert offset+_grh_offset == 97462

        shape = (120,)
        dtype = u1
        scale = 1
        mdr.FG_QI_ATMOSPHERIC_OZONE, offset = generic_read(raw_data, offset, shape, dtype, scale)
        # assert offset+_grh_offset == 97582

        shape = (120,)
        dtype = u1
        scale = 1
        mdr.FG_QI_SURFACE_TEMPERATURE, offset = generic_read(raw_data, offset, shape, dtype, scale)
        # assert offset+_grh_offset == 97702

        shape = (120, NLT)
        dtype = u2
        scale = 2
        mdr.ATMOSPHERIC_TEMPERATURE, offset = generic_read(raw_data, offset, shape, dtype, scale)
        # assert offset+_grh_offset == 121942

        shape = (120, NLQ)
        dtype = u4
        scale = 7
        mdr.ATMOSPHERIC_WATER_VAPOUR, offset = generic_read(raw_data, offset, shape, dtype, scale)
        # assert offset+_grh_offset == 170422

        shape = (120, NLO)
        dtype = u2
        scale = 8
        mdr.ATMOSPHERIC_OZONE, offset = generic_read(raw_data, offset, shape, dtype, scale)
        # assert offset+_grh_offset == 194662

        shape = (120,)
        dtype = u2
        scale = 2
        mdr.SURFACE_TEMPERATURE, offset = generic_read(raw_data, offset, shape, dtype, scale)
        # assert offset+_grh_offset == 194902

        shape = (120,)
        dtype = u2
        scale = 2
        mdr.INTEGRATED_WATER_VAPOUR, offset = generic_read(raw_data, offset, shape, dtype, scale)
        # assert offset+_grh_offset == 195142

        shape = (120,)
        dtype = u2
        scale = 6
        mdr.INTEGRATED_OZONE, offset = generic_read(raw_data, offset, shape, dtype, scale)
        # assert offset+_grh_offset == 195382

        shape = (120,)
        dtype = u2
        scale = 6
        mdr.INTEGRATED_N2O, offset = generic_read(raw_data, offset, shape, dtype, scale)
        # assert offset+_grh_offset == 195622

        shape = (120,)
        dtype = u2
        scale = 7
        mdr.INTEGRATED_CO, offset = generic_read(raw_data, offset, shape, dtype, scale)
        # assert offset+_grh_offset == 195862

        shape = (120,)
        dtype = u2
        scale = 6
        mdr.INTEGRATED_CH4, offset = generic_read(raw_data, offset, shape, dtype, scale)
        # assert offset+_grh_offset == 196102

        shape = (120,)
        dtype = u2
        scale = 3
        mdr.INTEGRATED_CO2, offset = generic_read(raw_data, offset, shape, dtype, scale)
        # assert offset+_grh_offset == 196342

        shape = (120, NEW)
        dtype = u2
        scale = 4
        mdr.SURFACE_EMISSIVITY, offset = generic_read(raw_data, offset, shape, dtype, scale)
        # assert offset+_grh_offset == 199222

        shape = (120,)
        dtype = u1
        scale = None
        mdr.NUMBER_CLOUD_FORMATIONS, offset = generic_read(raw_data, offset, shape, dtype, scale)
        # assert offset+_grh_offset == 199342

        shape = (120, 3)
        dtype = u2
        scale = 2
        mdr.FRACTIONAL_CLOUD_COVER, offset = generic_read(raw_data, offset, shape, dtype, scale)
        # assert offset+_grh_offset == 200062

        shape = (120, 3)
        dtype = u2
        scale = 2
        mdr.CLOUD_TOP_TEMPERATURE, offset = generic_read(raw_data, offset, shape, dtype, scale)
        # assert offset+_grh_offset == 200782

        shape = (120, 3)
        dtype = u4
        scale = 2  # change Pa to hPa
        mdr.CLOUD_TOP_PRESSURE, offset = generic_read(raw_data, offset, shape, dtype, scale)
        # assert offset+_grh_offset == 202222

        shape = (120, 3)
        dtype = u1
        scale = None
        mdr.CLOUD_PHASE, offset = generic_read(raw_data, offset, shape, dtype, scale)
        # assert offset+_grh_offset == 202582

        shape = (120,)
        dtype = u4
        scale = 2  # change Pa to hPa
        mdr.SURFACE_PRESSURE, offset = generic_read(raw_data, offset, shape, dtype, scale)
        # assert offset+_grh_offset == 203062

        shape = (1,)
        dtype = u1
        scale = None
        mdr.INSTRUMENT_MODE, offset = generic_read(raw_data, offset, shape, dtype, scale)
        # assert offset+_grh_offset == 203063

        shape = (1,)
        dtype = u4
        scale = 1
        mdr.SPACECRAFT_ALTITUDE, offset = generic_read(raw_data, offset, shape, dtype, scale)
        # assert offset+_grh_offset == 203067

        shape = (120, 4)
        dtype = i2
        scale = 2
        mdr.ANGULAR_RELATION, offset = generic_read(raw_data, offset, shape, dtype, scale)
        # assert offset+_grh_offset == 204027

        shape = (120, 2)
        dtype = i4
        scale = 4
        mdr.EARTH_LOCATION, offset = generic_read(raw_data, offset, shape, dtype, scale)
        # assert offset+_grh_offset == 204987

        shape = (120,)
        dtype = u1
        scale = None
        mdr.FLG_AMSUBAD, offset = generic_read(raw_data, offset, shape, dtype, scale)
        # assert offset+_grh_offset == 205107

        shape = (120,)
        mdr.FLG_AVHRRBAD, offset = generic_read(raw_data, offset, shape, dtype, scale)
        dtype = u1
        # assert offset+_grh_offset == 205227

        shape = (120,)
        dtype = u1
        scale = None
        mdr.FLG_CLDFRM, offset = generic_read(raw_data, offset, shape, dtype, scale)
        # assert offset+_grh_offset == 205347

        shape = (120,)
        dtype = u1
        scale = None
        mdr.FLG_CLDNES, offset = generic_read(raw_data, offset, shape, dtype, scale)
        # assert offset+_grh_offset == 205467

        shape = (120,)
        dtype = u2
        scale = None
        mdr.FLG_CLDTST, offset = generic_read(raw_data, offset, shape, dtype, scale)
        # assert offset+_grh_offset == 205707

        shape = (120,)
        dtype = u1
        scale = None
        mdr.FLG_DAYNIT, offset = generic_read(raw_data, offset, shape, dtype, scale)
        # assert offset+_grh_offset == 205827

        shape = (120,)
        dtype = u1
        scale = 1
        mdr.FLG_DUSTCLD, offset = generic_read(raw_data, offset, shape, dtype, scale)
        # assert offset+_grh_offset == 205947

        shape = (120,)
        dtype = u2
        scale = None
        mdr.FLG_FGCHECK, offset = generic_read(raw_data, offset, shape, dtype, scale)
        # assert offset+_grh_offset == 206187

        shape = (120,)
        dtype = u1
        scale = None
        mdr.FLG_IASIBAD, offset = generic_read(raw_data, offset, shape, dtype, scale)
        # assert offset+_grh_offset == 206307

        shape = (120,)
        dtype = u1
        scale = None
        mdr.FLG_INITIA, offset = generic_read(raw_data, offset, shape, dtype, scale)
        # assert offset+_grh_offset == 206427

        shape = (120,)
        dtype = u1
        scale = None
        mdr.FLG_ITCONV, offset = generic_read(raw_data, offset, shape, dtype, scale)
        # assert offset+_grh_offset == 206547

        shape = (120,)
        dtype = u1
        scale = None
        mdr.FLG_LANSEA, offset = generic_read(raw_data, offset, shape, dtype, scale)
        # assert offset+_grh_offset == 206667

        shape = (120,)
        dtype = u1
        scale = None
        mdr.FLG_MHSBAD, offset = generic_read(raw_data, offset, shape, dtype, scale)
        # assert offset+_grh_offset == 206787

        shape = (120,)
        dtype = u1
        scale = None
        mdr.FLG_NUMIT, offset = generic_read(raw_data, offset, shape, dtype, scale)
        # assert offset+_grh_offset == 206907

        shape = (120,)
        dtype = u1
        scale = None
        mdr.FLG_NWPBAD, offset = generic_read(raw_data, offset, shape, dtype, scale)
        # assert offset+_grh_offset == 207027

        shape = (120,)
        dtype = u1
        scale = None
        mdr.FLG_PHYSCHECK, offset = generic_read(raw_data, offset, shape, dtype, scale)
        # assert offset+_grh_offset == 207147

        shape = (120,)
        dtype = u2
        scale = None
        mdr.FLG_RETCHECK, offset = generic_read(raw_data, offset, shape, dtype, scale)
        # assert offset+_grh_offset == 207387

        shape = (120,)
        dtype = u1
        scale = None
        mdr.FLG_SATMAN, offset = generic_read(raw_data, offset, shape, dtype, scale)
        # assert offset+_grh_offset == 207507

        shape = (120,)
        dtype = u1
        scale = None
        mdr.FLG_SUNGLNT, offset = generic_read(raw_data, offset, shape, dtype, scale)
        # assert offset+_grh_offset == 207627

        shape = (120,)
        dtype = u1
        scale = None
        mdr.FLG_THICIR, offset = generic_read(raw_data, offset, shape, dtype, scale)
        # assert offset+_grh_offset == 207747

        shape = (1,)
        dtype = u1
        scale = None
        mdr.NERR, offset = generic_read(raw_data, offset, shape, dtype, scale)
        NERR = mdr.NERR
        # assert offset+_grh_offset == 207748

        shape = (120,)
        dtype = u1
        scale = None
        mdr.ERROR_DATA_INDEX, offset = generic_read(raw_data, offset, shape, dtype, scale)
        # assert offset+_grh_offset == 207868

        shape = (NERR, NERRT)
        dtype = u4
        scale = None
        mdr.TEMPERATURE_ERROR, offset = generic_read(raw_data, offset, shape, dtype, scale)
        # assert offset+_grh_offset == 306268

        shape = (NERR, NERRW)
        dtype = u4
        scale = None
        mdr.WATER_VAPOUR_ERROR, offset = generic_read(raw_data, offset, shape, dtype, scale)
        # assert offset+_grh_offset == 331468

        shape = (NERR, NERRO)
        dtype = u4
        scale = None
        mdr.OZONE_ERROR, offset = generic_read(raw_data, offset, shape, dtype, scale)
        # assert offset+_grh_offset == 340828

        shape = (120,)
        dtype = i2
        scale = None
        mdr.SURFACE_Z, offset = generic_read(raw_data, offset, shape, dtype, scale)
        # assert offset+_grh_offset == 341068

        if debug:
            profile.disable()
            s = io.StringIO()
            ps = pstats.Stats(profile, stream=s).sort_stats('cumulative')
            ps.print_stats()
            print(s.getvalue())

        return mdr

        shape = (120,)
        dtype = u1
        scale = None
        mdr.CO_QFLAG, offset = generic_read(raw_data, offset, shape, dtype, scale)
        # assert offset+_grh_offset == 341188

        shape = (120,)
        dtype = u4
        scale = None
        mdr.CO_BDIV, offset = generic_read(raw_data, offset, shape, dtype, scale)
        # assert offset+_grh_offset == 341668

        shape = (120,)
        dtype = u1
        scale = None
        mdr.CO_NPCA, offset = generic_read(raw_data, offset, shape, dtype, scale)
        # assert offset+_grh_offset == 341788

        shape = (120,)
        dtype = u1
        scale = None
        mdr.CO_NFITLAYERS, offset = generic_read(raw_data, offset, shape, dtype, scale)
        # assert offset+_grh_offset == 341908

        shape = (1,)
        dtype = u1
        scale = None
        mdr.CO_NBR, offset = generic_read(raw_data, offset, shape, dtype, scale)
        CO_NBR = mdr.CO_NBR
        # assert offset+_grh_offset == 341909

        shape = (CO_NBR, NL_CO)
        dtype = u2
        scale = -20
        mdr.CO_CP_AIR, offset = generic_read(raw_data, offset, shape, dtype, scale)
        # assert offset+_grh_offset == 343809

        shape = (CO_NBR, NL_CO)
        dtype = u2
        scale = -13
        mdr.CO_CP_CO_A, offset = generic_read(raw_data, offset, shape, dtype, scale)
        # assert offset+_grh_offset == 345709

        shape = (CO_NBR, NL_CO)
        itemsize = 3
        offset += np.prod(shape) * itemsize
        # mdr.CO_X_CO, offset = generic_read(raw_data, offset, shape, dtype, scale)
        # assert offset+_grh_offset == 348559

        shape = (CO_NBR, NEVA_CO)
        itemsize = 5
        offset += np.prod(shape) * itemsize
        # mdr.CO_H_EIGENVALUES, offset = generic_read(raw_data, offset, shape, dtype, scale)
        # assert offset+_grh_offset == 351059

        shape = (CO_NBR, NEVE_CO)
        itemsize = 5
        scale = None
        offset += np.prod(shape) * itemsize
        # mdr.CO_H_EIGENVECTORS, offset = generic_read(raw_data, offset, shape, dtype, scale)
        # assert offset+_grh_offset == 421059

        shape = (120,)
        dtype = u1
        scale = None
        mdr.HNO3_QFLAG, offset = generic_read(raw_data, offset, shape, dtype, scale)
        # assert offset+_grh_offset == 421179

        shape = (120,)
        dtype = u4
        scale = None
        mdr.HNO3_BDIV, offset = generic_read(raw_data, offset, shape, dtype, scale)
        # assert offset+_grh_offset == 421659

        shape = (120,)
        dtype = u1
        scale = None
        mdr.HNO3_NPCA, offset = generic_read(raw_data, offset, shape, dtype, scale)
        # assert offset+_grh_offset == 421779

        shape = (120,)
        dtype = u1
        scale = None
        mdr.HNO3_NFITLAYERS, offset = generic_read(raw_data, offset, shape, dtype, scale)
        # assert offset+_grh_offset == 421899

        shape = (1,)
        dtype = u1
        scale = None
        mdr.HNO3_NBR, offset = generic_read(raw_data, offset, shape, dtype, scale)
        HNO3_NBR = mdr.HNO3_NBR
        # assert offset+_grh_offset == 421900

        shape = (HNO3_NBR, NL_HNO3)
        dtype = u2
        itemsize = 2
        # scale = -20
        # mdr.HNO3_CP_AIR, offset = generic_read(raw_data, offset, shape, dtype, scale)
        offset += np.prod(shape) * itemsize

        shape = (HNO3_NBR, NL_HNO3)
        dtype = u2
        itemsize = 2
        # scale = -11
        # mdr.HNO3_CP_HNO3_A, offset = generic_read(raw_data, offset, shape, dtype, scale)
        offset += np.prod(shape) * itemsize

        shape = (HNO3_NBR, NL_HNO3)
        # dtype = vu2
        itemsize = 3
        # mdr.HNO3_X_HNO3, offset = generic_read(raw_data, offset, shape, dtype, scale)
        offset += np.prod(shape) * itemsize

        shape = (HNO3_NBR, NEVA_HNO3)
        itemsize = 5
        # dtype = vi4
        # mdr.HNO3_H_EIGENVALUES, offset = generic_read(raw_data, offset, shape, dtype, scale)
        offset += np.prod(shape) * itemsize

        shape = (HNO3_NBR, NEVE_HNO3)
        itemsize = 5
        # dtype = vi4
        # mdr.HNO3_H_EIGENVECTORS, offset = generic_read(raw_data, offset, shape, dtype, scale)
        offset += np.prod(shape) * itemsize

        shape = (120,)
        dtype = u1
        scale = None
        mdr.O3_QFLAG, offset = generic_read(raw_data, offset, shape, dtype, scale)
        # assert offset+_grh_offset == 422020

        shape = (120,)
        dtype = u4
        scale = None
        mdr.O3_BDIV, offset = generic_read(raw_data, offset, shape, dtype, scale)
        # assert offset+_grh_offset == 422500

        shape = (120,)
        dtype = u1
        scale = None
        mdr.O3_NPCA, offset = generic_read(raw_data, offset, shape, dtype, scale)
        # assert offset+_grh_offset == 422620

        shape = (120,)
        dtype = u1
        scale = None
        mdr.O3_NFITLAYERS, offset = generic_read(raw_data, offset, shape, dtype, scale)
        # assert offset+_grh_offset == 422740

        shape = (1,)
        dtype = u1
        scale = None
        mdr.O3_NBR, offset = generic_read(raw_data, offset, shape, dtype, scale)
        O3_NBR = mdr.O3_NBR
        # assert offset+_grh_offset == 422741

        shape = (O3_NBR, NL_O3)
        dtype = u2
        itemsize = 2
        # scale = -20
        # mdr.O3_CP_AIR, offset = generic_read(raw_data, offset, shape, dtype, scale)
        offset += np.prod(shape) * itemsize

        shape = (O3_NBR, NL_O3)
        dtype = u2
        itemsize = 2
        # scale = -14
        # mdr.O3_CP_O3_A, offset = generic_read(raw_data, offset, shape, dtype, scale)
        offset += np.prod(shape) * itemsize

        shape = (O3_NBR, NL_O3)
        # dtype = vu2
        itemsize = 3
        # mdr.O3_X_O3, offset = generic_read(raw_data, offset, shape, dtype, scale)
        offset += np.prod(shape) * itemsize

        shape = (O3_NBR, NEVA_O3)
        # dtype = vi4
        itemsize = 5
        # mdr.O3_H_EIGENVALUES, offset = generic_read(raw_data, offset, shape, dtype, scale)
        offset += np.prod(shape) * itemsize

        shape = (O3_NBR, NEVE_O3)
        # dtype = vi4
        itemsize = 5
        # mdr.O3_H_EIGENVECTORS, offset = generic_read(raw_data, offset, shape, dtype, scale)
        offset += np.prod(shape) * itemsize

        shape = (120,)
        dtype = u1
        scale = None
        mdr.SO2_QFLAG, offset = generic_read(raw_data, offset, shape, dtype, scale)
        # assert offset+_grh_offset == 422861

        shape = (120, NL_SO2)
        dtype = u2
        scale = 1
        mdr.SO2_COL_AT_ALTITUDES, offset = generic_read(raw_data, offset, shape, dtype, scale)
        # assert offset+_grh_offset == 424061

        shape = (120,)
        dtype = u2
        scale = None
        mdr.SO2_ALTITUDE, offset = generic_read(raw_data, offset, shape, dtype, scale)
        # assert offset+_grh_offset == 424301

        shape = (120,)
        dtype = u2
        scale = 1
        mdr.SO2_COL, offset = generic_read(raw_data, offset, shape, dtype, scale)
        # assert offset+_grh_offset == 424541

        shape = (120,)
        dtype = i2
        scale = 2
        mdr.SO2_BT_DIFFERENCE, offset = generic_read(raw_data, offset, shape, dtype, scale)
        # assert offset+_grh_offset == 424781
        print(offset)
        # assert grh.record_size == offset + GRH.size

        return mdr
