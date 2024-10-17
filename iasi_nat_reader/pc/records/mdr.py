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

import io, cProfile, pstats
import numpy as np
from numpy import fromstring

from ...generic.record_content import interpreted_content
from ...generic.grh import GRH
from ...generic.parameters import *
from ...generic.read import (
    generic_read,
    read_short_date,
    b,
    i1,
    i2,
    i4,
    u1,
    u2,
    u4,
    vi4,
)

from .record import Record
from .giadr import GIADR
from ...l1c.utilities import read_bitfield

debug = False

_grh_offset = 20


class MDR_PCR(interpreted_content):
    def __init__(self) -> None:
        self.DEGRADED_INST_MDR = None
        self.DEGRADED_PROC_MDR = None
        self.PccResidual = None

    @staticmethod
    def read(record: Record, giadr: GIADR):
        raw_data: bytes = record.content
        grh: GRH = record.grh

        mdr = MDR_PCR()

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

        shape = (SNOT, PN, S)
        dtype = i1
        scale = None
        mdr.PccResidual, offset = generic_read(raw_data, offset, shape, dtype, scale)

        assert grh.record_size == offset + GRH.size

        return mdr


class MDR_PCS(interpreted_content):
    def __init__(self) -> None:
        self.DEGRADED_INST_MDR = None
        self.DEGRADED_PROC_MDR = None
        self.GEPSIasiMode = None
        self.GEPSOPSProcessingMode = None
        self.GEPSIdConf = None
        self.OBT = None
        self.ONBoardUTC = None
        self.GEPSDatIasi = None
        self.GEPS_SP = None
        self.GQisFlagQual = None
        self.GQisFlagQualDetailed = None
        self.GQisQualIndex = None
        self.GQisQualIndexLoc = None
        self.GQisQualIndexRad = None
        self.GQisQualIndexSpect = None
        self.GQisSysTecSondQual = None
        self.GGeoSondLoc = None
        self.GGeoSondAnglesMETOP = None
        self.GGeoSondAnglesSUN = None
        self.EARTH_SATELLITE_DISTANCE = None
        self.IDefCcsChannelId = None
        self.GCcsRadAnalNbClass = None
        self.GCcsRadAnalWgt = None
        self.GCcsRadAnalY = None
        self.GCcsRadAnalZ = None
        self.GCcsRadAnalMean = None
        self.GCcsRadAnalStd = None
        self.GEUMAvhrr1BCldFrac = None
        self.GEUMAvhrr1BLandFrac = None
        self.GEUMAvhrr1BQual = None
        self.PcScoresB1P1 = None
        self.PcScoresB1P2 = None
        self.PcScoresB1P3 = None
        self.PcScoresB2P1 = None
        self.PcScoresB2P2 = None
        self.PcScoresB2P3 = None
        self.PcScoresB3P1 = None
        self.PcScoresB3P2 = None
        self.PcScoresB3P3 = None
        self.ResidualRMS = None

    @staticmethod
    def read(record: Record, giadr: GIADR):
        if debug:
            profile = cProfile.Profile()
            profile.enable()

        raw_data: bytes = record.content
        grh: GRH = record.grh

        mdr = MDR_PCS()

        NBS1P1 = giadr.NBS1P1
        NBS1P2 = giadr.NBS1P2
        NBS1P3 = giadr.NBS1P3
        NBS2P1 = giadr.NBS2P1
        NBS2P2 = giadr.NBS2P2
        NBS2P3 = giadr.NBS2P3
        NBS3P1 = giadr.NBS3P1
        NBS3P2 = giadr.NBS3P2
        NBS3P3 = giadr.NBS3P3

        offset = 0

        shape = (1,)
        dtype = b
        scale = None
        mdr.DEGRADED_INST_MDR, offset = generic_read(raw_data, offset, shape, dtype, scale)
        # assert offset + _grh_offset == 21

        shape = (1,)
        dtype = b
        scale = None
        mdr.DEGRADED_PROC_MDR, offset = generic_read(raw_data, offset, shape, dtype, scale)
        # assert offset + _grh_offset == 22

        shape = (1,)
        increase = np.prod(shape) * 4
        mdr.GEPSIasiMode = read_bitfield(raw_data[offset : offset + increase], 'GEPSIasiMode')
        offset += increase
        # assert offset + _grh_offset == 26

        shape = (1,)
        increase = np.prod(shape) * 4
        mdr.GEPSOPSProcessingMode = read_bitfield(raw_data[offset : offset + increase], 'GEPSOPSProcessingMode')
        offset += increase
        # assert offset + _grh_offset == 30

        shape = (1,)
        increase = np.prod(shape) * 32
        mdr.GEPSIdConf = read_bitfield(raw_data[offset : offset + increase], 'GEPSIdConf')
        offset += increase
        # assert offset + _grh_offset == 62

        increase = 6 * SNOT
        mdr.OBT = fromstring(raw_data[offset : offset + increase], dtype=u1).reshape(SNOT, 6)
        offset += increase
        # assert offset + _grh_offset == 242

        increase = SNOT * 6
        mdr.ONBoardUTC = read_short_date(raw_data[offset : offset + increase])
        offset += increase
        # assert offset + _grh_offset == 422

        increase = SNOT * 6
        mdr.GEPSDatIasi = read_short_date(raw_data[offset : offset + increase])
        offset += increase
        # assert offset + _grh_offset == 602

        shape = (SNOT,)
        dtype = i4
        scale = None
        mdr.GEPS_SP, offset = generic_read(raw_data, offset, shape, dtype, scale)

        shape = (SNOT, PN, SB)
        dtype = b
        scale = None
        mdr.GQisFlagQual, offset = generic_read(raw_data, offset, shape, dtype, scale)

        shape = (SNOT, PN)
        dtype = i2
        scale = None
        mdr.GQisFlagQualDetailed, offset = generic_read(raw_data, offset, shape, dtype, scale)

        shape = (1,)
        dtype = vi4
        scale = None
        mdr.GQisQualIndex, offset = generic_read(raw_data, offset, shape, dtype, scale)

        shape = (1,)
        dtype = vi4
        scale = None
        mdr.GQisQualIndexLoc, offset = generic_read(raw_data, offset, shape, dtype, scale)

        shape = (1,)
        dtype = vi4
        scale = None
        mdr.GQisQualIndexRad, offset = generic_read(raw_data, offset, shape, dtype, scale)

        shape = (1,)
        dtype = vi4
        scale = None
        mdr.GQisQualIndexSpect, offset = generic_read(raw_data, offset, shape, dtype, scale)

        shape = (1,)
        dtype = u4
        scale = None
        mdr.GQisSysTecSondQual, offset = generic_read(raw_data, offset, shape, dtype, scale)

        shape = (SNOT, PN, 2)
        dtype = i4
        scale = 6
        mdr.GGeoSondLoc, offset = generic_read(raw_data, offset, shape, dtype, scale)

        shape = (SNOT, PN, 2)
        dtype = i4
        scale = 6
        mdr.GGeoSondAnglesMETOP, offset = generic_read(raw_data, offset, shape, dtype, scale)

        shape = (SNOT, PN, 2)
        dtype = i4
        scale = 6
        mdr.GGeoSondAnglesSUN, offset = generic_read(raw_data, offset, shape, dtype, scale)

        shape = (1,)
        dtype = u4
        scale = None
        mdr.EARTH_SATELLITE_DISTANCE, offset = generic_read(raw_data, offset, shape, dtype, scale)

        shape = (NBK,)
        dtype = i4
        scale = None
        mdr.IDefCcsChannelId, offset = generic_read(raw_data, offset, shape, dtype, scale)

        shape = (SNOT, PN)
        dtype = i4
        scale = None
        mdr.GCcsRadAnalNbClass, offset = generic_read(raw_data, offset, shape, dtype, scale)

        shape = (SNOT, PN, NCL)
        dtype = vi4
        scale = None
        mdr.GCcsRadAnalWgt, offset = generic_read(raw_data, offset, shape, dtype, scale)

        shape = (SNOT, PN, NCL)
        dtype = i4
        scale = 6
        mdr.GCcsRadAnalY, offset = generic_read(raw_data, offset, shape, dtype, scale)

        shape = (SNOT, PN, NCL)
        dtype = i4
        scale = 6
        mdr.GCcsRadAnalZ, offset = generic_read(raw_data, offset, shape, dtype, scale)

        shape = (SNOT, PN, NCL, NBK)
        dtype = vi4
        scale = -3  # W/* -> mW/
        mdr.GCcsRadAnalMean, offset = generic_read(raw_data, offset, shape, dtype, scale)

        shape = (SNOT, PN, NCL, NBK)
        dtype = vi4
        scale = -3  #  W/* -> mW/*
        mdr.GCcsRadAnalStd, offset = generic_read(raw_data, offset, shape, dtype, scale)

        shape = (SNOT, PN)
        dtype = u1
        scale = None
        mdr.GEUMAvhrr1BCldFrac, offset = generic_read(raw_data, offset, shape, dtype, scale)

        shape = (SNOT, PN)
        dtype = u1
        scale = None
        mdr.GEUMAvhrr1BLandFrac, offset = generic_read(raw_data, offset, shape, dtype, scale)

        GEUMAvhrr1BQual = []
        shape = (SNOT, PN)
        increase = np.prod(shape)
        for i in range(increase):
            GEUMAvhrr1BQual.append(read_bitfield(raw_data[offset : offset + 1], 'GEUMAvhrr1BQual'))
            offset += 1
        mdr.GEUMAvhrr1BQual = GEUMAvhrr1BQual

        shape = (SNOT, PN, NBS1P1)
        dtype = i4
        scale = None
        mdr.PcScoresB1P1, offset = generic_read(raw_data, offset, shape, dtype, scale)

        shape = (SNOT, PN, NBS1P2)
        dtype = i2
        scale = None
        mdr.PcScoresB1P2, offset = generic_read(raw_data, offset, shape, dtype, scale)

        shape = (SNOT, PN, NBS1P3)
        dtype = i1
        scale = None
        mdr.PcScoresB1P3, offset = generic_read(raw_data, offset, shape, dtype, scale)

        shape = (SNOT, PN, NBS2P1)
        dtype = i4
        scale = None
        mdr.PcScoresB2P1, offset = generic_read(raw_data, offset, shape, dtype, scale)

        shape = (SNOT, PN, NBS2P2)
        dtype = i2
        scale = None
        mdr.PcScoresB2P2, offset = generic_read(raw_data, offset, shape, dtype, scale)

        shape = (SNOT, PN, NBS2P3)
        dtype = i1
        scale = None
        mdr.PcScoresB2P3, offset = generic_read(raw_data, offset, shape, dtype, scale)

        shape = (SNOT, PN, NBS3P1)
        dtype = i4
        scale = None
        mdr.PcScoresB3P1, offset = generic_read(raw_data, offset, shape, dtype, scale)

        shape = (SNOT, PN, NBS3P2)
        dtype = i2
        scale = None
        mdr.PcScoresB3P2, offset = generic_read(raw_data, offset, shape, dtype, scale)

        shape = (SNOT, PN, NBS3P3)
        dtype = i1
        scale = None
        mdr.PcScoresB3P3, offset = generic_read(raw_data, offset, shape, dtype, scale)

        shape = (SNOT, PN, SB)
        dtype = u2
        scale = 3
        mdr.ResidualRMS, offset = generic_read(raw_data, offset, shape, dtype, scale)

        assert grh.record_size == offset + GRH.size

        if debug:
            profile.disable()
            s = io.StringIO()
            ps = pstats.Stats(profile, stream=s).sort_stats('cumulative')
            ps.print_stats()
            print(s.getvalue())

        return mdr
