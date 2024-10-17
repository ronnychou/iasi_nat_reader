
# iasi_nat_reader

`iasi_nat_reader` is an upgraded and refactored version of the original [`piasi_reader`](https://github.com/spiani/piasi_reader) library, designed to read and convert IASI (Infrared Atmospheric Sounding Interferometer) files in native format. This new version expands on the functionality of the original project by incorporating support for additional products, including IASI Level 2 (L2) and Principal Component (PC) data.

## Features

- **[IASI Level 1C](https://navigator.eumetsat.int/product/EO:EUM:DAT:METOP:IASIL1C-ALL)**: Continued support for reading and converting IASI L1C files.
- **[IASI Level 2](https://navigator.eumetsat.int/product/EO:EUM:DAT:METOP:IASSND02)**: Added functionality to read and process IASI L2 data products.
- **[IASI Principal Component Scores and Residuals](https://navigator.eumetsat.int/product/EO:EUM:DAT:METOP:IASPCS01)**: Support for reading IASI PCS and PCR products.
- **Record Management**: Simplified handling of records with refactored `BaseRecord` and `Record` classes w.r.t different products.
- **Data Indexing**: Enhanced functionality to read MDR records by specific indices without loading the whole MDRs in the file.
- **Compatibility**: Removed support for Python 2.x, ensuring modern Python 3.x compatibility (at leat 3.10).
- **Improved Block Handling**: Fixed issues with reading incomplete data blocks, ensuring robustness in file handling.

## Installation

### Prerequisites

- Python 3.10
- `numpy`

### Installation via Git

Clone the repository from GitHub:

```bash
git clone https://github.com/ronnychou/iasi_nat_reader.git
```

## Usage

The `iasi_nat_reader` can be used to read IASI L1C, L2, and PC products, providing structured access to metadata and data blocks within the files. Here's a brief overview of how to use the reader:

### Examples

#### Import

```python
from iasi_nat_reader import L1cNativeFile
from iasi_nat_reader import L2NativeFile
from iasi_nat_reader import PCNativeFile
from iasi_nat_reader import PCC
```

#### Open file and load data

```python
idx: None | int | list | slice 
# None: read all MDRs
# int | list | slice: read MDRs by specific indices
l1c_file = L1cNativeFile('path_to_iasi_l1c_file', idx)
l2_file = L2NativeFile('path_to_iasi_l2_file', idx)
pc_file = PCNativeFile('path_to_iasi_pc_file', idx)
```

##### Read physical data

```python
lon = l1c_file.get_longitudes()
lat = l1c_file.get_latitudes()
rad = l1c_file.get_radiances()
cld = l1c_file.get_avhrr_cloud_fractions()

# or use `with` to automatically free memory
with L1cNativeFile('path_to_iasi_l1c_file') as l1c_file:
    rad = l1c_file.get_radiances()
```

#### Query what variables are in MDR

```python
dir(l1c_file.get_mdrs()[0])
```

## Changelog

### Version 0.1.0 - 2024/10/17

- **Refactored Project Structure**: Moved multiple functions and classes to more logical locations to improve code readability and maintainability.
- **L2 and PC Support**: Added new modules and classes to support IASI L2 and PC data products.
- **Improved Record Reading**: Introduced a feature to allow reading records by specific index or indices.
- **Bug Fixes**: Fixed issues related to reading incomplete data blocks.
- **Python 3.x Compatibility**: Removed legacy support for Python 2.x.

## References

- [`piasi_reader`](https://github.com/spiani/piasi_reader)
- [IASI Level 1 Product Guide](https://user.eumetsat.int/s3/eup-strapi-media/pdf_iasi_pg_487c765315.pdf)
- [IASI Level 1 Product Format Specification](https://user.eumetsat.int/s3/eup-strapi-media/pdf_iasi_level_1_pfs_2105bc9ccf.pdf)
- [IASI Level 2 Product Guide](https://user.eumetsat.int/s3/eup-strapi-media/IASI_Level_2_Product_Guide_8f61a2369f.pdf)
- [IASI Level 2 Product Format Specification](https://user.eumetsat.int/s3/eup-strapi-media/pdf_ten_980760_eps_iasi_l2_f9511c26d2.pdf)
