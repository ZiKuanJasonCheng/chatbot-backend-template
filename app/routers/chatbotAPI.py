from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
import numpy as np
import pandas as pd
from ..model_func import SentenceBert, calculate_similarity_index
from ..database.mysql_funcs import getAllQuestionEmbedding
from .. import config
from .. import logger

router = APIRouter()
logger_chatbotAPI = logger.setForWritefile("chatbotAPI", "app/logs/chatbotAPI.log")

df_data = pd.DataFrame()
arr_questions = np.array()

model = None
state = {
    "completed": "completed",
    "waitForFirstResponse": "waitForFirstResponse",
    "waitForSecondResponse": "waitForSecondResponse"
}

@router.on_event("startup")
async def startup_event():
    # Preload data
    global df_data, arr_questions, model
    df_data = getAllQuestionEmbedding(logger_chatbotAPI)
    arr_questions = df_data["question"].values()
    model = SentenceBert()


@router.on_event("shutdown")
async def shutdown_event():
    pass

@router.get("/chatbot/welcome")
async def welcome():
    text += "Hello! Welcome to ask me some questions! I will do my best to give you satisfactory responses!"
    return await responseReturn(uid=None, text=text, option=[], newState=None)


@router.get("/chatbot/reload")
async def ReloadData():
    """
        Manually reload embedded QA data
    """
    global df_data
    df_data = getAllQuestionEmbedding(logger_chatbotAPI)
    arr_questions = df_data["question"].values()
    return {"msg": "Reload successful"}

class userText(userInfo):
    uid: str = Field(..., min_length=1, max_length=15)
    ask_text: str = Field(..., title="Ask something to our bot ^^", min_length=1, max_length=250)
    state: str = Field(..., min_length=1, max_length=15)

@router.post("/chatbot/ask", dependencies=[Depends(startup_event)])
async def response(user: userText):
    uid = user.uid
    ask_text = user.ask_text
    state = user.state
    k = 7

    if (state == None) or (state == "Asking"):
        # Preproceed ask_text string
        ask_text = ask_text.lower().strip()
        # Remove some punctuations
        for punc in ["?", "？", "!", "！"]:
            if punc in ask_text:
                ask_text = ask_text.replace(punc, "")
        # Replace some punctuations
        for punc, punc_new in {",": "，", "(": "（", ")": "）"}.items():
            if punc in ask_text:
                ask_text = ask_text.replace(punc, punc_new)
        
        # Text to Embedding
        ask_emb = model([ask_text])

        # Calculate similarities between user input sentence and question banks
        idx_sorted, arr_similarities = calculate_similarity_index(target=ask_emb,
                                                                  pool=ask_text,
                                                                 )

        # Get an answer corresponding to the matched question
        text = df_data.iloc[idx_sorted[0]]["answer"]
        
        # If the top 1's similarity is 1, which exactly matches a question in our question bank
        if arr_similarities[idx_sorted[0]] == 1:
            # Set a new state
            newState = "Completed"
            return await responseReturn(uid=uid, text=text, option=[], newState=newState)
        # If the top 1's similarity is over the threshold
        elif arr_similarities[idx_sorted[0]] >= config.threshold:
            text = text + f"\nAre you satisfied with my response?"
            # Set a new state and option
            newState = "WaitingForFeedback"
            option = ["Yes", "No"]
            return await responseReturn(uid=uid, text=text, option=option, newState=newState)
        elif arr_similarities[idx_sorted[0]] >= config.second_threshold:
            text = f"Sorry, I'm not sure what you ask, so I find the following similar questions for you:\n"
            
            # Set a new state and option
            newState = "WaitingForSelection"
            # List top k similar questions for user to choose
            arr_topK_indices = idx_sorted[:k]
            option = arr_topK_indices.tolist()
            option.append("None of the above")

            text += "\n * ".join(arr_questions[arr_topK_indices].tolist())
            text += "* None of the above"

            return await responseReturn(uid=uid, text=text, option=option, newState=newState)
        else:  # arr_similarities[idx_sorted[0]] < config.second_threshold
            text = f"Sorry, I'm not clear what you ask, would you please change a way to ask your question."
            
            # Set a new state
            newState = "Asking"
            return await responseReturn(uid=uid, text=text, option=[], newState=newState)
    elif state == "WaitingForSelection":
        # ask_text should be a string number indicating an index of a question, or "None of the above"
        if ask_text == "None of the above":
            text = f"I'm sorry that my response couldn't help you. Please forgive me that I'm still learning to be a better assistant."
        else:
            idx = int(ask_text)
            text = df_data.iloc[idx]["answer"]
        
        newState = "Completed"
        return await responseReturn(uid=uid, text=text, option=[], newState=newState)
    else:  # state == "WaitingForFeedback"
        # ask_text should be "Yes" or "No"
        if ask_text == "Yes":
            text = f"Thanks for your positive feedback!"
        else:  # ask_text == "No"
            text = f"I'm sorry that my response couldn't help you. Please forgive me that I'm still learning to be a better assistant."
        
        newState = "Completed"
        return await responseReturn(uid=uid, text=text, option=[], newState=newState)


async def responseReturn(uid, text, option, newState):
    return {
        "user": uid,
        "text": text,
        "option": option,
        "newState": newState
    }