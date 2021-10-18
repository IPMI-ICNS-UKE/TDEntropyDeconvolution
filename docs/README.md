# Time-Dependent Entropy Deconvolution 

## About

This program deconvolves microscopy images. The input can either be a 2D single image or a 2D time series. 
The 2D-only version is based on [1]. For the deconvolution of a time series, a regularizer in time domain was added.
The point spread function can either be given as image input or calculated analytically with the relevant parameters.

## Usage

1. Download the Code and install the necessary Python packages, see [Setup]({{ site.baseurl }}{% link General/1-setup.md %}) 
2. Enter parameters in parameters.json file, see [Usage]({{ site.baseurl }}{% link General/2-usage.md %}) 
3. Run python main.py


## References
[1] Arigovindan, Muthuvel, Jennifer C. Fung, Daniel Elnatan, Vito Mennella, Yee-Hung Mark Chan, Michael Pollard, Eric Branlund, John W. Sedat, und David A. Agard. 2013. „High-Resolution Restoration of 3D Structures from Widefield Images with Extreme Low Signal-to-Noise-Ratio“. Proceedings of the National Academy of Sciences 110 (43): 17344–49. https://doi.org/10.1073/pnas.1315675110.