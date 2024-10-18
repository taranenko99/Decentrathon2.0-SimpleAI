import os
import json
import openai

import asyncio

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_community.vectorstores import FAISS
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.chains.retrieval import create_retrieval_chain
from langchain_core.prompts import MessagesPlaceholder

from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain.prompts.chat import ChatPromptTemplate


from dotenv import load_dotenv
from prompts import CLASSIFICATION_PROMPT

load_dotenv()

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
REDIS_URL=os.environ.get('REDIS_URL')


openai.api_key = OPENAI_API_KEY
client = openai.OpenAI()

def add_message_to_redis(ai_answer, user_query, telegram_id):
    chat_history_key = telegram_id
    
    chat_history_redis = RedisChatMessageHistory(session_id=chat_history_key,
                                                 url=REDIS_URL,
                                                 key_prefix='memory'
                                                 )
    
    chat_history_redis.add_user_message(user_query)
    chat_history_redis.add_ai_message(ai_answer)


def get_chain():
    model = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.4
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system","Ты ассистент гинеколог. Твоя задача задавать уточняющие вопросы пользователю из заметки гинеколога по проблеме пациента и помочь ему выявить причину проблемы. Если по ответам пациента можно понять, что ему очень плохо и такого быть не должно, то пиши слово ТРИГГЕР, или наоборот, если по ответам можно понять, что ничего страшного с пациентом не происходит, то пиши слово НОРМ.  А до тех пор задавай вопросы из заметок и также дополняй от себя. Если ответ пользователя не по теме, сообщи ему об этом. \nЗаметки гинеколога: {context}"),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "Ответ пользователя: {input}")
    ])

    chain = prompt | model

    return chain

def get_retrievers(pages):
    embeddings = OpenAIEmbeddings()

    bm25_retriever = BM25Retriever.from_texts(pages)
    bm25_retriever.k = 5

    faiss_vectorstore = FAISS.from_texts(pages, embeddings)
    faiss_retriever = faiss_vectorstore.as_retriever(search_kwargs={"k": 5})

    ensemble_retriever = EnsembleRetriever(retrievers=[bm25_retriever, faiss_retriever],weights=[0.6, 0.4])

    return ensemble_retriever


def binary_classify(text:str) -> json:
    '''Функция для генерации уточняющих вопрос пациенту
        text: Результат векторного поиска по самочувствию пациента
    '''
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": CLASSIFICATION_PROMPT},
            {"role": "user", "content": f'Ответ гинеколога: {text}'}
        ],
        temperature=0.6,
        max_tokens=2048,
    )
    
    answer = response.choices[0].message.content
    return json.loads(answer)

