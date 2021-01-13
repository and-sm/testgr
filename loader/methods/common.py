import base64
import secrets
import datetime
import io
import PIL
from PIL import Image

from django.core.files.base import ContentFile
from loader.models import Screenshots


def generate_images_path():
    year = datetime.date.today().year
    month = datetime.date.today().month
    day = datetime.date.today().day
    folder = secrets.token_urlsafe(6)
    path = f"{year}/{month}/{day}/" + folder + "/"
    return path

def save_images(obj, test):
    ext = ".png"
    if "screens" in obj.data:
        if isinstance(obj.data["screens"], list) or isinstance(obj.data["screens"], dict):
            for screenshot in obj.data['screens']:
                # If images data has list/dict format, for example [{name: base64}, {name: base64}]
                path = generate_images_path()
                if isinstance(screenshot, dict):
                    name = screenshot["name"]
                    image_decoded = base64.b64decode(screenshot["image"])
                    data = ContentFile(image_decoded, name=path + name + ext)
                # Images as list items: [base64, base64...]
                else:
                    name = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                    image_decoded = base64.b64decode(screenshot)
                    data = ContentFile(image_decoded, name=path+ name + ext)

                thumb = PIL.Image.open(io.BytesIO(image_decoded))
                new_width = 128
                new_height = new_width * thumb.size[1] / thumb.size[0]
                resized_thumb = thumb.resize((new_width, int(new_height)))
                thumb_extension = thumb.format.lower()
                thumb_filename = name + '_thumb'

                if thumb_extension in ['jpg', 'jpeg']:
                    FTYPE = 'JPEG'
                elif thumb_extension == 'gif':
                    FTYPE = 'GIF'
                elif thumb_extension == 'png':
                    FTYPE = 'PNG'
                else:
                    return False

                byteIO = io.BytesIO()
                resized_thumb.save(byteIO, format=FTYPE)
                byte_arr = byteIO.getvalue()

                t_data = ContentFile(byte_arr, name=path + thumb_filename + "." + thumb_extension)
                s_data = Screenshots(test=test, name=name, image=data, thumbnail=t_data)
                s_data.save()

