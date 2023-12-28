import os

from fastapi import FastAPI, Depends

from langchain.chains import RetrievalQA
from langchain_community.chat_models import ChatOpenAI
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores.pinecone import Pinecone

from utils import (
    get_api_key,
    get_embeddings,
    set_pinecone_connection,
    validate_token_length,
    Query
)
from chatbot.prompts import QA_CHAIN_PROMPT

app = FastAPI()


@app.post("/api/send/")
async def send_message_to_ai(
    query: Query,
    api_key: str = Depends(get_api_key),
    embeddings: OpenAIEmbeddings = Depends(get_embeddings),
    pinecone_connection=Depends(set_pinecone_connection)
):
    validate_token_length(query.message)

    chain = RetrievalQA.from_chain_type(
        llm=ChatOpenAI(
            openai_api_key=os.getenv("OPENAI_API_KEY")
        ),
        retriever=Pinecone.from_existing_index(
            index_name=os.getenv("PINECONE_INDEX_NAME"),
            embedding=embeddings,
        ).as_retriever(),
    )

    prompt = QA_CHAIN_PROMPT.format_prompt(
        query=query,
    )

    return {"message": chain.run(prompt.to_string())}
