"""
iasi_nat_reader: An enhanced library to read IASI L1C, L2, and PCC files
Copyright (C) 2024 Ronglian Zhou

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 3.0 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA


- Moved `read_vint` and  `read_short_date` functions to here.
- Simplified names of datatypes
- Created `generic_read` function
"""

from struct import unpack
import numpy as np
from numpy import fromstring


b = '>?'
i1 = '>i1'
i2 = '>i2'
i4 = '>i4'
u1 = '>u1'
u2 = '>u2'
u4 = '>u4'
vi4 = '>vi4'

# it's a performance bottleneck since calling the fromstring too many times (2w+)
# def read_vint(raw_data:bytes, dtype:str):
#     itsz = int(dtype[-1])+1
#     dtype = dtype.replace('v', '')
#     length = len(raw_data)
#     n_elements = length // itsz
#     data = np.zeros((n_elements,), dtype=np.float64)
#     for i, j in enumerate(range(0, length, itsz)):
#         sf = fromstring(raw_data[j:j+1], dtype=i1)[0]
#         data[i] = fromstring(raw_data[j+1:j+itsz], dtype=dtype) / 10.**sf
#     return data


def read_vint(raw_data: bytes, dtype: str) -> np.ndarray:
    itsz = int(dtype[-1])
    dtype = dtype.replace('v', '')
    n_elements = len(raw_data) // (itsz + 1)
    as_uint_data = fromstring(raw_data, dtype=u1).reshape(n_elements, (itsz + 1))
    mantissa = np.zeros((n_elements,), dtype=u4)
    for i in range(1, itsz + 1):
        mantissa += as_uint_data[:, i] * (2 ** (8 * (itsz - i)))
    return mantissa.astype(dtype) / 10.0 ** np.int8(as_uint_data[:, 0])


def read_short_date(raw_data: bytes) -> np.ndarray:
    n_elements = len(raw_data) // 6
    format_string = ">"
    for _ in range(n_elements):
        format_string += "HI"
    unpacked_data = unpack(format_string, raw_data)
    return np.array(unpacked_data, dtype=i4).reshape(n_elements, 2)


def generic_read(
    raw_data: bytes, 
    offset: int, 
    shape: tuple | list, 
    dtype: str, 
    sf: int | None = None
) -> tuple[np.ndarray, int]:
    if '?' in dtype:
        itemsize = 1
    elif 'v' in dtype:
        itemsize = int(dtype[-1]) + 1
    else:
        itemsize = int(dtype[-1])

    increase = np.prod(shape) * itemsize

    if 'v' in dtype:
        tmp = read_vint(raw_data[offset : offset + increase], dtype)
    else:
        tmp = fromstring(raw_data[offset : offset + increase], dtype=dtype)

    if '?' not in dtype and '1' not in dtype:
        if 'i' in dtype:
            tmp = np.where(tmp == -(2 ** (itemsize * 8 - 1)), np.nan, tmp)
        elif 'u' in dtype:
            tmp = np.where(tmp == 2 ** (itemsize * 8) - 1, np.nan, tmp)

    if 'v' not in dtype and np.all(~np.isnan(tmp)):
        tmp = tmp.astype(dtype)

    # if np.all(np.array(shape)==1) or shape[0]==1:
    #     tmp = tmp[0]
    # elif not np.all(np.array(shape)==1):
    #     tmp = tmp.reshape(shape)
    if np.all(np.array(shape) == 1):
        tmp = tmp[0]
    # elif np.any(np.array(shape)==1):
    #     tmp = np.squeeze(tmp)
    else:
        tmp = tmp.reshape(shape)

    offset += increase

    if sf is None:
        return tmp, offset
    else:
        return tmp / 10.0**sf, offset
