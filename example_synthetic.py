import numpy as np
from .synthetic_data.synthetic_data import SyntheticData
from .psf.psf import PSF
from .util.timedependence import convolve_fft
from .util.deconvolution import Deconvolution
import tifffile as tf
import os
import json

savepath = "your/path/here/"
savepath_noisy = savepath + 'noisy/'
savepath_decon = savepath + 'deconvolved/'

# synthetic data parameters
size = 200
frames = 50
spotsize = 1
numpoints = 50
motion = 3
brightness = 0.2

# noise parameters
p = 0.01
g = 0.0005

# deconvolution parameters
l = 0.1
lt = 0.1
eps = 0.001
maxit = 1

# create synthetic data
sd_params = dict(size=size, frames=frames, spotsize=spotsize, numpoints=numpoints, motion=motion, brightness=brightness)
SD = SyntheticData(**sd_params)
psf_params = dict(type='widefield', lambdaEx=561, lambdaEm=609, numAper=1.4,
                  magObj=100, rindexObj=1.518, ccdSize=6540, dz=0, xysize=sd_params['size'], nslices=1,
                  depth=0, rindexSp=1.518, nor=0)
pf = PSF((sd_params['size'], sd_params['size']), **psf_params)

testdata = SD.create_testdata()
psf_big = np.zeros(testdata.shape)
psf_big[testdata.shape[0] // 2, :, :] = pf.data
testdata_psf = convolve_fft(testdata, psf_big)

# add noise to synthetic data
noisy_p = SD.add_poisson_noise(testdata_psf, p)
noisy_g = SD.add_gaussian_noise(noisy_p, g)
noisename = "p{:06.2e}g{:06.2e}".format(p, g)

# save results
if not os.path.exists(savepath):
    os.makedirs(savepath)
if not os.path.exists(savepath_noisy):
    os.makedirs(savepath_noisy)
if not os.path.exists(savepath_decon):
    os.makedirs(savepath_decon)
tf.imwrite(savepath + 'spots_bare.tif', testdata)
with open(savepath + 'spot_params.json', 'w') as fp:
    json.dump(sd_params, fp)
tf.imwrite(savepath + 'spots_psf.tif', testdata_psf)
with open(savepath + 'spot_psf_params.json', 'w') as fp:
    json.dump(psf_params, fp)
tf.imwrite(savepath_noisy + 'spots_noisy_'+noisename+'.tif', noisy_g)

# deconvolve synthetic data
deconname = "lamb{0:.2f}lambt{1:.2f}eps{2:.2e}maxit{3}".format(l, lt, eps, maxit)
print('deconvolving ', noisename)
print('l =  ', l, ' lt = ', lt)
Dec = Deconvolution(pf.data, noisy_g, l, lt, eps, maxit)
result = Dec.deconvolve()
tf.imwrite(savepath_decon+'spots_noisy_' + noisename + '_' + deconname + '.tif', result)


