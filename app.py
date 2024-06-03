import chainlit as cl
import os
from langchain import HuggingFaceHub, PromptTemplate, LLMChain
from components.retriever import Retriever
from dotenv import load_dotenv
from langchain.memory import ConversationBufferMemory
from chainlit.types import ThreadDict
 
load_dotenv()
huggingfacehub_api_token = os.environ['HUGGINGFACEHUB_API_TOKEN']
repo_id = "mistralai/Mistral-7B-Instruct-v0.2"
llm = HuggingFaceHub(huggingfacehub_api_token=huggingfacehub_api_token,
                     repo_id=repo_id,
                     model_kwargs={"temperature":0.6, "max_new_tokens":500})
 
template = """
I want you to act as log analyzer Assistant  provide helpful, details of log answers with time stamps of recent logs for user's questions.
 
Context: {context}
Question: {question}
"""
retriever = Retriever.get_retriever()
 
@cl.password_auth_callback
def auth_callback(username: str, password: str):
    # Here you would typically query your database or some other service to verify the credentials
    # For demonstration purposes, I'm using hardcoded credentials
    if (username, password) == ("jeevitham@evertz.com", "admin"):
        return cl.User(
            identifier="admin", metadata={"role": "admin", "provider": "credentials"}
        )
    else:
        return None
 
@cl.on_chat_resume
async def on_chat_resume(thread: cl.ThreadDict):
    memory = ConversationBufferMemory(return_messages=True)
    root_messages = [m for m in thread["steps"] if m["parentId"] == None]
    for message in root_messages:
        if message["type"] == "user_message":
            memory.chat_memory.add_user_message(message["output"])
        else:
            memory.chat_memory.add_ai_message(message["output"])
 
    cl.user_session.set("memory", memory)
 
 
 
@cl.on_chat_start
async def main():
    # Store the initial prompt in the user session
    cl.user_session.set("initial_prompt", template)
    cl.user_session.set("memory", ConversationBufferMemory(return_messages=True))
    user = cl.user_session.get("user")
 
 
@cl.step
async def tool():
    # Simulate a running task
    await cl.sleep(2)
 
    return "Response from esGPT"
 
 
 
@cl.on_message
async def main(message):
    tool_res = await tool()
    memory = cl.user_session.get("memory")
    # Extract the message content if it's a Message object
    if isinstance(message, cl.message.Message):
        message_content = message.content
    else:
        message_content = message
 
    # Check if the message is of type str (string)
    if isinstance(message_content, str):
        # Retrieve the initial prompt from the user session
        initial_prompt = cl.user_session.get("initial_prompt")
       
        # Perform similarity search to retrieve relevant context from the database
        context = retriever.get_relevant_documents(message_content)
        print(context)
       
        input_text = ' '.join([doc.page_content.strip() for doc in context])
        print(input_text)
 
        # Instantiate the chain for that user session
        prompt_inputs = {"context": input_text, "question": message_content}
        prompt = PromptTemplate(template=initial_prompt, input_variables=["context", "question"])
        llm_chain = LLMChain(prompt=prompt, llm=llm, verbose=True)
 
        # Call the chain synchronously with the input dictionary
        response = llm_chain.invoke(input=prompt_inputs, callbacks=[cl.LangchainCallbackHandler()])
        print(response)
 
        # After extracting the LLM answer text from the dictionary
        llm_answer = response["text"]
 
        # Split the text by a separator to separate the context from the answer
        context_separator = "Question:"
        llm_answer_parts = llm_answer.split(context_separator)
 
        # Extract the answer part (assuming it's the second part after splitting)
        if len(llm_answer_parts) > 1:
            answer_text = llm_answer_parts[1].split("\n", 1)[1].strip()  # Split by newline and select the second part
        else:
            answer_text = llm_answer
 
        # Send the LLM answer
        await cl.Message(content=answer_text).send()
        memory.chat_memory.add_user_message(message_content)
        memory.chat_memory.add_ai_message(answer_text)
 
    else:
        # If the message is not a string, log an error or handle it appropriately
        print("Received message is not a string:", message_content)
 