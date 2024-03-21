import os
import requests
import json
import pickle
from pydantic import BaseModel, Field  #HttpUrl
from fastapi import APIRouter  #Body, Query, Path, Depends, HTTPException
from typing import List  #Set, Dict, Optional
from .. import logger
from ..database.mysql_funcs import getQuestionAnswer, getAllQuestionAnswer, createQuestionAnswer, createQuestionEmbedding, createQuestionEmbedding, updateQuestionAnswer, deleteQuestionAnswer, deleteAllQuestionAnswer, deleteQuestionEmbedding
from model_func import SentenceBert

router = APIRouter()
logger_qaAdmin = logger.setForWritefile("QA_manage", "app/logs/QA_manage.log")

@router.on_event("startup")
async def startup_event():
    await checkQA()
    
@router.on_event("shutdown")
async def shutdown_event():
    pass

@router.get("/check")
async def checkQA():
    """
        Check if there are QA data in our database. If not, insert some default data.
    """
    data = getAllQuestionAnswer(logger_qaAdmin)
    if data == False:
        return {"msg": "An error occurred while fetching all data from QA table"}
    elif len(data) == 0:
        list_toy_data = [
            QA_params(question=["Where is the gym?", "Wanna go exercise", "Is there a gym?", "Go for a treadmill workout"], answer="Please go to building A and the gym is at the basement 1"),
            QA_params(question=["Q2", "Q2-2", "Q2-3"], answer="Answer2"),
            QA_params(question=["Q3", "Q3-2"], answer="Answer3"),
            QA_params(question=["Q4", "Q4-2", "Q4-3", "Q4-4"], answer="Answer4"),
            QA_params(question=["Q5", "Q5-2", "Q5-3", "Q5-4"], answer="Answer5")
        ]
        for item in list_toy_data:
            response = await createQA(item)
            print(f"response: {response}") 


@router.get("/QA")
async def getTotalQA():  #conn: pymysql.Connection=Depends(mysql_conn)
    """
        Fetch all QA pairs
    """
    data = getAllQuestionAnswer(logger_qaAdmin)
    if data == False:
        return {"msg": "An error occurred while fetching all data from QA table"}
    return data

@router.get("/QA/{id}")  #deprecated=True
async def getQAbyId(id: int):  #conn: pymysql.Connection=Depends(mysql_conn)
    """
        Fetch a certain QA pair given id
    """
    data = getQuestionAnswer(id, logger_qaAdmin)
    if data == False:
        return {"msg": "An error occurred while fetching a data from QA table"}
    return data
    

class QA_params(BaseModel):
    question: List[str] = Field(..., min_length=1)
    answer: str = Field(..., min_length=1)

@router.post("/QA")
async def createQA(params: QA_params):  #conn: pymysql.Connection=Depends(mysql_conn)
    """
        create a new QA pair and return the id of that new question (or a set of similar questions)
    """
    if len(params.question) == 0:
        return {"msg": "Error: At least one question must be provided in a question list!"}
    
    list_q = []  # Will append processed questions
    # Preproceed a list of questions
    for q in params.question:
        q = q.lower().strip()
        # Remove some punctuations
        for punc in ["?", "？", "!", "！"]:
            if punc in q:
                q = q.replace(punc, "")
        # Replace some punctuations
        for punc, punc_new in {",": "，", "(": "（", ")": "）"}.items():
            if punc in q:
                q = q.replace(punc, punc_new)

        list_q.append(q)
    
    id = createQuestionAnswer(list_q, params.answer, logger_qaAdmin)
    if id is None:
        return {"msg": "An error occurred while inserting a row into QA table"}


    model = SentenceBert()
    # Embed questions
    arr_q_embedded = model(list_q)
    
    list_data = [{"qid": id, "question": q, "answer": params.answer, "question_embed": json.dumps(arr_q_embedded)} for q in list_q]

    status = createQuestionEmbedding(list_data, logger_qaAdmin)
    if not status:
        return {"msg": "An error occurred while inserting data into QA embedding table"}

    # Reload data
    try:
        response = requests.get(f"http://{os.getenv('LOCALHOST')}:80/chatbot/hr/ReLoad")
        logger_qaAdmin.info(f"response: {response}, r.text: {response.text}")
    except:
        logger_qaAdmin.exception("Something goes wrong while sending a request to API 'ReLoad'")
        return {"msg": "An error occurred while reloading data from tables"}

    return {"msg": "success", "Question ID": id}

