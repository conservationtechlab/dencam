"""Functions for calculations.

At this point this is just the function that calculates the blur
score.

"""
from scipy.ndimage import laplace


def calculate_blur(image_array):
    """Compute the blur variance for an image array.

    Calculates the blur variance of an array of pixels using the
    Laplacian method.

    Args:
        image_array (numpy.ndarray): Grayscale image array to analyze.

    Returns:
        float: Variance of the Laplacian, where a lower variance
        indicates more blur.

    """
    laplacian_result = laplace(image_array)
    return laplacian_result.var()
