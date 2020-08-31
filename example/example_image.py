from camp.utils.mock import create_fake_image
from camp.utils.image import Image

test_image = create_fake_image(center=[200,100], noise= 0.03)
image = Image(test_image)

image.show()
image.plot_profiles()
image.describe()