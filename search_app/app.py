import yaml
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

from flask import Flask
from google.cloud import logging
import sqlalchemy

envs = None
with open(".env.yaml", "rb") as fh:
    envs = yaml.load(fh, Loader=Loader)

sql_connection, sql_user, sql_database, sql_password = map(envs.get, 
        ["sql_connection", "sql_user", "sql_database", "sql_password"])

log_client = logging.Client()
logger = log_client.logger("search_app")


app = Flask(__name__)


# The SQLAlchemy engine will help manage interactions, including automatically
# managing a pool of connections to your database
db = sqlalchemy.create_engine(
    sqlalchemy.engine.url.URL(
        drivername="mysql+pymysql",
        username=sql_user,
        password=sql_password,
        database=sql_database,
        query={"unix_socket": "/cloudsql/{}".format(sql_connection)},
    ),
    pool_size=5,
    max_overflow=2,
    pool_timeout=30,  # 30 seconds
    pool_recycle=1800,  # 30 minutes
)

import routes