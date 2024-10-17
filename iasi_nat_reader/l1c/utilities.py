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
- Moved `read_vint` and  `read_short_date` functions to read.py in generic package.
- Added `read_bitfield` function.
"""

from __future__ import division

from struct import unpack
from numpy import meshgrid, argmax, max


def where_greater(a, b):
    """
    Given two array, a and b, return a new array c with the same
    length as b such that c[i] is the index of the first element
    of a to be greater (or equal) than b[i] (if there is not such
    an element, it returns -1 on that entry)
    """

    M = meshgrid(a, b)
    comparisons = a >= M[1]
    output = argmax(comparisons, axis=1)
    # Now, when every element in a is smaller than the elements in b,
    # we have 0 as entry. Now we will put that entries to -1
    fix_empty_entries = max(comparisons, axis=1) - 1
    output += fix_empty_entries
    return output


def read_bitfield(raw_data, name):

    if name == 'GEPSIasiMode':
        assert len(raw_data) == 4
        # return unpack('>HBB',raw_data)[:-1]
        return unpack('>hbb', raw_data)[:-1]

    elif name == 'GEPSOPSProcessingMode':
        assert len(raw_data) == 4
        # The first two digits indicate `level` and are extracted using the mask `0x03`
        level = raw_data[0] & 0x03
        instrument_mode = (raw_data[0] >> 2) & 0x01
        debug_mode = (raw_data[0] >> 3) & 0x01
        interface_mode = (raw_data[0] >> 4) & 0x01
        target_type = (raw_data[0] >> 5) & 0x01
        return level, instrument_mode, debug_mode, interface_mode, target_type

    elif name == 'GEPSIdConf':
        assert len(raw_data) == 32
        ptsi, idef_id_conf = unpack('>LL', raw_data[:8])
        bits = unpack('>Q', raw_data[8:16])[0]  # 64-bit integer
        normal_processing = (bits >> 0) & 0x01
        backlog_processing = (bits >> 1) & 0x01
        re_processing = (bits >> 2) & 0x01
        parallel_validation = (bits >> 3) & 0x01
        in_plane_manoeuvre = (bits >> 4) & 0x01
        gops_flags = {}
        gops_flags['GOPSFlaPixMiss'] = (bits >> 5) & 0x01
        gops_flags['GOPSFlaDataGap'] = (bits >> 6) & 0x01
        gops_flags['GOPSFltIsrfemOff'] = (bits >> 7) & 0x01
        gops_flags['GOPSFltBandMiss'] = (bits >> 8) & 0x01
        gops_flags['GOPSFltBBTMiss'] = (bits >> 9) & 0x01
        gops_flags['GOPSFltImgEWMiss'] = (bits >> 10) & 0x01
        gops_flags['GOPSFltImgBBMiss'] = (bits >> 11) & 0x01
        gops_flags['GOPSFltImgCSMiss'] = (bits >> 12) & 0x01
        gops_flags['GOPSFlagPacketVPMiss'] = (bits >> 13) & 0x01
        gops_flags['GOPSFlagPacketAPMiss'] = (bits >> 14) & 0x01
        gops_flags['GOPSFlagPacketPXMiss'] = (bits >> 15) & 0x01
        gops_flags['GOPSFlagPacketIPMiss'] = (bits >> 16) & 0x01

        return (
            ptsi,
            idef_id_conf,
            normal_processing,
            backlog_processing,
            re_processing,
            parallel_validation,
            in_plane_manoeuvre,
            gops_flags,
        )

    elif name == 'IDefCcsMode':
        assert len(raw_data) == 4
        return raw_data[0] >> 0

    elif name == 'GQisFlagQualDetailed':
        assert len(raw_data) == 2

        byte1 = raw_data[0]
        hardware = (byte1 >> 7) & 0x01
        band1_spikes = (byte1 >> 6) & 0x01
        band2_spikes = (byte1 >> 5) & 0x01
        band3_spikes = (byte1 >> 4) & 0x01
        nzpd_complex_error = (byte1 >> 3) & 0x01
        onboard_quality_flag = (byte1 >> 2) & 0x01
        overflow_underflow = (byte1 >> 1) & 0x01
        spectral_calibration_error = byte1 & 0x01

        byte2 = raw_data[1]
        radiometric_post_calibration_error = (byte2 >> 7) & 0x01
        gqis_flag_qual_summary = (byte2 >> 6) & 0x01
        missing_sounder_data = (byte2 >> 5) & 0x01
        missing_iis_data = (byte2 >> 4) & 0x01
        missing_avhrr_data = (byte2 >> 3) & 0x01

        return (
            hardware,
            band1_spikes,
            band2_spikes,
            band3_spikes,
            nzpd_complex_error,
            onboard_quality_flag,
            overflow_underflow,
            spectral_calibration_error,
            radiometric_post_calibration_error,
            gqis_flag_qual_summary,
            missing_sounder_data,
            missing_iis_data,
            missing_avhrr_data,
        )

    elif name == 'GEUMAvhrr1BQual':
        assert len(raw_data) == 1
        byte = raw_data[0]
        if byte & 0x80:  # Keep the eighth bit and the rest are 0
            # If Bit 7 is 1, it is a count value
            # Keep the last seven bits and the rest are 0
            num_missing_bad_pixels = byte & 0x7F
            return ['missing', num_missing_bad_pixels]
        else:
            # If Bit 7 is 0, it is a percentage
            # Keep the last seven bits and the rest are 0
            fraction_covered_with_snow_ice = byte & 0x7F
            return ['good', fraction_covered_with_snow_ice]
