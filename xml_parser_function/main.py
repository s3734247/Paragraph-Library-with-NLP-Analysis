import time
import json
import os
import re
from google.cloud import pubsub_v1
from google.cloud import storage
from google.cloud import logging
import untangle
import datetime
import pymysql

log_client = logging.Client()
logger = log_client.logger("cloudfunctions.googleapis.com%2Fcloud-functions")


project, downstream_topic, sql_connection, sql_user, sql_password, sql_database = \
    map(os.environ.get, ["GCP_PROJECT", "downstream_topic", "sql_connection", "sql_user", 
                        "sql_password", "sql_database"])


def store_author_RDS(d: dict) -> int:
    aid = -1
    sql = "insert into Author (blogger_id, gender, age, industry, astro_sign) values (%s, %s, %s, %s, %s)"
    vals = tuple(map(d.get, ["blogger_id", "gender", "age", "industry", "astro_sign"]))
    conn = None
    try:
        conn = pymysql.connect(user=sql_user, password=sql_password, database=sql_database,
                unix_socket="/cloudsql/{}".format(sql_connection))
    except Exception as e:
        logger.log_text("connection to cloud sql failed: {}".format(e))
        raise
    with conn.cursor() as cur:
        try:
            cur.execute(sql, vals)
        except Exception as e:
            logger.log_text("executing sql failed: {}".format(e))
            raise
        conn.commit()
        try:
            cur.execute("select last_insert_id() as id")
        except Exception as e:
            logger.log_text("executing sql failed: {}".format(e))
            raise
        try:
            aid = cur.fetchone()[0]
        except Exception as e:
            logger.log_text("fetchone failed: {}".format(e))
            raise
    conn.close()
    return aid


def parse_xml(data, context):
    CS = storage.Client()
    bucket = CS.bucket(data['bucket'])
    filepath = data['name']
    filename = os.path.split(filepath)[1]
    xmlblob = bucket.blob(filepath)
    b = xmlblob.download_as_string()
    s = to_en(b)
    s = preproc_xml(s)
    xml = untangle.parse(s)
    dates = xml.Blog.date
    posts = xml.Blog.post
    if not isinstance(posts, list):
        posts = [posts]
        dates = [dates]
    author_data = get_meta_from_filename(filename)
    author_id = store_author_RDS(author_data)
    downstream_post_id = 0
    batch_settings = pubsub_v1.types.BatchSettings(
        max_messages=100,  # default 100
        max_bytes=1024*8,  # default 1 MB
        max_latency=1,  # default 10 ms
    )    
    publisher = pubsub_v1.PublisherClient(batch_settings)
    for date, post in zip(dates, posts):
        post = post.cdata.strip()
        date = transform_date(date.cdata.strip())
        downstream_data = {
            "filename": filename, "author_id": author_id, "date": date.isoformat(),
            "post": post, "post_id": downstream_post_id
        }
        downstream_post_id += 1
        publish_messages_with_custom_attributes(publisher, project, downstream_topic, downstream_data)
    logger.log_text("{}/{} last post_id: {}".format(bucket, filepath, downstream_post_id - 1))
        


def to_en(b: bytes) -> str:
    return ''.join([chr(c) if 31 < c < 128 else " " for c in b ])

def preproc_xml(s: str) -> str:
    ncl = []
    for i in range(len(s)):
        if s[i] == '&' and not s[i:].startswith("&amp;") \
                and not s[i:].startswith("&lt;") \
                and not s[i:].startswith("&gt;") \
                and not s[i:].startswith("&quot;") \
                and not s[i:].startswith("&apos;"):
            ncl.append("&amp;")
        elif s[i] == "<" and not s[i:].startswith("<Blog>") \
                and not s[i:].startswith("</Blog>") \
                and not s[i:].startswith("<date>") \
                and not s[i:].startswith("</date>") \
                and not s[i:].startswith("<post>") \
                and not s[i:].startswith("</post>"):
            ncl.append("&lt;")
        elif s[i] == '>' and not s[:i+1].endswith("<Blog>") \
                and not s[:i+1].endswith("</Blog>") \
                and not s[:i+1].endswith("<date>") \
                and not s[:i+1].endswith("</date>") \
                and not s[:i+1].endswith("<post>") \
                and not s[:i+1].endswith("</post>"):
            ncl.append("&gt;")
        else:
            ncl.append(s[i])
    return "".join(ncl)
    

def transform_date(dateS: str) -> datetime.date:
    return datetime.datetime.strptime(dateS, "%d,%B,%Y").date()


def get_meta_from_filename(filename):
    i = filename.rfind(".xml")
    blogger_id, gender, age, industry, astro_sign = filename[:i].split(".")
    return {
        "blogger_id": int(blogger_id), "gender": gender, "age": int(age), "industry": industry,
        "astro_sign": astro_sign
    }

def get_callback(api_future, data: bytes):
    """Wrap message data in the context of the callback function."""
    def callback(api_future):
        try:
            logger.log_text(
                "Published message {} now has message ID {}".format(
                    data, api_future.result()
                )
            )
        except Exception:
            logger.log_text(
                "A problem occurred when publishing {}: {}\n".format(
                    data, api_future.exception()
                )
            )
            raise
    return callback


def publish_messages_with_custom_attributes(publisher, project_id, topic_name, data: dict):
    logger.log_text("publishing message {0}".format(data))
    topic_path = publisher.topic_path(project_id, topic_name)
    message = json.dumps(data)
    message_b = bytes(message, "utf-8")
    future = publisher.publish(topic_path, message_b)
    future.add_done_callback(get_callback(future, message_b))
    logger.log_text("publish-message task submitted: {}".format(data))
