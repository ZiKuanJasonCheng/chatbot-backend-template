from . import config
from contextlib import contextmanager
import pymysql

# Used for the first time when the database is not created yet.
# For other circumstances, use mysql_conn() from mysql_funcs.py
@contextmanager
def mysql_conn():
    try:
        conn = pymysql.connect(host=config.mysql["host"],
                               user=config.mysql["user"],
                               password=config.mysql["password"],
                               cursorclass=pymysql.cursors.DictCursor,
                            )
    except:
        raise Exception("Failed to connect to MySQL")
    try:
        yield conn
    finally:
        conn.close()

# connect to db
with mysql_conn() as db:
    cursor = db.cursor()
    # check database if exists
    if not cursor.execute(f"SHOW DATABASES like '{config.mysql['database']}'"):
        # create "chatbot" database if database doesn't not exist 
        print(f"create {config.mysql['database']} database")
        cursor.execute("CREATE DATABASE IF NOT EXISTS " + config.mysql["database"])
        print(f"create {config.mysql['database']} done")
    else:
        print(f"{config.mysql['database']} database exists.")

    # select "chatbot" database
    print(f"select {config.mysql['database']} database")
    db.select_db(config.mysql["database"])

    # Create a table: QAdata
    table = config.mysql["table-QA"]
    print(f"set up table : {table}")
    try:
        cursor.execute(f"SELECT 1 FROM {table} LIMIT 1;")
        print(f"table {table} exists.")
    except pymysql.err.ProgrammingError as e:
        if e.args[0] == 1146:
            print(e.args)
            # SQL command for creating a table
            sql = f"""CREATE TABLE {table} (
                    id BIGINT NOT NULL AUTO_INCREMENT,
                    PRIMARY KEY (id),
                    question JSON NOT NULL,
                    answer TEXT NOT NULL
                    )"""
            cursor.execute(sql)
            print(f"table: {table} created successfully.")
        else :
            print(f"table: {table} created unsuccessfully.")

    
    # Create a table: QA embedded questions
    table = config.mysql["table-QA-emb"]
    print(f"set up table : {table}")
    try:
        cursor.execute(f"SELECT 1 FROM {table} LIMIT 1;")
        print(f"table {table} exists.")
    except pymysql.err.ProgrammingError as e:
        if e.args[0] == 1146:
            print(e.args)
            # sql for create table
            sql = f"""CREATE TABLE {table} (
                    id BIGINT NOT NULL AUTO_INCREMENT,
                    PRIMARY KEY (id),
                    qid BIGINT NOT NULL,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    question_emb JSON NOT NULL
                    )"""
            cursor.execute(sql)
            print(f"table: {table} created successfully.")
        else :
            print(f"table: {table} created unsuccessfully.")

