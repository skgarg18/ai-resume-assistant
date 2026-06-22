from fastapi import APIRouter
from schema.chat_schema import ChatRequest

from langchain_core.messages import (
    HumanMessage,
    AIMessage
)

from routers.chat_router.chains.workflow_type import workflow_router_chain

from routers.chat_router.workflows.chat_workflow import chat_workflow
from routers.chat_router.workflows.email_content_workflow import email_content_workflow

router = APIRouter()

@router.post("/api/{session_id}/chat")
async def chat(req: ChatRequest , session_id:str):


    # ---------------------
    # Chat History
    # ---------------------

    chat_history = [
        HumanMessage(content=m.content)
        if m.role == "user"
        else AIMessage(content=m.content)
        for m in req.chat_history
    ]
   
    

    workflow_response = workflow_router_chain.invoke({
        "message" : req.question , 
        "chat_history" : chat_history,
        })
    

    if workflow_response.workflow == "chat":
        return await chat_workflow(req.question , chat_history , workflow_response.referenced_candidates , session_id)
    
    elif workflow_response.workflow == 'email':
        return await email_content_workflow(req.question ,  workflow_response.referenced_candidates , session_id)
    

    return {
        "type" : "chat",
        "error" : "There was a error in generating response"
    }






