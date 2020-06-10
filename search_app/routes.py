import io
from flask import request, jsonify, render_template, send_file
from google.cloud import storage

from app import logger, db, app
from managers import PostManager


@app.route('/ping')
def ping():
    return "hello world"


@app.route('/download')
def download_post():
    bucket_path = request.args.get("bucket_path")
    bucket_name, object_path = bucket_path.split("/", 1)
    gsc = storage.Client()
    bucket = gsc.get_bucket(bucket_name)
    blob = bucket.blob(object_path)
    filename = object_path.rsplit('/', 1)[-1]
    filename = filename[ : filename.rfind('.txt') + 4]
    s = blob.download_as_string()
    logger.log_text("downloaded from google storage: {}".format(s))
    mem = io.BytesIO()
    mem.write(s)
    mem.seek(0)
    logger.log_text("written string to BytesIO")
    return send_file(mem, attachment_filename=filename, mimetype='text/plain')
        


@app.route('/search', methods=["POST"])
def search():
    filt = request.form
    # ignore empty query values
    filt = {k: v for k,v in filt.items() if v is not None and v != ""}
    # tranform types
    typeD = {
        "post_id": int,
        "sentiment_score": float,
        "sentiment_magnitude": float,
        "author_id": int,
        "age": int
    }
    for k,v in typeD.items():
        if k in filt:
            filt[k] = v(filt[k])
    mgr = PostManager()
    posts = mgr.get_many(filt)
    return render_template("index.html", posts=posts)


@app.route('/', methods=["GET"])
def index():
    posts = PostManager().get_many({})
    # posts = []
    return render_template("index.html", posts=posts)