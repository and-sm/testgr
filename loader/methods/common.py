import base64
import secrets
import os
from io import BytesIO
from PIL import Image

from django.core.files.base import ContentFile
from loader.models import Screenshots

def save_images(obj, test):
    ext = ".png"
    if "screens" in obj.data:
        if isinstance(obj.data["screens"], list) or isinstance(obj.data["screens"], dict):
            for screenshot in obj.data['screens']:
                # If images data has list/dict format, for example [{name: base64}, {name: base64}]
                if isinstance(screenshot, dict):
                    folder = secrets.token_urlsafe(6)
                    name = screenshot["name"]
                    data = ContentFile(base64.b64decode(screenshot["image"]), name=folder + "/" + name + ext)
                    s_data = Screenshots(test=test, name=name, image=data,
                                         thumbnail="screenshots/" + folder + "/" + name + "_thumb" + ext)

                # Images as list items: [base64, base64...]
                else:
                    folder = secrets.token_urlsafe(6)
                    name = secrets.token_urlsafe(4)
                    data = ContentFile(base64.b64decode(screenshot), name=folder +"/ "+ name + ext)
                    s_data = Screenshots(test=test, name=name, image=data,
                                         thumbnail="screenshots/" + folder + "/" + name + "_thumb" + ext)
                s_data.save()
