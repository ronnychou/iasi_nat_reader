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

Modifications made by ronglian zhou <961836102@qq.com> on <2024/10/18>:
- Uploaded eigenvector files to `data` directory which are necessary
  for reading PC products (now only support products from MetOp B/C)
"""

import os
import sys
from importlib.resources import path
import traceback
import numpy as np
from h5py import File

from .records.giadr import GIADR

class PCC:
    def __init__(self, giadr: GIADR, eig_dir: os.PathLike | None = None) -> None:
        self.get_eig(eig_dir)
        self.giadr = giadr
        self.fc = self.giadr.FirstChannel
        self.sqf = self.giadr.ScoreQuantisationFactor
        self.rqf = self.giadr.ResidualQuantisationFactor
    
    def get_eig(self, eig_dir: os.PathLike | None):
        # if eig_dir is None:
        #     eig_dir = Path(__file__).joinpath('..','..').resolve().joinpath('data')
        self.eig_val = []
        self.eig_vec: list[np.ndarray] = []
        mean = []
        nedr = []
        for i in range(1,4):
            if eig_dir is None:
                fn = path('iasi_nat_reader.data', f'IASI_EV{i}_xx_Mxx')
            else:
                fn = os.path.join(eig_dir, f'IASI_EV{i}_xx_Mxx')
            f = File(fn)
            self.eig_val.append(f['Eigenvalues'][:])
            self.eig_vec.append(f['Eigenvectors'][:])
            mean.append(f['Mean'][:])
            nedr.append(f['Nedr'][:])
        self.mean = np.concatenate(mean)
        self.nedr = np.concatenate(nedr)
        
    def reconstruct_frompcs(self, pcscores: list[np.ndarray]|np.ndarray):
        if isinstance(pcscores, np.ndarray):
            assert pcscores.shape[-1] == 300
            _pcscores = [pcscores[:,:90], pcscores[:,90:-90], pcscores[:,-90:]]
        elif isinstance(pcscores, list):
            _pcscores = pcscores
        try:
            rad_pc = self.mean + np.concatenate([
                self.sqf[0] * (_pcscores[0] @ self.eig_vec[0]),
                self.sqf[1] * (_pcscores[1] @ self.eig_vec[1]),
                self.sqf[2] * (_pcscores[2] @ self.eig_vec[2]),
            ], axis=-1)
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            # to clear frames in Jupyter mode
            traceback.clear_frames(exc_traceback)
            # rad_pc = None
            # gc.collect()
            raise
        rad_pc = self.nedr * rad_pc * 1e5
        return rad_pc
    
    def reconstruct_add_residual_frompcr(self, pcscores: list[np.ndarray] | np.ndarray, residual: np.ndarray):
        fc = self.fc
        try:
            rad_pc = self.reconstruct_frompcs(pcscores) - np.concatenate([
                self.rqf[0] * residual[...,:fc[1]],
                self.rqf[1] * residual[...,fc[1]:fc[2]],
                self.rqf[2] * residual[...,fc[2]:],
            ], axis=-1) * self.nedr * 1e5
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            # to clear frames in Jupyter mode
            traceback.clear_frames(exc_traceback)
            # rad_pc = None
            # gc.collect()
            raise
        return rad_pc

    def compress_topcs(self, rad_l1c: np.ndarray):
        fc = self.fc
        eig_vec = self.eig_vec
        sqf = self.sqf
        mean = self.mean
        nedr = self.nedr
        
        tmp = (rad_l1c*1e-5 / nedr - mean)
        PcScoresB1 = np.round(tmp[...,:fc[1]] @ eig_vec[0].T / sqf[0]).astype(int)
        PcScoresB2 = np.round(tmp[...,fc[1]:fc[2]] @ eig_vec[1].T / sqf[1]).astype(int)
        PcScoresB3 = np.round(tmp[...,fc[2]:] @ eig_vec[2].T / sqf[2]).astype(int)
        return [PcScoresB1, PcScoresB2, PcScoresB3]
    
    def get_residual(self, rad_l1c: np.ndarray, PcScores: list):
        mean = self.mean
        nedr = self.nedr
        sqf = self.sqf
        eig_vec = self.eig_vec
        # suppose that residual = Rrecon - R not R - Rrecon
        residual = mean + np.concatenate([
            sqf[0] * (PcScores[0] @ eig_vec[0]),
            sqf[1] * (PcScores[1] @ eig_vec[1]),
            sqf[2] * (PcScores[2] @ eig_vec[2]),
        ], axis=-1) - rad_l1c*1e-5 / nedr
        return residual
    
    def get_rms(self, residual):
        fc = self.fc
        ResidualRMS = np.round(np.stack([
            rms(residual[...,:fc[1]]),
            rms(residual[...,fc[1]:fc[2]]),
            rms(residual[...,fc[2]:]),
        ], axis=2), 3)
        return ResidualRMS
    
    def encode_rms(self, rms):
        return np.round(rms, 3)
    
    def encode_residual(self, residual):
        fc = self.fc
        rqf = self.rqf
        return np.round(np.concatenate([
            residual[...,:fc[1]] / rqf[0],
            residual[...,fc[1]:fc[2]] / rqf[1],
            residual[...,fc[2]:] / rqf[2],
        ], axis=-1))


def rms(*args, axis=-1):
    if len(args)==1:
        return np.sqrt(np.mean(args[0]**2, axis=axis))
    elif len(args)==2:
        return np.sqrt(np.mean((args[0]-args[1])**2, axis=axis))