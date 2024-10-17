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

from __future__ import print_function, division
import gc
from os.path import getsize
import numpy as np

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


class VariableNotFound(ValueError):
    def __init__(self, flag):
        self.flag = flag

    def __str__(self):
        return f"{self.flag} file do not have this variable"


class NativeFile:
    def __init__(self, filename, mdr_record_idx: int | list | slice = None):
        if 'PCS' in filename:
            self.mdr_flag = 'PCS'
        elif 'PCR' in filename:
            self.mdr_flag = 'PCR'
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

    def get_record(self, i) -> Record:
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

    def get_mdrs(self) -> list[MDR_PCS | MDR_PCR]:
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
        giadr = self.get_giadr()
        if self.mdr_flag == 'PCS':
            MDR = MDR_PCS
        elif self.mdr_flag == 'PCR':
            MDR = MDR_PCR
        for i in mdr_record_positions:
            print(f'mdr pos {i-firstpos:03d} (rel) {i:03d} (abs)', end='\r')
            mdr_record = self.__record_list[i]
            if (
                mdr_record.grh.record_subclass_version != 1
                or mdr_record.grh.record_size < 122094
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
        self.mdrs: list[MDR_PCS | MDR_PCR] = [
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
        if self.mdr_flag == 'PCS':
            latitudes_list = [mdr.GGeoSondLoc[:, :, 1] for mdr in self.mdrs]
            return np.concatenate(latitudes_list).flatten()
        elif self.mdr_flag == 'PCR':
            VariableNotFound(self.mdr_flag)

    def get_longitudes(self, scan_pos: slice | int = slice(None, None)) -> np.ndarray:
        """
        Return a numpy array with all the longitudes read from all the records
        of the file.
        """
        if self.mdr_flag == 'PCS':
            longitudes_list = [mdr.GGeoSondLoc[:, :, 0] for mdr in self.mdrs]
            return np.concatenate(longitudes_list).flatten()
        elif self.mdr_flag == 'PCR':
            VariableNotFound(self.mdr_flag)

    def get_qcflag(self, scan_pos: slice | int = slice(None, None)) -> np.ndarray:
        return np.concatenate(
            [mdr.GQisFlagQual for mdr in self.mdrs], dtype=np.uint8
        )  # True for bad

    def get_sat_zenith_angles(
        self, scan_pos: slice | int = slice(None, None)
    ) -> np.ndarray:
        """
        Return an array with all the angles read from all the records
        of the file.
        """
        if self.mdr_flag == 'PCS':
            zenith_angles_list = [mdr.GGeoSondAnglesMETOP[:, :, 0] for mdr in self.mdrs]
            return np.concatenate(zenith_angles_list).flatten()
        elif self.mdr_flag == 'PCR':
            VariableNotFound(self.mdr_flag)

    def get_sat_azimuth_angles(
        self, scan_pos: slice | int = slice(None, None)
    ) -> np.ndarray:
        """
        Return an array with all the angles read from all the records
        of the file.
        """
        if self.mdr_flag == 'PCS':
            azimuth_angles_list = [
                mdr.GGeoSondAnglesMETOP[:, :, 1] for mdr in self.mdrs
            ]
            return np.concatenate(azimuth_angles_list).flatten()
        elif self.mdr_flag == 'PCR':
            VariableNotFound(self.mdr_flag)

    def get_sun_zenith_angles(
        self, scan_pos: slice | int = slice(None, None)
    ) -> np.ndarray:
        """
        Return an array with all the angles read from all the records
        of the file.
        """
        if self.mdr_flag == 'PCS':
            solar_zenith_angles_list = [
                mdr.GGeoSondAnglesSUN[:, :, 0] for mdr in self.mdrs
            ]
            return np.concatenate(solar_zenith_angles_list).flatten()
        elif self.mdr_flag == 'PCR':
            VariableNotFound(self.mdr_flag)

    def get_sun_azimuth_angles(
        self, scan_pos: slice | int = slice(None, None)
    ) -> np.ndarray:
        """
        Return an array with all the angles read from all the records
        of the file.
        """
        if self.mdr_flag == 'PCS':
            solar_azimuth_angles_list = [
                mdr.GGeoSondAnglesSUN[:, :, 1] for mdr in self.mdrs
            ]
            return np.concatenate(solar_azimuth_angles_list).flatten()
        elif self.mdr_flag == 'PCR':
            raise VariableNotFound(self.mdr_flag)

    def get_avhrr_cloud_fractions(
        self, scan_pos: slice | int = slice(None, None)
    ) -> np.ndarray:
        """
        Return an array with all the avhrr cloud fractions read from all the records
        of the file.

        Ref: iasi_l1_product_guide_v5.pdf P92
        """
        if self.mdr_flag == 'PCS':
            avhrr_cloud_fraction_list = [mdr.GEUMAvhrr1BCldFrac for mdr in self.mdrs]
            return np.concatenate(avhrr_cloud_fraction_list).flatten()
        elif self.mdr_flag == 'PCR':
            raise VariableNotFound(self.mdr_flag)

    def get_land_fractions(
        self, scan_pos: slice | int = slice(None, None)
    ) -> np.ndarray:
        """
        Return an array with all the land fractions read from all the records
        of the file.

        Ref: iasi_l1_product_guide_v5.pdf P92
        """
        if self.mdr_flag == 'PCS':
            avhrr_land_fraction_list = [mdr.GEUMAvhrr1BLandFrac for mdr in self.mdrs]
            return np.concatenate(avhrr_land_fraction_list).flatten()
        elif self.mdr_flag == 'PCR':
            raise VariableNotFound(self.mdr_flag)

    def get_date_day(self, scan_pos: slice | int = slice(None, None)) -> np.ndarray:
        """
        Ref: iasi_l1_product_guide_v5.pdf P55
        """
        if self.mdr_flag == 'PCS':
            date_day_list = [mdr.GEPSDatIasi[:, 0] for mdr in self.mdrs]
            return np.repeat(np.concatenate(date_day_list), 4)
        elif self.mdr_flag == 'PCR':
            raise VariableNotFound(self.mdr_flag)

    def get_date_msec(self, scan_pos: slice | int = slice(None, None)) -> np.ndarray:
        """
        Ref: iasi_l1_product_guide_v5.pdf P55
        """
        if self.mdr_flag == 'PCS':
            date_msec_list = [mdr.GEPSDatIasi[:, 1] for mdr in self.mdrs]
            return np.repeat(np.concatenate(date_msec_list), 4)
        elif self.mdr_flag == 'PCR':
            raise VariableNotFound(self.mdr_flag)

    def get_obs_times(self, scan_pos: slice | int = slice(None, None)) -> np.ndarray:
        """
        Combine together the date_msec and the date_day array and return
        an array of datetime64 objects that represent the time when the
        observations have been collected
        """
        if self.mdr_flag == 'PCS':
            msec = self.get_date_msec().astype(np.int64)
            days = self.get_date_day().astype(np.int64)

            msec.dtype = 'timedelta64[ms]'
            days.dtype = 'timedelta64[D]'

            start_time = np.datetime64('2000-01-01T00:00:00')

            return start_time + days + msec
        elif self.mdr_flag == 'PCR':
            raise VariableNotFound(self.mdr_flag)

    def get_pcscores(self, scan_pos: slice | int = slice(None, None)) -> np.ndarray:
        if self.mdr_flag == 'PCS':
            PcScoresB1 = np.concatenate(
                [
                    np.concatenate(
                        [mdr.PcScoresB1P1, mdr.PcScoresB1P2, mdr.PcScoresB1P3], axis=-1
                    ).reshape(120, -1)[scan_pos]
                    for mdr in self.mdrs
                ],
                axis=0,
            )
            PcScoresB2 = np.concatenate(
                [
                    np.concatenate(
                        [mdr.PcScoresB2P1, mdr.PcScoresB2P2, mdr.PcScoresB2P3], axis=-1
                    ).reshape(120, -1)[scan_pos]
                    for mdr in self.mdrs
                ],
                axis=0,
            )
            PcScoresB3 = np.concatenate(
                [
                    np.concatenate(
                        [mdr.PcScoresB3P1, mdr.PcScoresB3P2, mdr.PcScoresB3P3], axis=-1
                    ).reshape(120, -1)[scan_pos]
                    for mdr in self.mdrs
                ],
                axis=0,
            )
            PcScores = [PcScoresB1, PcScoresB2, PcScoresB3]
            return np.concatenate(PcScores, axis=-1)
        elif self.mdr_flag == 'PCR':
            raise VariableNotFound(self.mdr_flag)

    def get_residual(self, scan_pos: slice | int = slice(None, None)) -> np.ndarray:
        if self.mdr_flag == 'PCS':
            raise VariableNotFound(self.mdr_flag)
        elif self.mdr_flag == 'PCR':
            return np.concatenate(
                [mdr.PccResidual.reshape(120, -1)[scan_pos] for mdr in self.mdrs]
            )

    def get_channels(self) -> np.ndarray:
        return np.linspace(645, 2760, 8461)
