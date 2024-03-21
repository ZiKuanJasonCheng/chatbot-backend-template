from logging import Logger
from typing import List, Tuple, Dict
import json
from .. import config
import pymysql
from contextlib import contextmanager
from fastapi import HTTPException
import pandas as pd

@contextmanager
def mysql_conn():
    """
        Create a MySQL connection object
    """
    try:
        conn = pymysql.connect(host=config.mysql["host"],
                               user=config.mysql["user"],
                               password=config.mysql["password"],
                               database=config.mysql["database"],
                               cursorclass=pymysql.cursors.DictCursor,
                            )
    except:
        raise HTTPException(424 , "Failed to connect to MySQL database")
    try:
        yield conn
    finally:
        conn.close()

def createQuestionAnswer(
        questions: List[str],
        answer: str,
        logger: Logger,
    ):
    """
        Insert a QA then return last ID of the table
        Inputs:
            questions (list): A list of similar questions belonging to the same answer
            answer (str): Answer to the question
            logger (Logger): A logging object for logging errors
        Returns:
            id (str): Last ID in the table
            None if there is an error
    """
    try:
        with mysql_conn() as mysql:
            # SQL command for inserting new data
            sql = f"""
                    insert into {config.mysql["table-QA"]}
                    (question,answer) values (%(question)s,%(answer)s);
                    """

            # Dump a list of questions to json format
            question = json.dumps(question)
                
            # Create a cursor
            cursor = mysql.cursor()
            # Execute SQL command
            cursor.execute(sql, {"question": questions, "answer": answer})
            
            # Fetch id
            sql = """
                    SELECT LAST_INSERT_ID();
                """   
            cursor.execute(sql)
            mysql.commit()
            # Fetch last id
            id = cursor.fetchall()[0]['LAST_INSERT_ID()']
            # Close the cursor
            cursor.close()
        return id
    except:
        logger.exception("An error occurred while inserting a row into QA table")
        return None

def getQuestionAnswer(
        id: int,
        logger: Logger,
    ):
    """
        Get all question-answer pairs
        Inputs:
            id (int): ID of a QA pair
            logger (Logger): A logging object for logging errors
        Returns:
            list_data (list): A list of dictionaries containing all QA pairs
            False if there is an error
    """
    try:
        with mysql_conn() as conn:
            sql = f"""SELECT * FROM {config.mysql["table-QA"]} WHERE id={id}"""
            
            # Check if the connection works
            conn.ping(reconnect=True)
            # Create a cursor
            cursor = conn.cursor()
            # Execute SQL command
            cursor.execute(sql)
            # Fetch all data
            data = cursor.fetch()
            # Close the cursor
            cursor.close()
        return data
    except:
        logger.exception("An error occurred while fetching all data from QA table")
        return False
    
def updateQuestionAnswer(
        id: int,
        questions: List[str],
        answer: str,
        logger: Logger,
    ):
    """
        Update a certain question-answer pair by id
        Inputs:
            id (int): ID of a QA pair
            questions (list): A list of similar questions belonging to the same answer
            answer (str): Answer to the question
            logger (Logger): A logging object for logging errors
        Returns:
            True if the data is successfully updated
            False if there is an error

    """
    try:
        with mysql_conn() as mysql:
            # SQL command for updating an existing data
            sql = f"""
                    UPDATE {config.mysql["table-QA"]}
                    SET question=%(question)s, answer=%(answer)s
                    WHERE id=%(id)s
                    """
            # Dump a list of questions to json format
            question = json.dumps(question)
                
            # Create a cursor
            cursor = mysql.cursor()
            # Execute SQL command
            cursor.execute(sql, {"id": id, "question": questions, "answer": answer})
            mysql.commit()
            # Close the cursor
            cursor.close()
        return True
    except:
        logger.exception("An error occurred while updating a data into QA table")
        return False

def deleteQuestionAnswer(
        id: int,
        logger: Logger
    ):
    """
        Delete a certain question-answer pair by id
        Inputs:
            id (int): ID of a QA pair
            logger (Logger): A logging object for logging errors
        Returns:
            True if the data is successfully deleted
            False if there is an error
    """
    try:
        with mysql_conn() as mysql:
            # SQL command for deleting an existing data
            sql = f"""
                    DELETE FROM {config.mysql["table-QA"]} WHERE id={id}
                    """
            # Create a cursor
            cursor = mysql.cursor()
            # Execute SQL command
            cursor.execute(sql)
            mysql.commit()
            # Close the cursor
            cursor.close()
        return True
    except:
        logger.exception("An error occurred while deleting a data from QA table")
        return False
    
