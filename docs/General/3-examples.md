---
sort: 3
---

# Examples 


## 2D Deconvolution

Consider a single 2D image acquired with a confocal spinning disc microscope. 
The point spread function can be calculated analytically with the relevant microscope parameters.
In order to find the optimal parameters for the deconvolution, several parameters are given as input in the parameter
file. 

The following parameter input file will result in 8 different deconvolutions of the image. The resulting 8 images will be saved 
to the folder given by the parameter ```"save_path"``` with the file name indicating the parameter combination used for 
the deconvolution.
For single 2D images the most important parameter to determine is ````"lambda"````, although in some cases
the value of ````"epsilon"```` can have a small impact as well. The same is true for the value of ````"max_iterations"````,
which will sometimes give better results with a value of larger than 1.



```json
{
  "psf":
  {
    "experimental": false,
    "location": "path/to/psf/psf.tif",
    "microscope_type": "confocal",
    "lambdaEx": 561,
    "lambdaEm": 583,
    "numAper": 1.46,
    "magObj": 100,
    "rindexObj": 1.518,
    "ccdSize": 6544.9,
    "dz": 0,
    "nslices": 1,
    "depth": 0,
    "rindexSp": 1.518,
    "nor": 0
  },
  "io":
  {
    "read_folder": false,
    "read_path": "data/2D/",
    "image_name": "example.tif",
    "save_path": "results/2D/"
  },
  "roi":
  {
    "cut_roi": false,
    "size":  500,
    "upper_left": [250, 500],
    "time": "all"
  },
  "deconvolution":
  {
    "lambda": [
      0.5, 0.6, 0.7, 0.8
    ],
    "lambda_t": [
      0.0
    ],
    "epsilon": [
      0.001, 0.0001
    ],
    "max_iterations": 1,
    "delta": 1.0
  }
}
```

Once an appropriate parameter value is found, the parameters can of course be put individually as well.


## 2D Time-Dependent Deconvolution

For a time series, there is an extra parameter to determine ````"lambda_t"````. This parameter can also be looped
over, i.e. the following parameter input file

```json
{
  "psf":
  {
    "experimental": false,
    "location": "path/to/psf/psf.tif",
    "microscope_type": "confocal",
    "lambdaEx": 561,
    "lambdaEm": 609,
    "numAper": 1.46,
    "magObj": 100,
    "rindexObj": 1.518,
    "ccdSize": 6544.9,
    "dz": 0,
    "nslices": 1,
    "depth": 0,
    "rindexSp": 1.518,
    "nor": 0
  },
  "io":
  {
    "read_folder": false,
    "read_path": "data/time/",
    "image_name": "example_timeseries.tif",
    "save_path": "results/time/"
  },
  "deconvolution":
  {
    "lambda": [
      0.5, 0.6, 0.7
    ],
    "lambda_t": [
      0.0, 0.1, 0.2
    ],
    "epsilon": [
      0.001
    ],
    "max_iterations": 1,
    "delta": 1.0
  }
}
```
will result in 9 deconvolved time series.