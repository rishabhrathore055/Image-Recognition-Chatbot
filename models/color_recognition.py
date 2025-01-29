import webcolors
from sklearn.cluster import KMeans
import numpy as np
from PIL import Image

def rgb_to_name(rgb):
    """Convert RGB to the closest color name."""
    try:
        # Find the closest color name from the RGB value
        return webcolors.rgb_to_name(rgb)
    except ValueError:
        # Return a default color name if no match is found
        return "Unknown color"


def extract_dominant_colors(image, n_colors=3):
    """Extract dominant colors using K-means clustering."""
    # Convert image to RGB
    image_rgb = image.convert("RGB")
    image_np = np.array(image_rgb)

    # Reshape image to a 2D array of pixels
    pixels = image_np.reshape(-1, 3)

    # Remove alpha channel (if any)
    pixels = pixels[pixels[:, 3] < 255] if pixels.shape[1] == 4 else pixels

    # Apply KMeans clustering to find dominant colors
    kmeans = KMeans(n_clusters=n_colors)
    kmeans.fit(pixels)

    # Get the RGB values of the cluster centers (dominant colors)
    dominant_colors = kmeans.cluster_centers_

    # Convert RGB to color names (if possible)
    color_names = [rgb_to_name(tuple(map(int, color))) for color in dominant_colors]
    return color_names