@router.patch("/QA/{id}")
async def updateQA(id: int, params: QA_params):
    id = str(id)
    if len(params.question) == 0:
        return {"msg": "Error: At least one question must be provided in a question list!"}

    # Check if given id exists in QA table
    data = getQuestionAnswer(id)
    if data == False:
        return {"msg": "An error occurred while fetching a data from QA table"}
    elif data == None:
        return {"msg": "Given id does not exist in QA table!"}
    
    list_q = []  # Will append processed questions
    # Preproceed a list of questions
    for q in params.question:
        q = q.lower().strip()
        # Remove some punctuations
        for punc in ["?", "？", "!", "！"]:
            if punc in q:
                q = q.replace(punc, "")
        # Replace some punctuations
        for punc, punc_new in {",": "，", "(": "（", ")": "）"}.items():
            if punc in q:
                q = q.replace(punc, punc_new)

        list_q.append(q)

    
    status = updateQuestionAnswer(id, list_q, params.answer, logger_qaAdmin)
    if not status:
        return {"msg": "An error occurred while updating data into QA table"}


    model = SentenceBert()
    # Embed questions
    arr_q_embedded = model(list_q)
    list_ques_embedded = []
    for Q, embedded in zip(list_q, arr_q_embedded):
        list_ques_embedded.append(Q)
        list_ques_embedded.append(pickle.dumps(embedded))

    # Delete all questions related to the same answer in the QA embedding table
    status = deleteQuestionEmbedding(qid=id, logger=logger_qaAdmin)
    if not status:
        return {"msg": "An error occurred while deleting data from QA embedding table"}
    
    # Then insert newly embedded contents
    list_data = [{"qid": id, "question": q, "answer": params.answer, "question_embed": json.dumps(arr_q_embedded)} for q in list_q]
    status = createQuestionEmbedding(list_data, logger_qaAdmin)
    if not status:
        return {"msg": "An error occurred while inserting data into QA embedding table"}

    # Reload data
    try:
        response = requests.get(f"http://{os.getenv('LOCALHOST')}:80/chatbot/hr/ReLoad")
        logger_qaAdmin.info(f"response: {response}, response.text: {response.text}")
    except:
        logger_qaAdmin.exception("Something goes wrong while sending a request to API 'ReLoad'")
        return {"msg": "An error occurred while reloading data from tables"}

    return {"msg": "success"}


@router.delete("/QA/{id}")
async def deleteQA(id: int):
    status = deleteQuestionAnswer(id)
    if not status:
        return {"msg": "An error occurred while deleting a data from QA table"}
    # Reload data
    try:
        response = requests.get(f"http://{os.getenv('LOCALHOST')}:80/chatbot/hr/ReLoad")
        logger_qaAdmin.info(f"response: {response}, response.text: {response.text}")
    except:
        logger_qaAdmin.exception("Something goes wrong while sending a request to API 'ReLoad'")
        return {"msg": "An error occurred while reloading data from tables"}
    return {"msg": "success"}

@router.post("/QA/all")
async def deleteAllQA():
    status = deleteAllQuestionAnswer(logger_qaAdmin)
    if not status:
        return {"msg": "An error occurred while deleting all data from QA table"}

    # Reload data
    try:
        response = requests.get(f"http://{os.getenv('LOCALHOST')}:80/chatbot/hr/ReLoad")
        logger_qaAdmin.info(f"response: {response}, response.text: {response.text}")
    except:
        logger_qaAdmin.exception("Something goes wrong while sending a request to API 'ReLoad'")
        return {"msg": "An error occurred while reloading data from tables"}
    return {"msg": "success"}

