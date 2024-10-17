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


Support for printing MPHR friendly
"""


class UnitVariable:
    def __init__(self, magnitude: int | float, units: str) -> None:
        self.magnitude = magnitude
        self.units = units

    def __repr__(self) -> str:
        return f'{self.magnitude} {self.units}'


class units:
    def __init__(self, units) -> None:
        self.units = units

    def __mul__(self, other: int | float):
        if isinstance(other, (int, float)):
            return UnitVariable(other, self.units)
        else:
            raise TypeError("Multiplication is only supported with int or float.")

    def __rmul__(self, other):
        return self.__mul__(other)
