import os

# Main configs
mode = os.environ["MODE"]
top = 7
threshold = 0.9
second_threshold = 0.8

# latest Question and Answer excel
QADB = f"/app/app/QA.xlsx"

# test
class test_user:
    uid = "test-uid"
    test_acc = {"admin": "12345678"}

# database 
## redis
aioredis_redis = {"address": ("redis", 6379), "password": os.environ["REDIS_LOGIN_PWD"]}
## mysql
mysql = {"host": "mysql", "user": "root", "password": os.environ["MYSQL_LOGIN_PWD"], "database": "chatbot",
         "table-QA": "questionAnswer",
         "table-QA-emb": "questionEmbedding"
}

APP_IP = os.environ["APP_IP"] + ":" + os.environ["APP_PORT"]
UI_IP = os.environ["UI_IP"] + ":" + os.environ["UI_PORT"]
