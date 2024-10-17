from setuptools import setup, find_packages

setup(
    name="iasi_nat_reader",
    version="0.1.0",
    description="A library to read native IASI L1C, L2, and PC files",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/ronnychou/iasi_nat_reader",
    author="Ronglian Zhou",
    author_email="961836102@qq.com",
    license="LGPLv3",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.26.4",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.10',
)
