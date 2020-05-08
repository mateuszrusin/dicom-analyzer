from datetime import datetime
import os
from os.path import join, dirname, realpath

import pydicom
import dicognito.anonymizer
from PIL.Image import fromarray
from flask import Flask, flash, request, redirect, render_template, jsonify
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = join(dirname(realpath(__file__)), 'static', 'upload')

app = Flask(__name__, static_url_path='', static_folder='static')

app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ('dcm', 'ima', '')


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/send', methods=['POST'])
def send():
    if 'file[]' not in request.files:
        flash('No file part')
        return redirect('/')

    anonymizer = dicognito.anonymizer.Anonymizer()
    folder = datetime.now().strftime("%Y%m%d%H%M%S")
    dir = join(app.config['UPLOAD_FOLDER'], folder)
    os.makedirs(dir)
    jpgfiles = []
    for i, file in enumerate(request.files.getlist('file[]'), start=1):
        if file and allowed_file(file.filename):
            with pydicom.dcmread(file) as dataset:
                filename = str(i).zfill(4)
                dcmfile = join(dir, filename + '.dcm')
                anonymizer.anonymize(dataset)
                dataset.save_as(dcmfile)
                im = fromarray(dataset.pixel_array).convert('RGB')
                jpgfiles.append(join('upload', folder, filename + '.jpg'))
                im.save(join(dir, filename + '.jpg'))
        else:
            flash('File type not supported')
    else:
        flash('{} files successfully uploaded'.format(i))

    return render_template('home.html', files=jpgfiles)
