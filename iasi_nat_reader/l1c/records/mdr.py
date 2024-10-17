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
- Refactored MDR class.
"""

from numpy import fromstring, arange
import numpy as np

from ..utilities import where_greater, read_bitfield
from ...generic.record_content import interpreted_content
from ...generic.grh import GRH
from ...generic.parameters import *
from ...generic.read import (
    generic_read,
    read_short_date,
    b,
    i2,
    i4,
    u1,
    u2,
    u4,
    vi4,
)
from .record import Record
from .giadr import GIADR_scale_factors


class MDR(interpreted_content):
    def __init__(self) -> None:
        self.DEGRADED_INST_MDR = None
        self.DEGRADED_PROC_MDR = None
        self.GEPSIasiMode = None
        self.GEPSOPSProcessingMode = None
        self.GEPSIdConf = None
        self.GEPSLocIasiAvhrr_IASI = None
        self.GEPSLocIasiAvhrr_IIS = None
        self.OBT = None
        self.ONBoardUTC = None
        self.GEPSDatIasi = None
        self.GIsfLinOrigin = None
        self.GIsfColOrigin = None
        self.GIsfPds1 = None
        self.GIsfPds2 = None
        self.GIsfPds3 = None
        self.GIsfPds4 = None
        self.GEPS_CCD = None
        self.GEPS_SP = None
        self.GIrcImage = None
        self.GQisFlagQual = None
        self.GQisFlagQualDetailed = None
        self.GQisQualIndex = None
        self.GQisQualIndexIIS = None
        self.GQisQualIndexLoc = None
        self.GQisQualIndexRad = None
        self.GQisQualIndexSpect = None
        self.GQisSysTecIISQual = None
        self.GQisSysTecSondQual = None
        self.GGeoSondLoc = None
        self.GGeoSondAnglesMETOP = None
        self.GGeoIISAnglesMETOP = None
        self.GGeoSondAnglesSUN = None
        self.GGeoIISAnglesSUN = None
        self.GGeoIISLoc = None
        self.EARTH_SATELLITE_DISTANCE = None
        self.IDefSpectDWn1b = None
        self.IDefNsfirst1b = None
        self.IDefNslast1b = None
        self.GS1cSpect = None
        self.IDefCovarMatEigenVal1c = None
        self.IDefCcsChannelId = None
        self.GCcsRadAnalNbClass = None
        self.GCcsRadAnalWgt = None
        self.GCcsRadAnalY = None
        self.GCcsRadAnalZ = None
        self.GCcsRadAnalMean = None
        self.GCcsRadAnalStd = None
        self.GCcsImageClassified = None
        self.IDefCcsMode = None
        self.GCcsImageClassifiedNbLin = None
        self.GCcsImageClassifiedNbCol = None
        self.GCcsImageClassifiedFirstLin = None
        self.GCcsImageClassifiedFirstCol = None
        self.GCcsRadAnalType = None
        self.GIacVarImagIIS = None
        self.GIacAvgImagIIS = None
        self.GEUMAvhrr1BCldFrac = None
        self.GEUMAvhrr1BLandFrac = None
        self.GEUMAvhrr1BQual = None

    @staticmethod
    def read(record: Record, giadr_sf: GIADR_scale_factors):
        raw_data: bytes = record.content
        grh: GRH = record.grh

        mdr = MDR()

        offset = 0
        increase = 0

        shape = (1,)
        dtype = b
        scale = None
        mdr.DEGRADED_INST_MDR, offset = generic_read(raw_data, offset, shape, dtype, scale)

        shape = (1,)
        dtype = b
        scale = None
        mdr.DEGRADED_PROC_MDR, offset = generic_read(raw_data, offset, shape, dtype, scale)

        shape = (1,)
        increase = np.prod(shape) * 4
        mdr.GEPSIasiMode = read_bitfield(raw_data[offset : offset + increase], 'GEPSIasiMode')
        offset += increase

        shape = (1,)
        increase = np.prod(shape) * 4
        mdr.GEPSOPSProcessingMode = read_bitfield(raw_data[offset : offset + increase], 'GEPSOPSProcessingMode')
        offset += increase

        shape = (1,)
        increase = np.prod(shape) * 32
        mdr.GEPSIdConf = read_bitfield(raw_data[offset : offset + increase], 'GEPSIdConf')
        offset += increase

        shape = (SNOT, PN, 2)
        dtype = vi4
        scale = None
        mdr.GEPSLocIasiAvhrr_IASI, offset = generic_read(raw_data, offset, shape, dtype, scale)

        shape = (SNOT, SGI, 2)
        dtype = vi4
        scale = None
        mdr.GEPSLocIasiAvhrr_IIS, offset = generic_read(raw_data, offset, shape, dtype, scale)

        increase = 6 * SNOT
        mdr.OBT = fromstring(raw_data[offset : offset + increase], dtype=u1).reshape(SNOT, 6)
        offset += increase

        increase = SNOT * 6
        mdr.ONBoardUTC = read_short_date(raw_data[offset : offset + increase])
        offset += increase

        increase = SNOT * 6
        mdr.GEPSDatIasi = read_short_date(raw_data[offset : offset + increase])
        offset += increase

        shape = (CCD,)
        dtype = i4
        scale = None
        mdr.GIsfLinOrigin, offset = generic_read(raw_data, offset, shape, dtype, scale)

        shape = (CCD,)
        dtype = i4
        scale = None
        mdr.GIsfColOrigin, offset = generic_read(raw_data, offset, shape, dtype, scale)

        shape = (CCD,)
        dtype = i4
        scale = 6
        mdr.GIsfPds1, offset = generic_read(raw_data, offset, shape, dtype, scale)

        shape = (CCD,)
        dtype = i4
        scale = 6
        mdr.GIsfPds2, offset = generic_read(raw_data, offset, shape, dtype, scale)

        shape = (CCD,)
        dtype = i4
        scale = 6
        mdr.GIsfPds3, offset = generic_read(raw_data, offset, shape, dtype, scale)

        shape = (CCD,)
        dtype = i4
        scale = 6
        mdr.GIsfPds4, offset = generic_read(raw_data, offset, shape, dtype, scale)

        shape = (SNOT,)
        dtype = b
        scale = None
        mdr.GEPS_CCD, offset = generic_read(raw_data, offset, shape, dtype, scale)

        shape = (SNOT,)
        dtype = i4
        scale = None
        mdr.GEPS_SP, offset = generic_read(raw_data, offset, shape, dtype, scale)

        shape = (SNOT, IMLI, IMCO)
        dtype = u2
        scale = -5  # W/m2/sr/m-1 -> mW/m2/sr/cm-1
        mdr.GIrcImage, offset = generic_read(raw_data, offset, shape, dtype, scale)
        # mdr.GIrcImage = mdr.GIrcImage.astype(np.float64)
        # UFuncTypeError: Cannot cast ufunc 'multiply' output from dtype('float64') to dtype('>u2') with casting rule 'same_kind'

        if grh.record_subclass_version == 4:
            shape = (SNOT, PN)
            dtype = b
            scale = None
            mdr.GQisFlagQual, offset = generic_read(raw_data, offset, shape, dtype, scale)
        elif grh.record_subclass_version == 5:
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
        mdr.GQisQualIndexIIS, offset = generic_read(raw_data, offset, shape, dtype, scale)

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
        mdr.GQisSysTecIISQual, offset = generic_read(raw_data, offset, shape, dtype, scale)

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

        shape = (SNOT, SGI, 2)
        dtype = i4
        scale = 6
        mdr.GGeoIISAnglesMETOP, offset = generic_read(raw_data, offset, shape, dtype, scale)

        shape = (SNOT, PN, 2)
        dtype = i4
        scale = 6
        mdr.GGeoSondAnglesSUN, offset = generic_read(raw_data, offset, shape, dtype, scale)

        shape = (SNOT, SGI, 2)
        dtype = i4
        scale = 6
        mdr.GGeoIISAnglesSUN, offset = generic_read(raw_data, offset, shape, dtype, scale)

        shape = (SNOT, SGI, 2)
        dtype = i4
        scale = 6
        mdr.GGeoIISLoc, offset = generic_read(raw_data, offset, shape, dtype, scale)

        shape = (1,)
        dtype = u4
        scale = None
        mdr.EARTH_SATELLITE_DISTANCE, offset = generic_read(raw_data, offset, shape, dtype, scale)

        shape = (1,)
        dtype = vi4
        scale = None
        mdr.IDefSpectDWn1b, offset = generic_read(raw_data, offset, shape, dtype, scale)

        shape = (1,)
        dtype = i4
        scale = None
        mdr.IDefNsfirst1b, offset = generic_read(raw_data, offset, shape, dtype, scale)

        shape = (1,)
        dtype = i4
        scale = None
        mdr.IDefNslast1b, offset = generic_read(raw_data, offset, shape, dtype, scale)

        num_ch = mdr.IDefNslast1b - mdr.IDefNsfirst1b + 1

        pos = where_greater(giadr_sf.IDefScaleSondNslast, arange(num_ch) + mdr.IDefNsfirst1b)
        rad_sfs = giadr_sf.IDefScaleSondScaleFactor[pos]

        shape = (SNOT, PN, SS)
        dtype = i2
        scale = None
        GS1cSpect, offset = generic_read(raw_data, offset, shape, dtype, scale)
        # With the following two lines you have the original data format
        # with some useless values
        # mdr.GS1cSpect = zeros((SS, PN, SNOT), dtype=float64)
        # mdr.GS1cSpect[0:num_ch,:,:] = GS1cSpect[0:num_ch,:,:] / 10.**rad_sfs[:, newaxis, newaxis]
        # With this, instead, you have only the real data
        mdr.GS1cSpect = GS1cSpect[:, :, 0:num_ch] / 10.0**rad_sfs * 1e5  # W/(m² sr m^-1) -> mW/m2/sr/cm-1

        shape = (100, CCD)
        dtype = vi4
        scale = None
        mdr.IDefCovarMatEigenVal1c, offset = generic_read(raw_data, offset, shape, dtype, scale)

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
        # scale = None
        scale = -3  # W/* -> mW/*
        mdr.GCcsRadAnalMean, offset = generic_read(raw_data, offset, shape, dtype, scale)

        shape = (SNOT, PN, NCL, NBK)
        dtype = vi4
        # scale = None
        scale = -3  # W/* -> mW/*
        mdr.GCcsRadAnalStd, offset = generic_read(raw_data, offset, shape, dtype, scale)

        shape = (SNOT, AMLI, AMCO)
        dtype = u1
        scale = None
        mdr.GCcsImageClassified, offset = generic_read(raw_data, offset, shape, dtype, scale)

        shape = (1,)
        increase = np.prod(shape) * 4
        mdr.IDefCcsMode = read_bitfield(raw_data[offset : offset + increase], 'IDefCcsMode')
        offset += increase

        shape = (SNOT,)
        dtype = i2
        scale = None
        mdr.GCcsImageClassifiedNbLin, offset = generic_read(raw_data, offset, shape, dtype, scale)

        shape = (SNOT,)
        dtype = i2
        scale = None
        mdr.GCcsImageClassifiedNbCol, offset = generic_read(raw_data, offset, shape, dtype, scale)

        shape = (SNOT,)
        dtype = vi4
        scale = None
        mdr.GCcsImageClassifiedFirstLin, offset = generic_read(raw_data, offset, shape, dtype, scale)

        shape = (SNOT,)
        dtype = vi4
        scale = None
        mdr.GCcsImageClassifiedFirstCol, offset = generic_read(raw_data, offset, shape, dtype, scale)

        shape = (SNOT, NCL)
        dtype = b
        scale = None
        mdr.GCcsRadAnalType, offset = generic_read(raw_data, offset, shape, dtype, scale)

        if grh.record_subclass_version == 5:
            shape = (SNOT,)
            dtype = vi4
            scale = -5  # W/(m² sr m^-1) -> mW/(m² sr cm^-1)
            mdr.GIacVarImagIIS, offset = generic_read(raw_data, offset, shape, dtype, scale)

            shape = (SNOT,)
            dtype = vi4
            scale = -5  # W/(m² sr m^-1) -> mW/(m² sr cm^-1)
            mdr.GIacAvgImagIIS, offset = generic_read(raw_data, offset, shape, dtype, scale)

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

        assert grh.record_size == offset + GRH.size

        return mdr

    def get_times(self):
        from datetime import datetime, timedelta

        start_day = datetime(2000, 1, 1)
        return [
            start_day + timedelta(days=int(days), milliseconds=int(msec))
            for days, msec in self.GEPSDatIasi
        ]

    def __str__(self):
        output = "============ IASI MDR 1C ============\n"
        output += "Degraded inst mdr = " + str(self.DEGRADED_INST_MDR) + "\n"
        output += "Degraded proc mdr = " + str(self.DEGRADED_PROC_MDR) + "\n"
        output += "GEPS Iasi mode = " + str(self.GEPSIasiMode) + "\n"
        output += "GEPSOPSPROC Mode = " + str(self.GEPSOPSProcessingMode) + "\n"
        output += "GEPS id conf =\n" + str(self.GEPSIdConf) + "\n"
        output += "GEPS LocIasiAvhrr IASI =\n" + str(self.GEPSLocIasiAvhrr_IASI) + "\n"
        output += "GEPS LocIasiAvhrr IIS =\n" + str(self.GEPSLocIasiAvhrr_IIS) + "\n"
        output += "OBT =\n" + str(self.OBT) + "\n"
        output += "ONBoard UTC =\n" + str(self.ONBoardUTC) + "\n"
        output += "GEPS Date Iasi =\n" + str(self.GEPSDatIasi) + "\n"
        output += "GIsfLinOrigin = " + str(self.GIsfLinOrigin) + "\n"
        output += "GIsfColOrigin = " + str(self.GIsfColOrigin) + "\n"
        output += "GIsfPds1 = " + str(self.GIsfPds1) + "\n"
        output += "GIsfPds2 = " + str(self.GIsfPds2) + "\n"
        output += "GIsfPds3 = " + str(self.GIsfPds3) + "\n"
        output += "GIsfPds4 = " + str(self.GIsfPds4) + "\n"
        output += "GEPS CCD =\n" + str(self.GEPS_CCD) + "\n"
        output += "GEPS SP =\n" + str(self.GEPS_SP) + "\n"
        output += "GIrcImage =\n" + str(self.GIrcImage) + "\n"
        output += "GQisFlagQual =\n" + str(self.GQisFlagQual) + "\n"
        try:
            output += "GQisFlagQualDetailed =\n" + str(self.GQisFlagQualDetailed) + "\n"
        except AttributeError:
            pass
        output += "GQisQualIndex = " + str(self.GQisQualIndex) + "\n"
        output += "GQisQualIndexIIS = " + str(self.GQisQualIndexIIS) + "\n"
        output += "GQisQualIndexLoc = " + str(self.GQisQualIndexLoc) + "\n"
        output += "GQisQualIndexRas = " + str(self.GQisQualIndexRad) + "\n"
        output += "GQisQualIndexSpect = " + str(self.GQisQualIndexSpect) + "\n"
        output += "GQisSysTecIISQual = " + str(self.GQisSysTecIISQual) + "\n"
        output += "GQisSysTecSondQual = " + str(self.GQisSysTecSondQual) + "\n"
        output += "GGeoSondLoc =\n" + str(self.GGeoSondLoc) + "\n"
        output += "GGeoSondAnglesMETOP =\n" + str(self.GGeoSondAnglesMETOP) + "\n"
        output += "GGeoIISAnglesMETOP =\n" + str(self.GGeoIISAnglesMETOP) + "\n"
        output += "GGeoSondAnglesSUN =\n" + str(self.GGeoSondAnglesSUN) + "\n"
        output += "GGeoIISAnglesSUN =\n" + str(self.GGeoIISAnglesSUN) + "\n"
        output += "GGeoIISLoc =\n" + str(self.GGeoIISLoc) + "\n"
        output += "Earth-Satellite Distance = " + str(self.EARTH_SATELLITE_DISTANCE) + "\n"
        output += "IDefSpectDWn1b = " + str(self.IDefSpectDWn1b) + "\n"
        output += "IDefNsfirst1b = " + str(self.IDefNsfirst1b) + "\n"
        output += "IDefNsLAST1b = " + str(self.IDefNslast1b) + "\n"
        output += "GS1cSpect =\n" + str(self.GS1cSpect) + "\n"
        output += "IDefCovarMatEigenVal1c =\n" + str(self.IDefCovarMatEigenVal1c) + "\n"
        output += "IDefCcsChannelId = " + str(self.IDefCcsChannelId) + "\n"
        output += "GCcsRadAnalNbClass =\n" + str(self.GCcsRadAnalNbClass) + "\n"
        output += "GCcsRadAnalWgt =\n" + str(self.GCcsRadAnalWgt) + "\n"
        output += "GCcsRadAnalY =\n" + str(self.GCcsRadAnalY) + "\n"
        output += "GCcsRadAnalZ =\n" + str(self.GCcsRadAnalZ) + "\n"
        output += "GCcsRadAnalMean =\n" + str(self.GCcsRadAnalMean) + "\n"
        output += "GCcsRadAnalStd =\n" + str(self.GCcsRadAnalStd) + "\n"
        output += "GCcsImageClassified =\n" + str(self.GCcsImageClassified) + "\n"
        output += "IDefCcsMode = " + str(self.IDefCcsMode) + "\n"
        output += "GCcsImageClassifiedNbLin =\n" + str(self.GCcsImageClassifiedNbLin) + "\n"
        output += "GCcsImageClassifiedNbCol =\n" + str(self.GCcsImageClassifiedNbCol) + "\n"
        output += (
            "GCcsImageClassifiedFirstLin =\n"
            + str(self.GCcsImageClassifiedFirstLin)
            + "\n"
        )
        output += "GCcsImageClassifiedFirstCol =\n" + str(self.GCcsImageClassifiedFirstCol) + "\n"
        output += "GCcsRadAnalType =\n" + str(self.GCcsRadAnalType) + "\n"
        try:
            output += "GIacVarImagIIS =\n" + str(self.GIacVarImagIIS) + "\n"
            output += "GEUMAvhrr1BCldFrac =\n" + str(self.GEUMAvhrr1BCldFrac) + "\n"
            output += "GEUMAvhrr1BLandFrac =\n" + str(self.GEUMAvhrr1BLandFrac) + "\n"
            output += "GEUMAvhrr1BQual =\n" + str(self.GEUMAvhrr1BQual) + "\n"
        except AttributeError:
            pass

        return output
