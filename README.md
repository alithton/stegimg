# stegimg

Hide text in images using the least significant bit method.

This project is currently a work in progress.

## Installation

Install stegimg with pip:

```shell
python3 -m pip install --upgrade pip

python -m pip install --index-url https://test.pypi.org/simple/ \
--extra-index-url https://pypi.org/simple stegimg
```

## Usage

The stegimg package can function either as a library or a command line utility.

### Use as a library

To use as a library, import it into a Python file:

```python
from stegimg import lsb
```

Then, to encode a message in a selected cover image:

```python
from PIL import Image

# Select the image to be used as cover
cover_image = Image.open(path_to_image)

stego_image = lsb.encode_message(cover_image, "text to be hidden")
# Specify where the image should be saved
stego_image.save(output_path, format="bmp")
```

For least significant bit steganography, the image format should use lossless
compression, to ensure the message can be accurately retrieved. An example is
BMP format.

Decode an image containing a hidden message as follows:

```python
message = lsb.decode_message(path_to_stego_image)
```

### Use on the command line

To use as a command line utility run:

```shell
python3 -m stegimg.lsb
```

This will launch an interactive session. You will be asked to choose between
encoding a message or decoding a message contained within an image file.






