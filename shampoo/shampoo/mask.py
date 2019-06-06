
import numpy as np

class Circle(object):
    def __init__(self, centerx, centery, radius):
        self.centerx = centerx
        self.centery = centery
        self.radius = radius
        self._params = None
        self.get_params
    @property
    def get_params(self):
        if self._params is None:
            self._params = (self.centerx, self.centery, self.radius)
        return self._params

class Mask(object):
    def __init__(self, N, circle_list):
        self.x, self.y = np.meshgrid(np.linspace(0, N, N),np.linspace(0, N, N))
        self.N = N
        self.circle_list = circle_list
        self._mask = None
        self.mask
    @property
    def mask(self):
        if self._mask is None:
            self._mask = np.zeros((self.N, self.N, len(self.circle_list)), dtype=np.bool) 
            for _ in range(len(self.circle_list)):
                centerx, centery, radius = self.circle_list[_].get_params
                self._mask[:,:,_] = ( np.power(self.x-centerx,2) + np.power(self.y-centery, 2) < radius*radius )
        return self._mask 
        

