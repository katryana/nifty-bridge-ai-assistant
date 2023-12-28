import os

import pinecone
from PyPDF2 import PdfReader
from dotenv import load_dotenv
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores.pinecone import Pinecone


def create_chunks_from_pdf(file_name: str):
    pdf = PdfReader(os.path.abspath(file_name))
    text = ""

    for page in pdf.pages:
        text += page.extract_text()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=700,
        chunk_overlap=200,
        length_function=len
    )
    texts = text_splitter.split_text(text)

    return texts


def create_vector_database(index_name: str, chunks: list, embed: OpenAIEmbeddings):
    if index_name not in pinecone.list_indexes():
        pinecone.create_index(
            name=index_name,
            metric="cosine",
            dimension=1536
        )

    return Pinecone.from_texts(chunks, embed, index_name=index_name)


if __name__ == "__main__":
    load_dotenv()
    chunks = create_chunks_from_pdf("NiftyBridge_info.pdf")

    pinecone.init(
        api_key=os.getenv("PINECONE_API_KEY"),
        environment=os.getenv("PINECONE_ENVIRONMENT")
    )

    embeddings = OpenAIEmbeddings(
        model="text-embedding-ada-002",
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )

    create_vector_database(os.getenv("PINECONE_INDEX_NAME"), chunks, embeddings)
