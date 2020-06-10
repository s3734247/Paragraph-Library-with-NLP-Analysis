import os
import time
import json
import datetime
import base64
import pymysql
from google.cloud import pubsub_v1
from google.cloud import logging
from google.cloud import storage
from google.cloud import tasks_v2
from google.protobuf import timestamp_pb2



log_client = logging.Client()
logger = log_client.logger("cloudfunctions.googleapis.com%2Fcloud-functions")


project, downstream_bucket, downstream_topic,queue,location = map(os.environ.get,
        ["project", "downstream_bucket", "downstream_topic","queue","location"])
sql_connection, sql_user, sql_database, sql_password = map(os.environ.get,
        ["sql_connection", "sql_user", "sql_database", "sql_password"])


def store_paragraph(event, context):
    dataJ = base64.b64decode(event['data']).decode('utf-8')
    logger.log_text("dataJ {}".format(dataJ))
    data = json.loads(dataJ)
    logger.log_text("received data {}".format(data))
    author_id, filename, post_id, dateS, post = map(data.get, ["author_id", "filename", "post_id", "date", "post"])
    date = datetime.date.fromisoformat(dateS)
    ds_bucket_name = downstream_bucket
    ds_file_path = "{}.{}.txt.{}".format(filename, post_id, time.time())
    logger.log_text("ds_file_path {}".format(ds_file_path))
    upload_paragraph(post, ds_bucket_name, ds_file_path)
    rds_data = {
        "author_id": author_id,
        "bucket_path": "{}/{}".format(ds_bucket_name, ds_file_path),
        "publish_date": date
    }
    post_rds_id = store_post_RDS(rds_data)
    task_data = {
        "post_rds_id": post_rds_id,
        "bucket_path": "{}/{}".format(ds_bucket_name, ds_file_path)
    }
    mess1= str(task_data)
    asds=creat_task(mess1)
    logger.log_text("post_rds_id {}".format(post_rds_id))


    # TODO: publish to cloud tasks


def store_post_RDS(d: dict) -> int:
    logger.log_text("storing post to RDS: {}".format(d))
    pid = -1
    sql = "insert into Post (author_id, publish_date, bucket_path) values (%s, %s, %s)"
    vals = (d["author_id"], d["publish_date"], d["bucket_path"])
    logger.log_text("vals {}".format(vals))
    conn = pymysql.connect(user=sql_user, password=sql_password, database=sql_database,
            unix_socket="/cloudsql/{}".format(sql_connection))
    with conn.cursor() as cur:
        cur.execute(sql, vals)
        conn.commit()
        cur.execute("select last_insert_id()")
        pid = cur.fetchone()[0]
    conn.close()
    return pid


def upload_paragraph(content, bucket_name, object_path):
    logger.log_text("uploading paragraph bucket {2} content {1} object_path {0}".format(object_path, content, bucket_name))
    gcs = storage.Client()
    bucket = gcs.get_bucket(bucket_name)
    blob = bucket.blob(object_path)
    blob.upload_from_string(content)
    logger.log_text("successfully uploaded {}/{}".format(bucket_name, object_path))

def creat_task(rds_data):
    # Create a client.
    client = tasks_v2.CloudTasksClient()
    #TODO Task target
    #For example : url = 'http://35.201.14.192:8080/NLP_to'
    url = 'TODO'
    payload = rds_data
    task_name=None
    in_seconds=None
    parent = client.queue_path(project, location, queue)

    # Construct the request body.
    task = {
            'http_request': {  # Specify the type of request.
                'http_method': 'POST',

                'headers': {
                   'Content-Type': 'application/json'
                  },

                'url': url  # The full url path that the task will be sent to.
            }
    }
    if payload is not None:
        # The API expects a payload of type bytes.

        converted_payload = payload.encode()

        # Add the payload to the request.
        task['http_request']['body'] = converted_payload
        #task['http_request']['body'] = payload

    if in_seconds is not None:
        # Convert "seconds from now" into an rfc3339 datetime string.
        d = datetime.datetime.utcnow() + datetime.timedelta(seconds=in_seconds)

        # Create Timestamp protobuf.
        timestamp = timestamp_pb2.Timestamp()
        timestamp.FromDatetime(d)

        # Add the timestamp to the tasks.
        task['schedule_time'] = timestamp

    if task_name is not None:
        # Add the name to tasks.
        task['name'] = task_name

    # Use the client to build and send the task.
    response = client.create_task(parent, task)

    print('Created task {}'.format(response.name))
    return response
