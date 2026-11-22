# -*- coding: utf-8 -*-
# -.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.#

#* File Name : test_fractal_sound.py
#
#* Purpose :
#
#* Creation Date : 22-11-2026
#
#* Last Modified : Sunday 22 November 2026 01:31:10 PM
#
#* Created By : Yaay Nands
#_._._._._._._._._._._._._._._._._._._._._.#
from pprint import pprint as pp


import numpy as np, soundfile as sf
y, sr = sf.read("./sounds/outputs/fractal_output.wav")
print("NaNs:", np.isnan(y).any(), "| Peak:", np.max(np.abs(y)), "| RMS:", np.sqrt(np.mean(y**2)))
