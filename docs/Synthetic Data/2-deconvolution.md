---
sort: 2
---

# Deconvolving Synthetic Data 

Given here is an example of a workflow for using our deconvolution algorithm with synthetic data.
The same workflow can be run at once by changing the relevant parameters in the script ``example_synthetic.py`` and running it as 
``shell
python example_synthetic.py
``

## Creation of Noisy Synthetic Data

First step is to create the synthetic data using the parameters detailed in [parameters]({{ site.baseurl }}{% link Synthetic Data/1-parameters.md %}).
For example:

```python
from synthetic_data.synthetic_data import SyntheticData

sd_params = dict(size=200, frames=50, spotsize=3, numpoints=50, motion=3, brightness=0.1)
SD = SyntheticData(**sd_params)

testdata = SD.create_testdata()
```

To convolve with a PSF, continue as follows:

```python
from psf.psf import PSF
import numpy as np
from util.timedependence import convolve_fft

psf_params = dict(type='widefield', lambdaEx=561, lambdaEm=609, numAper=1.4,
                  magObj=100, rindexObj=1.518, ccdSize=6540, dz=0, xysize=200, nslices=1,
                  depth=0, rindexSp=1.518, nor=0)
pf = PSF((200, 200), **psf_params)


psf_big = np.zeros(testdata.shape)
psf_big[testdata.shape[0] // 2, :, :] = pf.data
testdata_psf = convolve_fft(testdata, psf_big)
```

Finally, noise can be added to the synthetic data.

```python
noisy_p = SD.add_poisson_noise(testdata_psf, p)
noisy_g = SD.add_gaussian_noise(noisy_p, g)
```
where p and g control the level of Poisson and Gaussian noise, respectively.


## Deconvolution


For the deconvolution, the deconvolution parameters lambda, lambda_t, epsilon and maxit are needed. See [usage]({{ site.baseurl }}{% link General/2-usage.md %}).
Of course it is necessary to use the same PSF (or generate one with the same parameters), as was used to degenerate the data earlier.

```python
from util.deconvolution import Deconvolution

Dec = Deconvolution(pf.data, noisy_g, l=0.1, lt=0.1, eps=0.001, maxit=1)
result = Dec.deconvolve()                
```