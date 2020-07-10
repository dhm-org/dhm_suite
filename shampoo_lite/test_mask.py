from shampoo_lite.mask import (Circle, Mask)
import numpy as np


#holo.generate_spectral_mask(center_x=[1267, 1599, 1382], center_y=[1483, 1042, 440], radius=[250, 250, 250])

dk = 0.008892642248612411

circle_list = []

circle_list.append(Circle(1267, 1483, 250))
circle_list.append(Circle(1599, 1042, 250))
circle_list.append(Circle(1382, 440, 250))

mask = Mask(2048, circle_list, dk)

print(mask.mask_centered.shape)
print(mask.mask_uncentered.shape)
print(len(mask.mask_coordinates))
