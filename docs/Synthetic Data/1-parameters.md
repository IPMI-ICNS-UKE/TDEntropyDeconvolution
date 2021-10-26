---
sort: 1
---

# Parameters

To create synthetic data, the following parameters are available:

```size```: spatial dimensions of the resulting time frame, i.e. ``size=500``results in 500 x 500 pixel frames

```frames```: number of time frames

```spotsize```: size of the individual spots

```numpoints```: total number of spots

```motion```: factor to determine the speed of the Brownian motion. Larger values correspond to faster motion. 

```brightness```: relative brightness of the spots


Also necessary is the definition of a point spread function to convolve (and eventually deconvolve) with. 
For psf parameters, see [usage]({{ site.baseurl }}{% link General/2-usage.md %}).

