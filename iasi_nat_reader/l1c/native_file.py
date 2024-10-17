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
- Added functionality that reading record(s) by the specific index (or indices) to NativeFile class.
- Fixed the bug when reading incomplete blocks occured.
"""

from __future__ import print_function, division
import gc
import numpy as np
import os

from ..generic.mphr import MPHR
from .records import *


class MphrNotFoundException(Exception):
    """A error that happens if the file do not has a MPHR"""

    pass


class GiadrQualityNotFoundException(Exception):
    """A error that happens if the file do not has a GIADR quality"""

    pass


class GiadrScalefactorsNotFoundException(Exception):
    """A error that happens if the file do not has a GIADR scalefactor"""

    pass


class NotSoManyRecordsException(ValueError):
    """
    This error is raised if something tries to access to a record whose
    number is greater than the total number of records
    """

    pass


class TooSmallThresholdException(ValueError):
    pass


class NativeFile:
    def __init__(self, filename, mdr_record_idx: int | list | slice = None):
        self.__fn = filename
        self.__record_list: list[Record] = []
        self.__size = os.path.getsize(filename)
        self.__data_read = False

        # Read content from the file
        bytes_read = 0
        with open(filename, 'rb') as iasi_file:
            while bytes_read < self.__size:
                rcd = Record.read(iasi_file)
                self.__record_list.append(rcd)
                bytes_read += rcd.size

        if mdr_record_idx is not None:
            i = 0
            while True:
                if self.__record_list[i].type == 'MDR':
                    break
                i += 1
            header = self.__record_list[:i]
            main = self.__record_list[i:]

            if isinstance(mdr_record_idx, int):
                main = [main[mdr_record_idx]]
            elif isinstance(mdr_record_idx, list):
                main = [
                    element
                    for index, element in enumerate(main)
                    if index in mdr_record_idx
                ]
            elif isinstance(mdr_record_idx, slice):
                rng = range(mdr_record_idx.start, mdr_record_idx.stop)
                main = [element for index, element in enumerate(main) if index in rng]
            self.__record_list = [*header, *main]

        self.read_mdrs()

    def __enter__(self) -> 'NativeFile':
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.close()

    def close(self):
        self.__record_list = None
        self.mdrs = None
        gc.collect()

    @property
    def size(self):
        """
        An integer which is the size of the file in bytes
        """
        return self.__size

    @property
    def n_of_records(self):
        """
        An integer which is the number of the records saved in the file
        """
        return len(self.__record_list)

    def get_record(self, i):
        """
        Return the i-th record saved inside the file

        Args:
            - *i*: an integer between 0 and n_of_records

        Returns:
            An object of the Record class
        """

        if i >= self.n_of_records:
            raise NotSoManyRecordsException
        return self.__record_list[i]

    def get_mphr(self) -> MPHR:
        """
        Return the record with the mphr of the file.

        Returns:
            An object of the Record class
        """

        mphr_records = [rcd for rcd in self.__record_list if rcd.type == 'MPHR']
        if len(mphr_records) == 0:
            raise MphrNotFoundException
        return mphr_records[0].content

    def get_giadr_quality(self) -> GIADR_quality:
        """
        Return the record with the GIADR quality of the file.

        Returns:
            An object of the Record class
        """

        giadr_records = [
            rcd
            for rcd in self.__record_list
            if rcd.type == 'GIADR' and rcd.grh.record_subclass == 0
        ]
        if len(giadr_records) == 0:
            raise GiadrQualityNotFoundException
        return giadr_records[0].content

    def get_giadr_scalefactors(self) -> GIADR_scale_factors:
        """
        Return the record with the GIADR scalefactors of the file.

        Returns:
            An object of the Record class
        """

        giadr_records = [
            rcd
            for rcd in self.__record_list
            if rcd.type == 'GIADR' and rcd.grh.record_subclass == 1
        ]
        if len(giadr_records) == 0:
            raise GiadrScalefactorsNotFoundException
        return giadr_records[0].content

    def get_mdrs(self) -> list[MDR]:
        """
        Return a list of all the records of mdr type

        Returns:
            A list of record objects
        """
        return [r.content for r in self.__record_list if r.type == "MDR"]

    def read_mdrs(self):
        mdr_record_positions = [
            i for i in range(self.n_of_records) if self.__record_list[i].type == 'MDR'
        ]
        firstpos = mdr_record_positions[0]
        giadr = self.get_giadr_scalefactors()
        for i in mdr_record_positions:
            print(f'mdr pos {i-firstpos:03d} (rel) {i:03d} (abs)', end='\r')
            mdr_record = self.__record_list[i]
            if (
                mdr_record.grh.record_subclass_version not in (4, 5)
                or mdr_record.grh.record_size == 21
            ):
                mdr_record.grh._GRH__record_class = 9
                print(
                    'anormal mdr at {} (rel) {} (abs) : sub class version = {}, record size = {}\nfilename = {}'.format(
                        i - firstpos,
                        i,
                        mdr_record.grh.record_subclass_version,
                        mdr_record.grh.record_size,
                        self.__fn,
                    )
                )
                new_content = 'bad'
            else:
                new_content = MDR.read(mdr_record, giadr)
            self.__record_list[i] = Record(mdr_record.grh, new_content)
        print()
        self.__data_read = True
        self.mdrs: list[MDR] = [
            r.content for r in self.__record_list if r.type == "MDR"
        ]

    def split(
        self, threshold, split_files_names='split_$F', output_dir='.', temp_name='temp'
    ):
        # Get the size of the non-mdr part of the file
        non_mdr_list = [r for r in self if r.type != 'MDR']
        non_mdr_size = sum([r.size for r in non_mdr_list])

        # Get the size of the biggest mdr record
        mdr_list = [r for r in self if r.type == 'MDR']
        msr_max_size = max([r.size for r in mdr_list])

        if threshold < non_mdr_size + msr_max_size:
            raise TooSmallThresholdException(
                'The file can not be splitted in the ' 'desidered size'
            )
        split_file_index = 0
        file_times = []

        # Prepare the first file
        file_size = 0
        current_file = open(os.path.join(output_dir, temp_name), 'w')
        for r in non_mdr_list:
            current_file.write(r.raw)
            file_size += r.size

        for mdr_record in mdr_list:
            if file_size + mdr_record.size > threshold:
                current_file.close()
                file_start_time = min(file_times)
                file_end_time = max(file_times)

                file_name = split_files_names.replace('$F', str(split_file_index))
                file_name = file_name.replace(
                    '$SD', file_start_time.strftime('%Y%m%d%H%M%S') + 'Z'
                )
                file_name = file_name.replace(
                    '$ED', file_end_time.strftime('%Y%m%d%H%M%S') + 'Z'
                )
                os.rename(
                    os.path.join(output_dir, temp_name),
                    os.path.join(output_dir, file_name),
                )
                file_size = 0
                file_times = []
                split_file_index += 1
                current_file = open(os.path.join(output_dir, temp_name), 'w')
                for r in non_mdr_list:
                    current_file.write(r.raw)
                    file_size += r.size

            interpreted_mdr = MDR.read(
                mdr_record.content.raw, self.get_giadr_scalefactors()
            )
            file_times.extend(interpreted_mdr.get_times())
            current_file.write(mdr_record.raw)
            file_size += mdr_record.size

        current_file.close()
        file_start_time = min(file_times)
        file_end_time = max(file_times)
        file_name = split_files_names.replace('$F', str(split_file_index))
        file_name = file_name.replace(
            '$SD', file_start_time.strftime('%Y%m%d%H%M%S') + 'Z'
        )
        file_name = file_name.replace(
            '$ED', file_end_time.strftime('%Y%m%d%H%M%S') + 'Z'
        )
        os.path.join(
            os.path.join(output_dir, temp_name), os.path.join(output_dir, file_name)
        )

    def __iter__(self):
        return self.__record_list.__iter__()

    def get_dgd_flag(self):
        dgd_inst_flag = np.array(
            [mdr.DEGRADED_INST_MDR for mdr in self.mdrs], dtype=np.uint8
        )  # True for bad
        dgd_proc_flag = np.array(
            [mdr.DEGRADED_PROC_MDR for mdr in self.mdrs], dtype=np.uint8
        )  # True for bad
        return dgd_inst_flag, dgd_proc_flag

    def get_latitudes(self) -> np.ndarray:
        """
        Return a numpy array with all the latitudes read from all the records
        of the file.
        """
        latitudes_list = [mdr.GGeoSondLoc[:, :, 1] for mdr in self.mdrs]
        return np.concatenate(latitudes_list).flatten()

    def get_longitudes(self) -> np.ndarray:
        """
        Return a numpy array with all the longitudes read from all the records
        of the file.
        """
        longitudes_list = [mdr.GGeoSondLoc[:, :, 0] for mdr in self.mdrs]
        return np.concatenate(longitudes_list).flatten()

    def get_radiances(self) -> np.ndarray:
        """
        Return a numpy array with all the radiances read from all the records
        of the file.
        """
        radiances_list = [mdr.GS1cSpect.reshape(120, -1) for mdr in self.mdrs]
        return np.concatenate(radiances_list)

    def get_sat_zenith_angles(self) -> np.ndarray:
        """
        Return an array with all the satellite zenith angles read from all the records
        of the file.
        """
        zenith_angles_list = [mdr.GGeoSondAnglesMETOP[:, :, 0] for mdr in self.mdrs]
        return np.concatenate(zenith_angles_list).flatten()

    def get_sat_azimuth_angles(self) -> np.ndarray:
        """
        Return an array with all the satellite azimuth angles read from all the records
        of the file.
        """
        azimuth_angles_list = [mdr.GGeoSondAnglesMETOP[:, :, 1] for mdr in self.mdrs]
        return np.concatenate(azimuth_angles_list).flatten()

    def get_solar_zenith_angles(self) -> np.ndarray:
        """
        Return an array with all the solar zenith angles read from all the records
        of the file.
        """
        solar_zenith_angles_list = [mdr.GGeoSondAnglesSUN[:, :, 0] for mdr in self.mdrs]
        return np.concatenate(solar_zenith_angles_list).flatten()

    def get_solar_azimuth_angles(self) -> np.ndarray:
        """
        Return an array with all the solar azimuth angles read from all the records
        of the file.
        """
        solar_azimuth_angles_list = [
            mdr.GGeoSondAnglesSUN[:, :, 1] for mdr in self.mdrs
        ]
        return np.concatenate(solar_azimuth_angles_list).flatten()

    def get_avhrr_cloud_fractions(self) -> np.ndarray:
        """
        Return an array with all the avhrr cloud fractions read from all the records
        of the file.
        """
        avhrr_cloud_fraction_list = [mdr.GEUMAvhrr1BCldFrac for mdr in self.mdrs]
        return np.concatenate(avhrr_cloud_fraction_list).flatten()

    def get_land_fractions(self) -> np.ndarray:
        """
        Return an array with all the land fractions read from all the records
        of the file.
        """
        avhrr_land_fraction_list = [mdr.GEUMAvhrr1BLandFrac for mdr in self.mdrs]
        return np.concatenate(avhrr_land_fraction_list).flatten()

    def get_date_day(self) -> np.ndarray:
        """
        Return an array with all the days read from all the records
        of the file.
        """
        date_day_list = [mdr.GEPSDatIasi[:, 0] for mdr in self.mdrs]
        return np.repeat(np.concatenate(date_day_list), 4)

    def get_date_msec(self) -> np.ndarray:
        """
        Return an array with all the milliseconds read from all the records
        of the file.
        """
        date_msec_list = [mdr.GEPSDatIasi[:, 1] for mdr in self.mdrs]
        return np.repeat(np.concatenate(date_msec_list), 4)

    def get_obs_times(self) -> np.ndarray:
        """
        Combine together the date_msec and the date_day array and return
        an array of datetime64 objects that represent the time when the
        observations have been collected
        """
        msec = self.get_date_msec().astype(np.int64)
        days = self.get_date_day().astype(np.int64)

        msec.dtype = 'timedelta64[ms]'
        days.dtype = 'timedelta64[D]'

        start_time = np.datetime64('2000-01-01T00:00:00')

        return start_time + days + msec

    def get_channels(self) -> np.ndarray:
        return np.linspace(645, 2760, 8461)
