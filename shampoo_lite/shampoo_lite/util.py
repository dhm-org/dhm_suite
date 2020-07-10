import numpy as np

def circ_prop(kx, ky, k): 

    r = np.sqrt(kx**2+ky**2)/k
    z = r < 1 

    return z.astype(np.float)

def crop_image(image, crop_fraction):
    """
    Crop an image by a factor of ``crop_fraction``.
    """
    if crop_fraction == 0:
        return image

    crop_length = int(image.shape[0] * crop_fraction)

    if crop_length not in TWO_TO_N:
        message = ("Final dimensions after crop should be a power of 2^N. "
                   "Crop fraction of {0} yields dimensions ({1}, {1})"
                   .format(crop_fraction, crop_length))
        warnings.warn(message, CropEfficiencyWarning)

    cropped_image = image[crop_length//2:crop_length//2 + crop_length,
                          crop_length//2:crop_length//2 + crop_length]
    return cropped_image
