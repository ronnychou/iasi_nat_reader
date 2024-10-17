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
- Removed support for python 2.x.
- Refactored MPHR class.
"""

from typing import IO

from .record_content import interpreted_content
from .grh import GRH
from .units import units

instrument_model_dict = {
    0: 'Reserved',
    1: 'Flight Model 1',
    2: 'Flight Model 2',
    3: 'Engineering Model',
    4: 'Protoflight Model',
}

processing_centre_dict = {
    'CGS1': 'First EUMETSAT EPS Core Ground Segment',
    'CGS2': 'Second EUMETSAT EPS Core Ground Segment',
    'NSSx': 'NOAA/NESDIS',
    'RUSx': 'Reference User Station',
    'DMIx': 'DMI, Copenhagen (GRAS SAF)',
    'DWDx': 'DWD, Offenbach (Climate SAF)',
    'FMIx': 'FMI , Helsinki (Ozone SAF)',
    'IMPx': 'IMP, Lisbon (Land SAF)',
    'INMx': 'INM, Madrid (NCW SAF)',
    'MFxx': 'MF, Lannion (OSI SAF)',
    'UKMO': 'UKMO, Bracknell (NWP SAF)',
}

processing_mode_dict = {
    'N': 'Nominal',
    'B': 'Backlog Processing',
    'R': 'Reprocessing',
    'V': 'Validation',
}

disposition_mode_dict = {
    'T': 'Testing',
    'O': 'Oprational',
    'C': 'Commissioning',
}

receiving_ground_station_dict = {
    'SVL': 'Svalbard',
    'WAL': 'Wallops Island, Virginia',
    'FBK': 'Fairbanks, Alaska',
    'SOC': 'SOCC (NESDIS Satellite Operations Control Centre), Suitland, Maryland',
    'RUS': 'Reference User Station',
    'SVL': 'Svalbard',
}

product_type_dict = {
    'ENG': 'IASI engineering data',
    'GAC': 'NOAC Global Area Coverage AVHRR data',
    'SND': 'Sounding Data',
    'SZF': 'ASCAT calibrated s0 data at full resolution',
    'SZO': 'ASCAT calibrated s0 data at operational resolution (50 km)',
    'SZR': 'ASCAT calibrated s0 data at research resolution (25 km)',
    'VER': 'IASI verification data',
    'xxx': 'No specific product type specified',
    'AIP': 'NOAA AIP/SAIP data',
    'TIP': 'NOAA TIP/STIP data',
    'HRP': 'HRPT data',
    'LRP': 'LRPT data',
    'PCS': 'Principal Component Scores data\nPrincipal component compressed IASI L1C spectra',
    'PCR': 'Principal Component Residuals data\nResidual after reconstruction of principal component compressed IASI L1C spectra',
}


def parse(x: str):
    return x.split('=')[1].strip()


class MPHR(interpreted_content):
    def __init__(self) -> None:
        self.__raw = None
        self.product_name = None
        self.parent_product_name1 = None
        self.parent_product_name2 = None
        self.parent_product_name3 = None
        self.parent_product_name4 = None
        self.instrument_id = None
        self.instrument_model = None
        self.product_type = None
        self.processing_level = None
        self.spacecraft_id = None
        self.sensing_start = None
        self.sensing_end = None
        self.sensing_start_theoretical = None
        self.sensing_end_theoretical = None
        self.processing_centre = None
        self.processor_major_version = None
        self.processor_minor_version = None
        self.format_major_version = None
        self.format_minor_version = None
        self.processing_time_start = None
        self.processing_time_end = None
        self.processing_mode = None
        self.disposition_mode = None
        self.receiving_ground_station = None
        self.receive_time_start = None
        self.receive_time_end = None
        self.orbit_start = None
        self.orbit_end = None
        self.actual_product_size = None
        self.state_vector_time = None
        self.semi_major_axis = None
        self.eccentricity = None
        self.inclination = None
        self.perigee_argument = None
        self.right_ascension = None
        self.mean_anomaly = None
        self.x_position = None
        self.y_position = None
        self.z_position = None
        self.x_velocity = None
        self.y_velocity = None
        self.z_velocity = None
        self.earth_sun_distance_ratio = None
        self.location_tolerance_radial = None
        self.location_tolerance_crosstrack = None
        self.location_tolerance_alongtrack = None
        self.yaw_error = None
        self.roll_error = None
        self.pitch_error = None
        self.subsat_latitude_start = None
        self.subsat_longitude_start = None
        self.subsat_latitude_end = None
        self.subsat_longitude_end = None
        self.leap_second = None
        self.leap_second_utc = None
        self.total_records = None
        self.total_mphr = None
        self.total_sphr = None
        self.total_ipr = None
        self.total_geadr = None
        self.total_giadr = None
        self.total_veadr = None
        self.total_viadr = None
        self.total_mdr = None
        self.count_degraded_inst_mdr = None
        self.count_degraded_proc_mdr = None
        self.count_degraded_inst_mdr_blocks = None
        self.count_degraded_proc_mdr_blocks = None
        self.duration_of_product = None
        self.milliseconds_of_data_present = None
        self.milliseconds_of_data_missing = None
        self.subsetted_product = None

    @property
    def raw(self):
        return self.__raw

    @staticmethod
    def read(f: IO, grh: GRH):
        mphr = MPHR()
        raw_data: bytes = f.read(grh.record_size - GRH.size)
        mphr.__raw = raw_data
        raw_data = raw_data.decode('ASCII')
        data = raw_data.split('\n')

        mphr.product_name = parse(data[0])

        mphr.parent_product_name1 = parse(data[1])

        mphr.parent_product_name2 = parse(data[2])

        mphr.parent_product_name3 = parse(data[3])

        mphr.parent_product_name4 = parse(data[4])

        mphr.instrument_id = parse(data[5])

        instrument_model = int(parse(data[6]))
        mphr.instrument_model = instrument_model_dict.get(instrument_model, None)

        mphr.product_type = parse(data[7])

        mphr.processing_level = parse(data[8])

        mphr.spacecraft_id = parse(data[9])

        mphr.sensing_start = parse(data[10])

        mphr.sensing_end = parse(data[11])

        mphr.sensing_start_theoretical = parse(data[12])

        mphr.sensing_end_theoretical = parse(data[13])

        processing_centre = parse(data[14])
        mphr.processing_centre = processing_centre_dict.get(processing_centre, None)

        processor_major_version_raw = parse(data[15])
        if 'x' in processor_major_version_raw:
            mphr.processor_major_version = None
        else:
            mphr.processor_major_version = int(processor_major_version_raw)

        processor_minor_version_raw = parse(data[16])
        if 'x' in processor_minor_version_raw:
            mphr.processor_minor_version = None
        else:
            mphr.processor_minor_version = int(processor_minor_version_raw)

        format_major_version_raw = parse(data[17])
        if 'x' in format_major_version_raw:
            mphr.format_major_version = None
        else:
            mphr.format_major_version = int(format_major_version_raw)

        format_minor_version_raw = parse(data[18])
        if 'x' in format_minor_version_raw:
            mphr.format_minor_version = None
        else:
            mphr.format_minor_version = int(format_minor_version_raw)

        mphr.processing_time_start = parse(data[19])

        mphr.processing_time_end = parse(data[20])

        mphr.processing_mode = processing_mode_dict.get(parse(data[21]), None)

        mphr.disposition_mode = disposition_mode_dict.get(parse(data[22]), None)

        mphr.receiving_ground_station = receiving_ground_station_dict.get(parse(data[23]), None)

        mphr.receive_time_start = parse(data[24])

        mphr.receive_time_end = parse(data[25])

        mphr.orbit_start = int(parse(data[26]))

        mphr.orbit_end = int(parse(data[27]))

        mphr.actual_product_size = int(parse(data[28])) * units('bytes')

        mphr.state_vector_time = parse(data[29])

        scale = 1e3
        mphr.semi_major_axis = float(parse(data[30])) / scale * units('m')

        scale = 1e6
        mphr.eccentricity = float(parse(data[31])) / scale

        scale = 1e3
        mphr.inclination = float(parse(data[32])) / scale * units('deg')

        scale = 1e3
        mphr.perigee_argument = float(parse(data[33])) / scale * units('deg')

        scale = 1e3
        mphr.right_ascension = float(parse(data[34])) / scale * units('deg')

        scale = 1e3
        mphr.mean_anomaly = float(parse(data[35])) / scale * units('deg')

        scale = 1e3
        mphr.x_position = float(parse(data[36])) / scale * units('m')

        scale = 1e3
        mphr.y_position = float(parse(data[37])) / scale * units('m')

        scale = 1e3
        mphr.z_position = float(parse(data[38])) / scale * units('m')

        scale = 1e3
        mphr.x_velocity = float(parse(data[39])) / scale * units('m/s')

        scale = 1e3
        mphr.y_velocity = float(parse(data[40])) / scale * units('m/s')

        scale = 1e3
        mphr.z_velocity = float(parse(data[41])) / scale * units('m/s')

        mphr.earth_sun_distance_ratio = float(parse(data[42]))

        mphr.location_tolerance_radial = float(parse(data[43])) * units('m')

        mphr.location_tolerance_crosstrack = float(parse(data[44])) * units('m')

        mphr.location_tolerance_alongtrack = float(parse(data[45])) * units('m')

        scale = 1e3
        mphr.yaw_error = float(parse(data[46])) / scale * units('deg')

        scale = 1e3
        mphr.roll_error = float(parse(data[47])) / scale * units('deg')

        scale = 1e3
        mphr.pitch_error = float(parse(data[48])) / scale * units('deg')

        scale = 1e3
        subsat_latitude_start_raw = parse(data[49])
        if 'x' in subsat_latitude_start_raw:
            mphr.subsat_latitude_start = None
        else:
            mphr.subsat_latitude_start = float(subsat_latitude_start_raw) / scale * units('deg')

        scale = 1e3
        subsat_longitude_start_raw = parse(data[50])
        if 'x' in subsat_longitude_start_raw:
            mphr.subsat_longitude_start = None
        else:
            mphr.subsat_longitude_start = float(subsat_longitude_start_raw) / scale * units('deg')

        scale = 1e3
        subsat_latitude_end_raw = parse(data[51])
        if 'x' in subsat_latitude_end_raw:
            mphr.subsat_latitude_end = None
        else:
            mphr.subsat_latitude_end = float(subsat_latitude_end_raw) / scale * units('deg')

        scale = 1e3
        subsat_longitude_end_raw = parse(data[52])
        if 'x' in subsat_longitude_end_raw:
            mphr.subsat_longitude_end = None
        else:
            mphr.subsat_longitude_end = float(subsat_longitude_end_raw) / scale * units('deg')

        mphr.leap_second = int(parse(data[53]))

        mphr.leap_second_utc = parse(data[54])

        mphr.total_records = int(parse(data[55]))

        mphr.total_mphr = int(parse(data[56]))
        assert mphr.total_mphr == 1

        mphr.total_sphr = int(parse(data[57]))
        assert mphr.total_sphr <= 1

        mphr.total_ipr = int(parse(data[58]))

        mphr.total_geadr = int(parse(data[59]))

        mphr.total_giadr = int(parse(data[60]))

        mphr.total_veadr = int(parse(data[61]))

        mphr.total_viadr = int(parse(data[62]))

        mphr.total_mdr = int(parse(data[62]))

        mphr.count_degraded_inst_mdr = int(parse(data[63]))

        mphr.count_degraded_proc_mdr = int(parse(data[64]))

        mphr.count_degraded_inst_mdr_blocks = int(parse(data[66]))

        mphr.count_degraded_proc_mdr_blocks = int(parse(data[67]))

        mphr.duration_of_product = int(parse(data[68])) * units('ms')

        milliseconds_of_data_present_raw = parse(data[69])
        if 'x' in milliseconds_of_data_present_raw:
            mphr.milliseconds_of_data_present = None
        else:
            mphr.milliseconds_of_data_present = int(milliseconds_of_data_present_raw) * units('ms')

        milliseconds_of_data_missing_raw = parse(data[70])
        if 'x' in milliseconds_of_data_missing_raw:
            mphr.milliseconds_of_data_missing = None
        else:
            mphr.milliseconds_of_data_missing = int(milliseconds_of_data_missing_raw) * units('ms')

        subsetted_product_raw = parse(data[71])
        if subsetted_product_raw == 'T' or subsetted_product_raw == '1':
            mphr.subsetted_product = True
        elif subsetted_product_raw == 'F' or subsetted_product_raw == '0':
            mphr.subsetted_product = False
        else:
            raise ValueError('Invalid value for subsetted product: ' + str(subsetted_product_raw))

        return mphr

    def __str__(self):
        # \(\n\s+(.*)\n\s+\)
        # \(\n\s+(.*)\n\s+(.*)\n\s+(.*)\s+\)
        output = 'Product name:                   ' + str(self.product_name) + '\n'
        output += 'Parent product name 1:          ' + str(self.parent_product_name1) + '\n'
        output += 'Parent product name 2:          ' + str(self.parent_product_name2) + '\n'
        output += 'Parent product name 3:          ' + str(self.parent_product_name3) + '\n'
        output += 'Parent product name 4:          ' + str(self.parent_product_name4) + '\n'
        output += 'Instrument id:                  ' + str(self.instrument_id) + '\n'
        output += 'Instrument model:               ' + str(self.instrument_model) + '\n'
        output += 'Product type:                   ' + str(self.product_type) + '\n'
        output += 'Processing level:               ' + str(self.processing_level) + '\n'
        output += 'Spacecraft id:                  ' + str(self.spacecraft_id) + '\n'
        output += 'Sensing start:                  ' + str(self.sensing_start) + '\n'
        output += 'Sensing end:                    ' + str(self.sensing_end) + '\n'
        output += 'Sensing start theoretical:      ' + str(self.sensing_start_theoretical) + '\n'
        output += 'Sensing end theoretical:        ' + str(self.sensing_end_theoretical) + '\n'
        output += 'Processing centre:              ' + str(self.processing_centre) + '\n'
        output += 'Processor major version:        ' + str(self.processor_major_version) + '\n'
        output += 'Processor minor version:        ' + str(self.processor_minor_version) + '\n'
        output += 'Format major version:           ' + str(self.format_major_version) + '\n'
        output += 'Format minor version:           ' + str(self.format_minor_version) + '\n'
        output += 'Processing time start:          ' + str(self.processing_time_start) + '\n'
        output += 'Processing time end:            ' + str(self.processing_time_end) + '\n'
        output += 'Processing mode:                ' + str(self.processing_mode) + '\n'
        output += 'Disposition mode:               ' + str(self.disposition_mode) + '\n'
        output += 'Receiving ground station:       ' + str(self.receiving_ground_station) + '\n'
        output += 'Receive time start:             ' + str(self.receive_time_start) + '\n'
        output += 'Receive time end:               ' + str(self.receive_time_end) + '\n'
        output += 'Orbit start:                    ' + str(self.orbit_start) + '\n'
        output += 'Orbit end:                      ' + str(self.orbit_end) + '\n'
        output += 'Actual product size:            ' + str(self.actual_product_size) + '\n'
        output += 'State vector time:              ' + str(self.state_vector_time) + '\n'
        output += 'Semi major axis:                ' + str(self.semi_major_axis) + '\n'
        output += 'Eccentricity:                   ' + str(self.eccentricity) + '\n'
        output += 'Inclination:                    ' + str(self.inclination) + '\n'
        output += 'Perigee argument:               ' + str(self.perigee_argument) + '\n'
        output += 'Right ascension:                ' + str(self.right_ascension) + '\n'
        output += 'Mean anomaly:                   ' + str(self.mean_anomaly) + '\n'
        output += 'X position:                     ' + str(self.x_position) + '\n'
        output += 'Y position:                     ' + str(self.y_position) + '\n'
        output += 'Z position:                     ' + str(self.z_position) + '\n'
        output += 'X velocity:                     ' + str(self.x_velocity) + '\n'
        output += 'Y velocity:                     ' + str(self.y_velocity) + '\n'
        output += 'Z velocity:                     ' + str(self.z_velocity) + '\n'
        output += 'Earth sun distance ratio:       ' + str(self.earth_sun_distance_ratio) + '\n'
        output += 'Location tolerance radial:      ' + str(self.location_tolerance_radial) + '\n'
        output += 'Location tolerance crosstrack:  ' + str(self.location_tolerance_crosstrack) + '\n'
        output += 'Location tolerance alongtrack:  ' + str(self.location_tolerance_alongtrack) + '\n'
        output += 'Yaw error:                      ' + str(self.yaw_error) + '\n'
        output += 'Roll error:                     ' + str(self.roll_error) + '\n'
        output += 'Pitch error:                    ' + str(self.pitch_error) + '\n'
        output += 'Subsat latitude start:          ' + str(self.subsat_latitude_start) + '\n'
        output += 'Subsat longitude start:         ' + str(self.subsat_longitude_start) + '\n'
        output += 'Subsat latitude end:            ' + str(self.subsat_latitude_end) + '\n'
        output += 'Subsat longitude end:           ' + str(self.subsat_longitude_end) + '\n'
        output += 'Leap second:                    ' + str(self.leap_second) + '\n'
        output += 'Leap second utc:                ' + str(self.leap_second_utc) + '\n'
        output += 'Total records:                  ' + str(self.total_records) + '\n'
        output += 'Total mphr:                     ' + str(self.total_mphr) + '\n'
        output += 'Total sphr:                     ' + str(self.total_sphr) + '\n'
        output += 'Total ipr:                      ' + str(self.total_ipr) + '\n'
        output += 'Total geadr:                    ' + str(self.total_geadr) + '\n'
        output += 'Total giadr:                    ' + str(self.total_giadr) + '\n'
        output += 'Total veadr:                    ' + str(self.total_veadr) + '\n'
        output += 'Total viadr:                    ' + str(self.total_viadr) + '\n'
        output += 'Total mdr:                      ' + str(self.total_mdr) + '\n'
        output += 'Count degraded inst mdr:        ' + str(self.count_degraded_inst_mdr) + '\n'
        output += 'Count degraded proc mdr:        ' + str(self.count_degraded_proc_mdr) + '\n'
        output += 'Count degraded inst mdr blocks: ' + str(self.count_degraded_inst_mdr_blocks) + '\n'
        output += 'Count degraded proc mdr blocks: ' + str(self.count_degraded_proc_mdr_blocks) + '\n'
        output += 'Duration of product:            ' + str(self.duration_of_product) + '\n'
        output += 'Milliseconds of data present:   ' + str(self.milliseconds_of_data_present) + '\n'
        output += 'Milliseconds of data missing:   ' + str(self.milliseconds_of_data_missing) + '\n'
        output += 'Subsetted product:              ' + str(self.subsetted_product)
        return output
