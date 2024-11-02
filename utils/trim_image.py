from PIL import Image, ImageChops

def trim(image: Image) -> Image:
    bg = Image.new(image.mode, image.size, image.getpixel((0, 0)))
    diff = ImageChops.difference(image, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    return image.crop(bbox) if bbox else image

def trim_image():
    im = Image.open("images\\registry_captcha.png")
    im = trim(im)
    im.save("images\\registry_captcha_after_trim.png")