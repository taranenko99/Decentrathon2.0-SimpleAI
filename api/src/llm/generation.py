import os
import json
import openai
import redis
from loguru import logger

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import MessagesPlaceholder

from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain.prompts.chat import ChatPromptTemplate
from sqlalchemy import insert, select
from src.settings.base import session

from dotenv import load_dotenv
from src.db.models import PatientTests, Patients
from src.llm.prompts import CLASSIFICATION_PROMPT, SUMMARY_ANALYSIS, GINEKOLOGY_PROMPT


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
        ("system",GINEKOLOGY_PROMPT),
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
        temperature=0.0,
        max_tokens=2048,
    )
    
    answer = response.choices[0].message.content
    return answer


def generate_summary_of_analysis(analysis_json):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SUMMARY_ANALYSIS},
            {"role": "user", "content": f'Анализ в JSON: {analysis_json}'}
        ],
        temperature=0.4,
        max_tokens=2048,
    )
    
    answer = response.choices[0].message.content
    return answer

r = redis.Redis(host='localhost', port=6379, db=0)

def is_memory_empty(telegram_id: str) -> bool:
    """Проверяет, пустой ли ключ в Redis."""
    value = r.lrange(f'memory{telegram_id}', 0, -1)  # Получаем значение по ключу
    print(value)
    if value == []:
        return True
    else:
        return False


embeddings = OpenAIEmbeddings()

async def get_analysis(telegram_id: int):
    try:
        query = select(Patients).where(Patients.telegram_id == int(telegram_id))
        async with session() as conn:
            result = await conn.execute(query)
            temp = result.scalars().one_or_none()
        
        analysis_result = ""
        for j in temp.tests:
            analysis = generate_summary_of_analysis(j.data)
            analysis_result = analysis_result + analysis
        return analysis_result
    
    except Exception as e:
        logger.error(e)
        
async def qa(user_query, telegram_id):
    chat_history_redis = RedisChatMessageHistory(session_id=telegram_id,
                                                    url=REDIS_URL,
                                                    key_prefix='memory'
                                                    )
    
    chat_chain = get_chain()
    db_vector = FAISS.load_local(r"faiss_index", embeddings, allow_dangerous_deserialization=True)
    retriever = db_vector.as_retriever()
    docs = retriever.invoke(user_query)
    context = docs[0].page_content
    
    
    analysis = await get_analysis(telegram_id)
    empty = is_memory_empty(telegram_id=telegram_id)
    print(empty)
    if empty:
        
        response = chat_chain.invoke({"input": user_query,'context':context, 'chat_history':chat_history_redis.messages[-5:], 'analysis': analysis})
        answer = response.content
        add_message_to_redis(ai_answer=answer, user_query=user_query,telegram_id=telegram_id)

        
        result = {'bot_message':answer,'trigger':0}
        return result
        
    else:
        response = chat_chain.invoke({"input": user_query,'context':context, 'chat_history':chat_history_redis.messages[-5:], 'analysis': analysis})
        answer = response.content
        add_message_to_redis(ai_answer=answer, user_query=user_query,telegram_id=telegram_id)
        status_answer = binary_classify(answer)
        
        result = {'bot_message':answer,'trigger':status_answer}
        return result

if __name__ == '__main__':
    with open('result.json','r',encoding='utf-8') as f:
        data = f.read()
    rs =generate_summary_of_analysis(data)
    print(rs)