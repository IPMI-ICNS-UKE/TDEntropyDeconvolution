import numpy as np
from synthetic_data.perlin import PerlinNoiseFactory
from synthetic_data.Brownian import Brownian
import scipy.stats as stats


class SyntheticData:

    def __init__(self, size, frames, spotsize, numpoints, motion, brightness,
                 perlin_res=100, perlin_octaves=1, perlin_dim=2):
        self.size = size
        self.frames = frames
        self.spotsize = spotsize
        self.numpoints = numpoints
        self.motion = motion
        self.brightness = brightness
        self.perlin_res = perlin_res
        self.perlin_octaves = perlin_octaves
        self.perlin_dim = perlin_dim
        self.testdata = np.zeros((self.frames, self.size, self.size))


    def perlin_noise(self):
        space_range = self.size // self.perlin_res
        pnf = PerlinNoiseFactory(self.perlin_dim, octaves=self.perlin_octaves, tile=(space_range, space_range))
        perlin = np.zeros((self.size, self.size))
        for x in range(self.size):
            for y in range(self.size):
                n = pnf(x / self.perlin_res, y / self.perlin_res)
                perlin[x, y] = n
        return perlin


    def pick_spot_locations(self, perlin):
        light_area = np.where(perlin > 0.5 * perlin.max())
        light_area_x = light_area[0]
        light_area_y = light_area[1]
        light_range = len(light_area_x)
        light_picks = np.random.randint(low=0, high=light_range, size=self.numpoints)
        x0 = light_area_x[light_picks]
        y0 = light_area_y[light_picks]
        return x0, y0


    def create_spot_dynamic(self, x0, y0):
        motion = np.zeros((self.numpoints, 2, self.frames))
        for i in range(self.numpoints):
            # trajectory of spot
            b1 = Brownian()
            b2 = Brownian()
            xt = b1.gen_normal(self.frames)
            yt = b2.gen_normal(self.frames)
            # shift by initial position
            xt_shifted = xt * self.motion + x0[i]
            yt_shifted = yt * self.motion + y0[i]
            motion[i] = np.vstack((xt_shifted, yt_shifted))
            # periodic boundary conditions
            motion[np.where(motion < 0)] += self.size
            motion[np.where(motion > self.size)] -= self.size
        return motion


    def create_gaussian_spot(self, x_i, y_i):
        x, y = np.mgrid[0:self.size:1, 0:self.size:1]
        pos = np.dstack((x, y))
        Sigma = np.array([[self.spotsize, 0], [0, self.spotsize]])
        mu = np.array([x_i, y_i])
        rv = stats.multivariate_normal(mu, Sigma)
        gauss = rv.pdf(pos)
        return gauss / gauss.max()


    def create_testdata(self):
        perlin = self.perlin_noise()
        # pick start locations of spots
        x0, y0 = self.pick_spot_locations(perlin)
        # position of spots
        motion = self.create_spot_dynamic(x0, y0)
        self.testdata = np.zeros((self.frames, self.size, self.size))
        for t in range(self.frames):
            for i in range(self.numpoints):
                spot = self.create_gaussian_spot(motion[i, 0, t], motion[i, 1, t])
                self.testdata[t] += spot
        self.testdata *= self.brightness
        return self.testdata


    def create_testdata_autofluo(self):
        perlin = self.perlin_noise()
        # pick start locations of spots
        x0, y0 = self.pick_spot_locations(perlin)
        # position of spots
        motion = self.create_spot_dynamic(x0, y0)
        testdata = np.zeros((self.frames, self.size, self.size))
        testdata_autofluo = np.zeros((self.frames, self.size, self.size))
        for t in range(self.frames):
            for i in range(self.numpoints):
                spot = self.create_gaussian_spot(motion[i, 0, t], motion[i, 1, t])
                testdata[t] += spot
        testdata *= self.brightness
        testdata_autofluo = testdata + 0.1 * self.brightness * perlin
        testdata_autofluo = testdata_autofluo - testdata_autofluo.min()
        return testdata, testdata_autofluo


    def add_poisson_noise(self, img, p):
        img_noisy = np.zeros(img.shape)
        for t in range(img.shape[0]):
            img_noisy[t] = p*np.random.poisson(lam=img[t]/p)
        return img_noisy

    def add_gaussian_noise(self, img, var, mean=0.0):
        sigma = var**0.5
        gauss = np.random.normal(mean,sigma,img.shape)
        gauss = gauss.reshape(img.shape)
        img_noisy = img + gauss
        return img_noisy
