---
sort: 2
---
# Usage

## Running the Program 

Once all the required packages are installed, the program can be run by executing

```
python main.py
```

in the command line. In case your default Python executable is not linked to Python 3.x, run ```python3 main.py```
instead.

## Input Parameters

This program relies heavily on input parameters and should not be run without carefully choosing their values.
Parameters are given to the program by editing the file `parameters.json` with a text editor of your choice.

### Point Spread Function
The point spread function can either be given as an image file, for example the result of experimental measurements, or
calculated analytically using microscope parameters.


If the psf is given **experimentally** (i.e. by a .tif file or comparable), the first two parameters 
in the ```parameters.json``` file should be set to

```json
{
  ...
  "experimental": true,
  "location": "path/to/your/psf.tif",
  ...
}
```
where of course the path is to be replaced by the path to the image of the psf. Note that the size of the psf 
needs to be the same as the size of the input image. For a time series, the size of the psf should be the 
same as the size of one frame.
For example, for a time series with 100 frames with 500 x 500 pixels each, the psf should be 500 x 500 pixels.


If the psf is to be calculated **analytically**, the parameter "experimental" has to be set to "false", i.e.

```json
{
  ...
  "experimental": false,
  ...
}
```
In this case, the ``"location"`` parameter will be ignored.
 
The types of microscope supported are either ```"confocal"``` or ``"widefield"`` , which needs to be specified in the 
corresponding parameter. Other microscope parameters are

- ``"lambdaEx"``: Excitation Wavelength (in nm),
- ``"lambdaEm"``: Emission wavelength (in nm),
- ``"numAper"``: Numerical aperture of the objective,
- ``"magObj"``: Objective total magnification,
- ``"rindexObj"``: Refractive index of the objective immersion medium,
- ``"ccdSize"``: Pixel dimension of the CCD (in the plane of the camera),
- ``"dz"``: Optical axis Z sampling or defocusing (in nm),
- ``"nslices"``: Number of slices desired (Depth view/Z axis sampling),
- ``"depth"``: depth of the specimen under the cover-slip in nm,
- ``"rindexSp"``: Refractive index of the specimen medium,
- ``"nor"``: Normalization on the PSF (default: no normalization)
         0: l-infinity normalization
         1: l-1 normalization
  

and need to be set accordingly. 

The calculation of the psf is based on the following matlab function by Praveen Pankajakshan:

Praveen Pankajakshan (2021). Widefield Fluorescence Microscope point-spread function (https://www.mathworks.com/matlabcentral/fileexchange/31945-widefield-fluorescence-microscope-point-spread-function), MATLAB Central File Exchange. Retrieved April 29, 2021. 



### Input/ Output

Supported datatypes for input images (including psf, if given experimentally) are determined by the [tifffiles](https://pypi.org/project/tifffile/)
package and as of now given by TIFF, BigTIFF, OME-TIFF, STK, LSM, SGI, NIHImage, ImageJ, 
MicroManager, FluoView, ScanImage, SEQ, GEL, SVS, SCN, SIS, ZIF (Zoomable Image File Format), 
QPTIFF (QPI), NDPI, and GeoTIFF files.


For processing images using this deconvolution method, there are two options

1. Provide a single image file to be deconvolved. This can either be a 2D individual image, or a time series.
2. Provide the path to a folder where _all_ files detected will be processed. Note that currently, 
this folder needs to contain only files of supported types, see above.
   
In the first case, where a single image should be processed, set the following parameters to

```json
{
  ...
  "read_folder": false,
  "read_path": "path/to/folder",
  "image_name": "nameofimage.tif",
  ...
}
```

where the path and name are of course substituted with the actual path and name. Note that all paths can either be given
as absolute paths or relative to the current working directory, i.e. the directory the ``main.py`` file is located. 

In case the entire folder is to be processed, the first variable should be set to 
````json
{
  ...
  "read_folder": true,
  "read_path": "path/to/folder",
  ...
}
````

In this case, the parameter ````"image_name"```` will be ignored.

The parameter ```"save_path"``` controls the location of the result. Note that for each image procesed,
a new subfolder will be created in this location. Results for each parameter set (see next section) will be saved as a different
file with the parameter values in the file name.


At the moment, depending on your machine, the program does not support very large data files due to memory issues. 
The workaround is to give a specific region of interest to process. 

Whether or not a region of interest will be cut out is controlled by the parameter ````"cut_roi"````, which can be set
either to ````true```` or ```false```.

If it is set to ``true``, the spatial region can be determined by setting the desired image size and the upper 
left corner of the roi. If slicing in the time domain is also desired, the first and last frame should be given. 
For example

```json
{
  ...
  "size": 500,
  "upper_left": [250, 500],
  "time": [0, 10],
  ...
}
```

will cut a 500 pixel x 500 pixel region of interest starting at the point ```[250, 500]```, where the first 
is the _vertical_ and the second the _horizontal_ coordinate. Only frames ````0-10```` will be processed.

If the entire image (or frame) is to be processed with no region of interest cut out, the value of ````"size"```` needs 
to be set to ```"size": "all"```. Similarly, in the time domain, ``"time": "all"`` will ensure processing of all frames.

If ```"cut_roi"``` is set to ```"false"```, all of the above parameters will be ignored.


### Deconvolution

For the actual deconvolution, some parameters need to be empirically determined to ensure best results.

Most important are the values of ```"lambda"``` and ```"lambda_t"```, the two lagrange parameters which control the 
regularization. ```"lambda"``` controls the smoothness within each time frame, whereas ```"lambda_t"``` controls the 
smoothness over time. If the input image is a single image and not a time series, the value of ```"lambda_t"``` will be 
ignored.

Since the optimal set of parameters needs to be determined for each image or image type, multiple values can be given, 
which will be iterated over. The variable ```"epsilon"``` can also be assigned several values to iterate over, although 
this should simply be set to a small positive number.

For example, 

```json
{
  ...
  "lambda":[
    0.1, 0.2, 0.3
  ],
  "lambda_t":[
    0.0, 0.1, 0.2    
  ],
  "epsilon": [
    0.001, 0.0001
  ],
  ...
}
```

will iterate over each parameter combination and deconvolve the input image or images with each set of parameters 
separately. The results are then saved in the results folder (see above) with the values of the parameters saved to the 
file name.

Additionally, the number of iterations can be chosen with the parameter ```"max_iterations"```. In a lot of cases, one
iteration will suffice, but in some cases, a higher number can be beneficial. 

The parameter ```"delta"``` controls the weighting between spatial and temporal derivatives. If the value is set to
```1```, all derivatives are weighed equally. For values ```"delta" < 1```, the temporal derivatives will be weighted less
in comparison to spatial derivatives.