def deleteAllQuestionAnswer(logger: Logger):
    """
        Delete all question-answer pairs
        Inputs:
            logger (Logger): A logging object for logging errors
        Returns:
            True if the data is successfully deleted
            False if there is an error
    """
    try:
        with mysql_conn() as mysql:
            # SQL command for deleting all data
            sql = f"""
                    TRUNCATE {config.mysql["table-QA"]}
                    """
            # Create a cursor
            cursor = mysql.cursor()
            # Execute SQL command
            cursor.execute(sql)
            mysql.commit()
            # Close the cursor
            cursor.close()
        return True
    except:
        logger.exception("An error occurred while deleting all data from QA table")
        return False

def getAllQuestionAnswer(
        logger: Logger,
    ):
    """
        Get all question-answer pairs
        Inputs:
            logger (Logger): A logging object for logging errors
        Returns:
            list_data (list): A list of dictionaries containing all QA pairs
            False if there is an error
    """
    try:
        with mysql_conn() as conn:
            sql = f"""SELECT * FROM {config.mysql["table-QA"]}"""
            
            # Check if the connection works
            conn.ping(reconnect=True)
            # Create a cursor
            cursor = conn.cursor()
            # Execute SQL command
            cursor.execute(sql)
            # Fetch all data
            list_data = cursor.fetchall()
            # Close the cursor
            cursor.close()
        return list_data
    except:
        logger.exception("An error occurred while fetching all data from QA table")
        return False

def getAllQuestionEmbedding(
        logger: Logger,
    ):
    """
        Get all question-embedding-answer pairs
        Inputs:
            table (str): Table name; default is questionEmbedding
            logger (Logger): A logging object for logging errors
        Returns:
            df_data (DataFrame): A DataFrame containing all QA embedding pairs
            False if there is an error
    """
    try:
        with mysql_conn() as conn:
            sql = f"""SELECT * FROM {config.mysql["table-QA-emb"]}"""
            
            # Check if the connection works
            conn.ping(reconnect=True)
            # Create a cursor
            cursor = conn.cursor()
            # Execute SQL command
            cursor.execute(sql)
            # Fetch all data
            list_data = cursor.fetchall()
            # Close the cursor
            cursor.close()
        return pd.DataFrame(list_data)
    except:
        logger.exception("An error occurred while fetching all data from QA embedding table")
        return False


def createQuestionEmbedding(
        list_data: List[Dict],
        logger: Logger
    ):
    """
        Insert Question embeddings
        Inputs:
            list_data (list): A list of dictionaries of question and answers
            logger (Logger): A logging object for logging errors
        Returns:
            True if data are successfully inserted into the table
            False otherwise
    """
    try:
        with mysql_conn() as mysql:
            # SQL command for inserting new data
            sql = f"""
                    insert into {config.mysql['table-QA']}
                    (qid,question,answer,question_emb) values (%(qid)s,%(question)s,%(answer)s,%(question_emb)s);
                    """
                
            # Create a cursor
            cursor = mysql.cursor()
            # Execute SQL command
            cursor.executemany(sql, list_data)
        return True
    except:
        logger.exception("An error occurred while inserting data into QA embedding table")
        return False
    

def deleteQuestionEmbedding(
        qid: int,
        logger: Logger
    ):
    """
        Delete Question embeddings given qid
        Note: All questions related to one same answer will be deleted
        Inputs:
            qid (int): Question ID from QA table
            logger (Logger): A logging object for logging errors
        Returns:
            True if data are successfully deleted from the table
            False otherwise
    """
    try:
        with mysql_conn() as mysql:
            # SQL command for deleting data
            sql = f"""
                    DELETE FROM {config.mysql['table-QA-emb']}
                    WHERE qid={qid};
                    """
                
            # Create a cursor
            cursor = mysql.cursor()
            # Execute SQL command
            cursor.execute(sql)
        return True
    except:
        logger.exception("An error occurred while deleting data from QA embedding table")
        return False