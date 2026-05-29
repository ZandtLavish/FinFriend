import chainlit as cl
from langchain_core.messages import HumanMessage, AIMessage
import logging

from app.agent import app
from app.config_logging import configure_logging

configure_logging()
logger = logging.getLogger(__name__)

@cl.on_chat_start
def start_chat():
    logger.debug("Starting chat")
    cl.user_session.set("message_history", [])


@cl.on_message
async def on_message(message: cl.Message):
    logger.debug("Starting on-message response")
    history = cl.user_session.get("message_history")
    
    history.append(HumanMessage(content=message.content))
    
    result = await app.ainvoke({
        "messages": history, 
        "context": ""
    })
    
    response = result["messages"][-1].content
    
    history.append(AIMessage(content=response))
    
    cl.user_session.set("message_history", history)
    
    await cl.Message(content=response).send()