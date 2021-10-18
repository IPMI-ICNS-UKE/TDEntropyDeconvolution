import numpy as np
from synthetic_data.synthetic_data import SyntheticData
from matplotlib import pyplot as plt
from psf.psf import PSF
from util.timedependence import convolve_fft
from util.deconvolution import Deconvolution
import tifffile as tf
import time
import os
from skimage.metrics import structural_similarity
import json
import skimage
from util.helper import convert_to_uint, convert_to_float

# number of runs
n = 1

# amount of poisson noise
p_array = np.linspace(0.001, 0.05, num=3, endpoint=True)
# amount of gaussian noise
g_array = np.linspace(0.0001, 0.005, num=3, endpoint=True)

# deconvolution parameter
l_array = np.array([0.2, 0.2])
lt_array = np.array([0.0, 0.2])
eps = 0.001
maxit = 1

for i in range(n):
    sd_params = dict(size=200, frames=50, spotsize=3, numpoints=50, motion=3, brightness=0.1)
    SD = SyntheticData(**sd_params)
    psf_params = dict(type='widefield', lambdaEx=561, lambdaEm=609, numAper=1.4,
                      magObj=100, rindexObj=1.518, ccdSize=6540, dz=0, xysize=sd_params['size'], nslices=1,
                      depth=0, rindexSp=1.518, nor=0)
    pf = PSF((sd_params['size'], sd_params['size']), **psf_params)
    wd = '/Users/lwoelk/pcloud/popsync/Syntheticdata/largerspots/skimage/float/'

    epoch = int(time.time())
    print('epoch: ', epoch)
    savepath = wd + str(epoch) + '/'
    savepath_noisy = savepath + 'noisy/'
    if not os.path.exists(savepath):
        os.makedirs(savepath)
    testdata = SD.create_testdata()
    psf_big = np.zeros(testdata.shape)
    psf_big[testdata.shape[0] // 2, :, :] = pf.data
    testdata_psf = convolve_fft(testdata, psf_big)
    tf.imwrite(savepath + 'spots_bare.tif', testdata)
    with open(savepath + 'spot_params.json', 'w') as fp:
        json.dump(sd_params, fp)
    tf.imwrite(savepath + 'spots_psf.tif', testdata_psf)
    with open(savepath + 'spot_psf_params.json', 'w') as fp:
        json.dump(psf_params, fp)

    if not os.path.exists(savepath_noisy):
        os.makedirs(savepath_noisy)
    for p in p_array:
        noisy_p = SD.add_poisson_noise(testdata_psf, p)
        for g in g_array:
            noisy_g = SD.add_gaussian_noise(noisy_p, g)
            noisename = "p{:06.2e}g{:06.2e}".format(p, g)
            tf.imwrite(savepath_noisy + 'spots_noisy_'+noisename+'.tif', noisy_g)

    for p in p_array:
        for g in g_array:
            for l, lt in zip(l_array, lt_array):
                noisename = "p{:06.2e}g{:06.2e}".format(p, g)
                img = tf.imread(savepath_noisy + 'spots_noisy_' + noisename + '.tif')
                savepath_decon = savepath + 'deconvolved/' + noisename + '/'
                deconname = "lamb{0:.2f}lambt{1:.2f}eps{2:.2e}maxit{3}".format(l, lt, eps, maxit)
                if not os.path.exists(savepath_decon):
                    os.makedirs(savepath_decon)
                print('deconvolving ', noisename)
                print('l =  ', l, ' lt = ', lt)
                Dec = Deconvolution(pf.data, img, l, lt, eps, maxit)
                result = Dec.deconvolve()
                tf.imwrite(savepath_decon+'spots_noisy_' + noisename + '_' + deconname + '.tif', result)


