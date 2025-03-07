from PIL import Image, ImageEnhance
import matplotlib.pyplot as plt

# Load the image
image_path = '/Users/psinha/Downloads/peakpx.jpg'
image = Image.open(image_path)

# Enhance the sharpness
enhancer = ImageEnhance.Sharpness(image)
enhanced_image = enhancer.enhance(2.0)  # Increase sharpness by a factor of 2

# Display the original and enhanced images
plt.figure(figsize=(10, 5))
plt.subplot(1, 2, 1)
plt.title("Original Image")
plt.imshow(image)
plt.axis("off")

plt.subplot(1, 2, 2)
plt.title("Enhanced Image")
plt.imshow(enhanced_image)
plt.axis("off")

plt.show()