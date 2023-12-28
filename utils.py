import os

import pinecone
import tiktoken
from dotenv import load_dotenv
from fastapi import HTTPException, Depends
from fastapi.security import APIKeyHeader
from langchain_community.embeddings import OpenAIEmbeddings
from pydantic import BaseModel

load_dotenv()
FAST_API_KEY = os.getenv("FAST_API_KEY")


class Query(BaseModel):
    message: str


def set_pinecone_connection():
    pinecone.init(
        api_key=os.getenv("PINECONE_API_KEY"),
        environment=os.getenv("PINECONE_ENVIRONMENT")
    )


def get_embeddings() -> OpenAIEmbeddings:
    return OpenAIEmbeddings(
        model="text-embedding-ada-002",
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )


api_key_header = APIKeyHeader(name="X-API-KEY-Token")


def get_api_key(fast_api_key: str = Depends(api_key_header)):
    if fast_api_key == FAST_API_KEY:
        return fast_api_key
    else:
        raise HTTPException(
            status_code=403, detail="Invalid API key"
        )


def calculate_tokens(text: str) -> int:
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    num_tokens = len(encoding.encode(text))
    return num_tokens


def validate_token_length(query: str):
    max_token_length = 4097
    message_tokens = calculate_tokens(query)

    if message_tokens > max_token_length:
        raise HTTPException(
            status_code=400,
            detail="Message exceeds the maximum context"
                   f" length of {max_token_length} tokens."
        )
