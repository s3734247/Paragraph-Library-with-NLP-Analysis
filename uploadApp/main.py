import time
import logging
import json
from flask import Flask, render_template, request, redirect, url_for
import os
from werkzeug.utils import secure_filename
from google.cloud import storage
from pip._internal.cli.status_codes import SUCCESS
from _ast import If
ALLOWED_EXTENSIONS = {'xml'}
app = Flask(__name__)

bucket_config = {}
with open("xml_bucket.config.json") as fh:
    bucket_config = json.load(fh)

@app.route('/upload', methods=['POST', 'GET'])  
def upload():
    if request.method == 'POST':
        uploaded_file = request.files.get('file')
        if allowed_file(uploaded_file.filename):
            gcs = None  
            if bucket_config.get('project', None) is not None:
                gcs = storage.Client(project=bucket_config['project'])
            else:
                gcs = storage.Client()
            bucket = gcs.get_bucket(bucket_config["bucket_name"])
            blob = bucket.blob("{}.{}".format(uploaded_file.filename, time.time()))
            blob.upload_from_file(uploaded_file)
        else:
            return render_template('index.html',messg=" File EXTENSIONS is not Allowed!!")
   
       
    return render_template('index.html',messg="UPLOAD SUCCESSFUL")


@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500



@app.route('/')
def hello():
    return render_template('index.html',messg="Hello!,you can upload now!")


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
















if __name__ == '__main__':

    app.run(host='127.0.0.1', port=6061, debug=True)

