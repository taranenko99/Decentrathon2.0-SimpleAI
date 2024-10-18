import uuid

from generation import *
from vector_db.utils import create_vector_db

chat_history_key = str(uuid.uuid4())
chat_history_redis = RedisChatMessageHistory(session_id=chat_history_key,
                                                url=REDIS_URL,
                                                key_prefix='memory'
                                                )

chat_chain = get_chain()

a = 0

embeddings = OpenAIEmbeddings()

query = input('Как ваше самочувствие? ')
db = FAISS.load_local(r"faiss_index", embeddings, allow_dangerous_deserialization=True)
# create_vector_db(r'vector_db/symptoms.txt')
retriever = db.as_retriever()
docs = retriever.invoke(query)
context = docs[0].page_content
# print(context)


while True:
    if a == 0:
        response = chat_chain.invoke({"input": query,'context':context, 'chat_history':chat_history_redis.messages[-5:]})
        answer = response.content
        add_message_to_redis(ai_answer=answer, user_query=query,telegram_id=chat_history_key)
        print(response.content)
        a = 1
    else:
        query_b = input('your answer: ')
        response = chat_chain.invoke({"input": query_b,'context':context, 'chat_history':chat_history_redis.messages[-5:]})
        answer = response.content
        
        status_answer = binary_classify(answer)
        
        result = {'text':answer,'status':status_answer}
        print(result)

        add_message_to_redis(ai_answer=answer, user_query=query,telegram_id=chat_history_key)
        
        # print(response.content)