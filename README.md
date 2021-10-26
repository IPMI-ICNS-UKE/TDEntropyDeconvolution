
# Time-Dependent Image Restoration

For detailed instructions see the [Documentation](https://ipmi-icns-uke.github.io/TDEntropyDeconvolution/). 

## About

This program deconvolves microscopy images. The input can either be a 2D single image or a 2D time series, i.e. 2D+t data. 
The corresponding publication is published as a preprint in [1].
The 2D-only version is based on [2]. For the deconvolution of a time series, a regularizer in time domain was added.
The point spread function can either be given as image input or calculated analytically with the relevant parameters.

## Usage

1. Enter parameters in parameters.json file, details see in the 
   [Documentation](https://ipmi-icns-uke.github.io/TDEntropyDeconvolution/)
2. Run python main.py


## References
[1] L. Woelk, S. A. Kannabiran, V. Brock, Ch. E. Gee, Ch. Lohr, A. H. Guse, B. Diercks, and R. Werner. 2021. "Time-Dependent Image Restoration of Low-SNR Live Cell Ca2+ Fluorescence Microscopy Data". bioRxiv 2021.10.05.462864. https://doi.org/10.1101/2021.10.05.462864.

[2] Arigovindan, Muthuvel, Jennifer C. Fung, Daniel Elnatan, Vito Mennella, Yee-Hung Mark Chan, Michael Pollard, Eric Branlund, John W. Sedat, und David A. Agard. 2013. „High-Resolution Restoration of 3D Structures from Widefield Images with Extreme Low Signal-to-Noise-Ratio“. Proceedings of the National Academy of Sciences 110 (43): 17344–49. https://doi.org/10.1073/pnas.1315675110.
