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

from __future__ import print_function, division
import gc
import numpy as np
from os.path import getsize
from datetime import datetime, timedelta

from ..generic.mphr import MPHR
from .records import *


class MphrNotFoundException(Exception):
    """A error that happens if the file do not has a MPHR"""

    pass


class GiadrNotFoundException(Exception):
    """A error that happens if the file do not has a GIADR"""

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
        self.__size = getsize(filename)
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

    def get_giadr(self) -> GIADR:
        """
        Return the record with the GIADR of the file.

        Returns:
            An object of the Record class
        """

        giadr_records = [rcd for rcd in self.__record_list if rcd.type == 'GIADR']
        if len(giadr_records) == 0:
            raise GiadrNotFoundException
        return giadr_records[0].content

    def get_mdrs(self) -> list[MDR]:
        """
        Return a list of all the records of mdr type

        Returns:
            A list of record objects
        """
        return [r.content for r in self.__record_list if r.type == "MDR"]

    def read_mdrs(self, idx: int | slice = None):
        mdr_record_positions = [
            i for i in range(self.n_of_records) if self.__record_list[i].type == 'MDR'
        ]
        firstpos = mdr_record_positions[0]
        giadr = self.get_giadr()
        if idx is not None:
            if isinstance(idx, int):
                mdr_record_positions = [mdr_record_positions[idx]]
            elif isinstance(idx, slice):
                mdr_record_positions = mdr_record_positions[idx]
        for i in mdr_record_positions:
            print(f'mdr pos {i-firstpos:03d} (rel) {i:03d} (abs)', end='\r')
            mdr_record = self.__record_list[i]
            if (
                mdr_record.grh.record_subclass_version != 4
                or mdr_record.grh.record_size <= 207747
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

    def get_latitudes(self, scan_pos: slice | int = slice(None, None)) -> np.ndarray:
        """
        Return a numpy array with all the latitudes read from all the records
        of the file.
        """
        return np.concatenate([mdr.EARTH_LOCATION[:, 0][scan_pos] for mdr in self.mdrs])

    def get_longitudes(self, scan_pos: slice | int = slice(None, None)) -> np.ndarray:
        """
        Return a numpy array with all the longitudes read from all the records
        of the file.
        """
        return np.concatenate([mdr.EARTH_LOCATION[:, 1][scan_pos] for mdr in self.mdrs])

    def get_sat_zenith_angles(
        self, scan_pos: slice | int = slice(None, None)
    ) -> np.ndarray:
        """
        Return an array with all the angles read from all the records
        of the file.
        """
        return np.concatenate(
            [mdr.ANGULAR_RELATION[:, 1][scan_pos] for mdr in self.mdrs]
        )

    def get_sat_azimuth_angles(
        self, scan_pos: slice | int = slice(None, None)
    ) -> np.ndarray:
        """
        Return an array with all the angles read from all the records
        of the file.
        """
        return np.concatenate(
            [mdr.ANGULAR_RELATION[:, 3][scan_pos] for mdr in self.mdrs]
        )

    def get_sun_zenith_angles(
        self, scan_pos: slice | int = slice(None, None)
    ) -> np.ndarray:
        """
        Return an array with all the angles read from all the records
        of the file.
        """
        return np.concatenate(
            [mdr.ANGULAR_RELATION[:, 0][scan_pos] for mdr in self.mdrs]
        )

    def get_sun_azimuth_angles(
        self, scan_pos: slice | int = slice(None, None)
    ) -> np.ndarray:
        """
        Return an array with all the angles read from all the records
        of the file.
        """
        return np.concatenate(
            [mdr.ANGULAR_RELATION[:, 2][scan_pos] for mdr in self.mdrs]
        )

    def get_fractional_cloud_cover(
        self, scan_pos: slice | int = slice(None, None)
    ) -> np.ndarray:
        """
        Return a numpy array with all the fractional cloud cover read from all the records
        of the file.
        """
        return np.concatenate(
            [mdr.FRACTIONAL_CLOUD_COVER[scan_pos] for mdr in self.mdrs], axis=0
        )

    def get_cloud_top_temperature(
        self, scan_pos: slice | int = slice(None, None)
    ) -> np.ndarray:
        """
        Return an array with all the cloud top temperature read from all the records
        of the file.
        """
        return np.concatenate(
            [mdr.CLOUD_TOP_TEMPERATURE[scan_pos] for mdr in self.mdrs], axis=0
        )

    def get_cloud_top_pressure(
        self, scan_pos: slice | int = slice(None, None)
    ) -> np.ndarray:
        """
        Return an array with all the cloud top pressure read from all the records
        of the file.
        """
        return np.concatenate(
            [mdr.CLOUD_TOP_PRESSURE[scan_pos] for mdr in self.mdrs], axis=0
        )

    def get_cloudmask(self, scan_pos: slice | int = slice(None, None)) -> np.ndarray:
        """
        Return an array with all the cloud mask read from all the records
        of the file.

        Ref: iasi_l1_product_guide_v5.pdf P56
        """
        return np.concatenate([mdr.FLG_CLDNES[scan_pos] for mdr in self.mdrs])

    def get_aero_dect(self, scan_pos: slice | int = slice(None, None)) -> np.ndarray:
        return np.concatenate([mdr.FLG_DUSTCLD[scan_pos] for mdr in self.mdrs])

    def get_temp_profiles(
        self, scan_pos: slice | int = slice(None, None)
    ) -> np.ndarray:
        return np.concatenate(
            [mdr.ATMOSPHERIC_TEMPERATURE[scan_pos] for mdr in self.mdrs], axis=0
        )

    def get_wv_profiles(self, scan_pos: slice | int = slice(None, None)) -> np.ndarray:
        return np.concatenate(
            [mdr.ATMOSPHERIC_WATER_VAPOUR[scan_pos] for mdr in self.mdrs], axis=0
        )

    def get_ozone_profiles(
        self, scan_pos: slice | int = slice(None, None)
    ) -> np.ndarray:
        return np.concatenate(
            [mdr.ATMOSPHERIC_OZONE[scan_pos] for mdr in self.mdrs], axis=0
        )

    def get_integrated(self, scan_pos: slice | int = slice(None, None)) -> np.ndarray:
        int_wv = np.concatenate(
            [mdr.INTEGRATED_WATER_VAPOUR[scan_pos] for mdr in self.mdrs], axis=0
        )
        int_o3 = np.concatenate(
            [mdr.INTEGRATED_OZONE[scan_pos] for mdr in self.mdrs], axis=0
        )
        int_n2o = np.concatenate(
            [mdr.INTEGRATED_N2O[scan_pos] for mdr in self.mdrs], axis=0
        )
        int_co = np.concatenate(
            [mdr.INTEGRATED_CO[scan_pos] for mdr in self.mdrs], axis=0
        )
        int_ch4 = np.concatenate(
            [mdr.INTEGRATED_CH4[scan_pos] for mdr in self.mdrs], axis=0
        )
        int_co2 = np.concatenate(
            [mdr.INTEGRATED_CO2[scan_pos] for mdr in self.mdrs], axis=0
        )
        return np.stack([int_wv, int_o3, int_n2o, int_co, int_ch4, int_co2], axis=1)

    def get_surface_temperature(
        self, scan_pos: slice | int = slice(None, None)
    ) -> np.ndarray:
        return np.concatenate([mdr.SURFACE_TEMPERATURE[scan_pos] for mdr in self.mdrs])

    def get_surface_pressure(
        self, scan_pos: slice | int = slice(None, None)
    ) -> np.ndarray:
        return np.concatenate([mdr.SURFACE_PRESSURE[scan_pos] for mdr in self.mdrs])

    def get_surface_emissivity(
        self, scan_pos: slice | int = slice(None, None)
    ) -> np.ndarray:
        return np.concatenate(
            [mdr.SURFACE_EMISSIVITY[scan_pos] for mdr in self.mdrs], axis=0
        )

    def get_integrated_water_vapor(
        self, scan_pos: slice | int = slice(None, None)
    ) -> np.ndarray:
        return np.concatenate(
            [mdr.INTEGRATED_WATER_VAPOUR[scan_pos] for mdr in self.mdrs], axis=0
        )

    def get_landsea(self, scan_pos: slice | int = slice(None, None)) -> np.ndarray:
        return np.concatenate([mdr.FLG_LANSEA[scan_pos] for mdr in self.mdrs])

    def get_surface_elevation(
        self, scan_pos: slice | int = slice(None, None)
    ) -> np.ndarray:
        return np.concatenate([mdr.SURFACE_Z[scan_pos] for mdr in self.mdrs])

    def get_sunglint(self, scan_pos: slice | int = slice(None, None)) -> np.ndarray:
        return np.concatenate([mdr.FLG_SUNGLNT[scan_pos] for mdr in self.mdrs])

    def get_time(self, scan_pos: slice | int = slice(None, None)) -> np.ndarray:
        return np.concatenate(
            [
                datetime(2000, 1, 1)
                + timedelta(days=rcd.grh.record_start_time_day)
                + timedelta(milliseconds=rcd.grh.record_start_time_msec)
                for rcd in self.__record_list
                if rcd.type == 'MDR'
            ]
        )

    def get_quality_flag(self, scan_pos: slice | int = slice(None, None)) -> np.ndarray:
        # flag_amsubad = np.concatenate([mdr.FLG_AMSUBAD for mdr in self.mdrs])
        # flag_avhrrbad = np.concatenate([mdr.FLG_AVHRRBAD for mdr in self.mdrs])
        flag_iasibad = np.concatenate([mdr.FLG_IASIBAD[scan_pos] for mdr in self.mdrs])
        flag_cldnes = np.concatenate([mdr.FLG_CLDNES[scan_pos] for mdr in self.mdrs])
        flag_dustcld = np.concatenate([mdr.FLG_DUSTCLD[scan_pos] for mdr in self.mdrs])
        # flag_fgcheck = np.concatenate([mdr.FLG_FGCHECK[scan_pos] for mdr in self.mdrs])
        flag_retcheck = np.concatenate(
            [mdr.FLG_RETCHECK[scan_pos] for mdr in self.mdrs]
        )
        flag_physcheck = np.concatenate(
            [mdr.FLG_PHYSCHECK[scan_pos] for mdr in self.mdrs]
        )
        flag_landsea = np.concatenate([mdr.FLG_LANSEA[scan_pos] for mdr in self.mdrs])
        flag_itconv = np.concatenate([mdr.FLG_ITCONV[scan_pos] for mdr in self.mdrs])
        flag_thicir = np.concatenate([mdr.FLG_THICIR[scan_pos] for mdr in self.mdrs])
        return (
            # (flag_amsubad==0) &
            # (flag_avhrrbad==0) &
            (flag_iasibad == 0)
            & (flag_cldnes == 1)
            & (flag_dustcld < 2)
            & (flag_itconv == 5)
            & (flag_physcheck == 0)
            & (flag_retcheck == 0)
            & (flag_thicir == 0)
            & ((flag_landsea == 0) | (flag_landsea == 1) | (flag_landsea == 3))
        )

    def get_nerror(self, scan_pos: slice | int = slice(None, None)) -> np.ndarray:
        """
        Get number of FOV for current scan line which has error covariance
        """
        return np.array([mdr.NERR[scan_pos] for mdr in self.mdrs])

    def get_error_idx(self, scan_pos: slice | int = slice(None, None)) -> np.ndarray:
        """
        Get index of FOV for current scan line which has error covariance
        255 for N/A
        """
        err_idx = np.concatenate([mdr.ERROR_DATA_INDEX[scan_pos] for mdr in self.mdrs])
        err_idx = np.where(err_idx != 255, True, err_idx)
        err_idx = np.where(err_idx == 255, False, err_idx)
        err_idx = err_idx.astype(bool)
        return err_idx
