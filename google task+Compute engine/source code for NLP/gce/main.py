import time
import logging
import json
from flask import Flask, render_template, request, redirect, url_for
import os
from werkzeug.utils import secure_filename
from google.cloud import storage
from pip._internal.cli.status_codes import SUCCESS
from _ast import If
import os
import json
import datetime
import base64
import pymysql
from google.cloud import tasks_v2
from google.protobuf import timestamp_pb2
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
from google.cloud import logging
import ast

log_client = logging.Client()
logger = log_client.logger("cloudfunctions.googleapis.com%2Fcloud-functions")


ALLOWED_EXTENSIONS = {'xml'}
app = Flask(__name__)

bucket_config = {}
with open("xml_bucket.config.json") as fh:
    bucket_config = json.load(fh)

@app.route('/upload', methods=['POST', 'GET'])
def upload():

    return render_template('index.html',messg=mess22)





@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500



@app.route('/')
def hello():
    #print('Received task with payload: {}'.format(payload))
    #logging.exception('Hello this is Hello')
    
    logger.log_text(" hello from Compure engine ")
    return render_template('index.html',messg="heeeee4llo")
    



@app.route('/NLP_to', methods=['POST'])
def NLP_to():
    """Log the request payload."""
    logger.log_text('welcome to NLP')
    payload = request.get_data(as_text=True) or '(empty payload)'
    logger.log_text('Received task with payload: {}'.format(payload))
    payload = ast.literal_eval(payload)
    logger.log_text("convert")
    google_NLP(payload)
    print('Received task with payload')
    return 'Printed task payload: {}'.format(payload)
# [END cloud_tasks_appengine_quickstart]




def google_NLP(task_data):
    CS = storage.Client()
    bucket = CS.bucket(bucket_config['bucket2_name'])

    filepath = os.path.split(task_data['bucket_path'])[1]
    txtblob = bucket.blob(filepath)
    b = txtblob.download_as_string()
    s = to_en(b)
    # Instantiates a client
    client = language.LanguageServiceClient()

    # The text to analyze

    document = types.Document(
    content=s,
    type=enums.Document.Type.PLAIN_TEXT)
    sentiment = client.analyze_sentiment(document=document).document_sentiment
    response1 ='Sentiment: {}, {}'.format(sentiment.score, sentiment.magnitude)
    sql = 'UPDATE Post SET sentiment_score='+str(sentiment.score)+',sentiment_magnitude='+str(sentiment.magnitude)+' WHERE id='+ str(task_data['post_rds_id'])

    conn = pymysql.connect(user=bucket_config['sql_user'], password=bucket_config['sql_password'], database=bucket_config['sql_database'],
            unix_socket="/opt/app/gce/socket/{}".format(bucket_config['sql_connection']))
    with conn.cursor() as cur:
        cur.execute(sql)
        conn.commit()
    conn.close()
    return response1




def to_en(b: bytes) -> str:
    return ''.join([chr(c) if 31 < c < 128 else " " for c in b ])








if __name__ == '__main__':

    app.run(host='127.0.0.1', port=6061, debug=True)
