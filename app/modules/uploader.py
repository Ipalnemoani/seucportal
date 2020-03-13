import os
import sys
import datetime


from app import app


def upload_file_to_server(fileobj, preffix, secure_filename):


    original_name = fileobj.filename
    extantion = original_name.rsplit('.', 1)[1].lower()
    suffix = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")

    fullname = '{}_{}.{}'.format(preffix, suffix, extantion)
    filename = secure_filename(fullname)

    fileobj.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    return filename