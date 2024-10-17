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
- Moved it from elsewhere to here.
- Added more parameters.
"""

AMCO = 100  # Number of columns for AVHR image pixel
AMLI = 100  # Number of lines for AVHRR image pixel
CCD = 2  # Number of corner cube directions
IMCO = 64  # Number of columns for IASi imager pixel
IMLI = 64  # Number of lines for IASI imager pixel
MAXBA = 3600  # Maximum number of samples in one IASI band
NBK = 6  # Number of AVHRR channels
NCL = 7  # Number of classes for FOV sounder analysis
NIM = 28  # Number of samples used to represent the imaginary part of the IASI spectrum
PN = 4  # Number of sounder pixels
S = 8461  # Number of IASI channels
SB = 3  # Number of spectral bands
SGI = 25  # 5 x 5 - Number of pixels of the subgrid imager
SN = 30  # Scan Number
SNOT = 30  # Number of steps for observational target
SS = 8700  # Number of samples in an IASI spectrum
ST = 3  # Number of widths used for holding PC scores
VP = 1  # Number of verification packets per IASI line
