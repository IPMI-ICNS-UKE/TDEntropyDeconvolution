import itertools
import json
import os
import time

import numpy as np
import tifffile as tf

import util.inputoutput as io
from psf.psf import PSF
from util.deconvolution import Deconvolution


def main():
    # read in parameters
    with open('parameters.json', 'r') as read_file:
        parameters = json.load(read_file)
    psf_data = parameters['psf']
    io_data = parameters['io']
    decon_data = parameters['deconvolution']

    # create folders to save results
    try:
        if io_data['read_folder']:
            readpaths, savepaths = io.inputoutput_folder(io_data['save_path'], io_data['read_path'],
                                                         io_data['create_image_folder'])
        else:
            read_image_path, save_image_path = io.inputoutput(io_data['save_path'],
                                                              io_data['read_path'],
                                                              io_data['image_name'],
                                                              io_data['create_image_folder'])
            readpaths = [read_image_path]
            savepaths = [save_image_path]
    except Exception as E:
        print(E)
        return

    for read_image_path, save_image_path in zip(readpaths, savepaths):
        try:
            img = tf.imread(read_image_path)
        except Exception as E:
            print(E)
            print("!! Failed to read image " + read_image_path)
            continue
        # correct shape if image not quadratic
        if img.ndim == 2:
            if img.shape[0] != img.shape[1]:
                minshape = np.min(img.shape)
                img = img[:minshape, :minshape]
            xdims = img.shape
        else:
            if img.shape[1] != img.shape[2]:
                minshape = np.min(img.shape)
                img = img[:, minshape, :minshape]
            xdims = (img.shape[1], img.shape[2])

        # load or create point spread function
        if psf_data['experimental']:
            psf = tf.imread(psf_data['location'])
            pf = PSF(xdims)
            pf.data = psf
        else:
            psf_data['xysize'] = xdims[0]
            pf = PSF(xdims, **psf_data)

        # start deconvolution with parameter loops
        lamb_t_arr = decon_data['lambda_t']
        lamb_arr = decon_data['lambda']
        eps_arr = decon_data['epsilon']
        maxit = decon_data['max_iterations']
        delta = decon_data['delta']
        tol = 1e-6

        startingtime = time.strftime('%Y-%m-%d-%Hh%M', time.localtime(time.time()))
        with open(save_image_path + 'parameters_' + startingtime + '.json', 'w') as outfile:
            json.dump(parameters, outfile)

        for lamb_t, lamb, eps in itertools.product(lamb_t_arr, lamb_arr, eps_arr):
            if lamb_t != 0.0 and lamb_t != lamb:
                continue
            if img.ndim == 2:
                lamb_t = 0.0
            start = time.time()
            start_hr = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start))
            print("....................................")
            print(".... starting time : ", start_hr, " .......")
            print("deconvolving image ", os.path.basename(read_image_path))
            print("lamb_t = ", lamb_t, "  lamb = ", lamb, "  eps = ", eps)
            print(".......starting deconvolution.......")
            #            imf = convert_to_float(img)
            Dec = Deconvolution(pf.data, img, lamb, lamb_t, eps, maxit)
            result = Dec.deconvolve()
            print(".......deconvolution finished.......")
            print(".......saving results.......")
            # T, X, Y = result.shape
            # if original image is 2D only, a dimension needs to be dropped
            # if T == 1:
            #    result = result[0]
            # save result
            io.set_baseline(img, result)
            #            imu = convert_to_uint(result)
            # result = result.astype(np.uint16)
            tf.imwrite(io.create_filename_decon(save_image_path, lamb, lamb_t, maxit, eps),
                       result, photometric='minisblack')
            finish = time.time()
            finish_hr = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(finish))
            print(".... finished at : ", finish_hr, " .......")
            totaltime = finish - start
            print("total time for deconvolution: ", "{:6.2f}".format(totaltime), " s")
            print("............................")


if __name__ == '__main__':
    main()
