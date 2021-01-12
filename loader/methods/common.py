import base64
import secrets
import datetime

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
                    data = ContentFile(base64.b64decode(screenshot["image"]), name=path + name + ext)
                    s_data = Screenshots(test=test, name=name, image=data)
                # Images as list items: [base64, base64...]
                else:
                    name = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                    data = ContentFile(base64.b64decode(screenshot), name=path+ name + ext)
                    s_data = Screenshots(test=test, name=name, image=data)

                s_data.save(path)
