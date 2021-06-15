"""inline-html-images.py -- Inline HTML Images

Encode images straight into the html source, to save a http round-trip.

Usage: inline-html-images.py filename.html file_size_limit > output.html

"""

#TODO: Add support for favicons, and for the reverse operation
#TODO: Parse arguments with argparse instead of naively reading sys.argv
#TODO: the filename (path actually) is lost when translating to base64. Maybe we can save that information into some html attrbiute to the img tag.

import base64
import os
import sys

from bs4 import BeautifulSoup


def pad_string(string: str, length: int, delimiter: str="\n") -> str:
    """Add `delimiter` to every `length` chars in `string`"""
    string = delimiter.join(string[i: i + length] for i in range(0, len(string), length))
    return string


def image_to_base64(path: str):
    contents = None
    with open(path, "rb") as f:
        contents = f.read()

    base64string = base64.b64encode(contents).decode("utf-8")

    return base64string


def base64_to_image():
    pass


def main():
    # Parse args. TODO: should really be done with argparse
    source_file = sys.argv[1]
    assert str.endswith(source_file, ".html")

    if len(sys.argv) > 2:
        file_size_limit = int(sys.argv[2])
    else:
        file_size_limit = 1024 * 1024 # 1MB

    # Because embedding an image into a base64 string straight into html can cause really long lines, which
    # are problematic for some editors, we add newlines at every `length` character.
    length = 100

    with open(source_file, "r") as html_contents:
        soup = BeautifulSoup(html_contents, "html")
      
        # For all images, if they are under file_size_limit, replace their src with the base64 src
        for img in soup.findAll("img"):
            # To encode the image into html, we need to find out three things:
            #   - image size -- we don't actually need this, but we use it not to encode large images, as they mangle the html too much.
            #   - image type -- we get this from the extension for now. TODO: Use something akin to unix `file`
            #   - image path and contents -- we get this from the `src` html attribute. TODO: handle both URLs as well as paths, we just handle paths for now.

            # image size
            if not os.path.exists(img.attrs["src"]):
                continue
            if os.path.getsize(img.attrs["src"]) > file_size_limit:
                continue # skip files larger that file_size_limit

            # image path and contents
            base64string = image_to_base64(img.attrs["src"])            
            base64string = pad_string(base64string, length)

            # image type
            img_type = img.attrs["src"].split(".")[-1] # get the filename extension

            # Construct the new `src` html attribute
            new_src = "data:image/" + img_type + ";charset=utf-8;base64," + base64string

            # Add the new `src` attribute in the html source.
            img.attrs["src"] = new_src

    # Write the modified html source to the file. TODO: This operation should probably be done in a safer way,
    # but for not there is no problem of overwriting the file we read from, beacuse we read everything into
    # memory before we write back to the file.
    with open(source_file, "w") as output_file:
        output_file.write(str(soup))


if __name__ == "__main__":
    main()
