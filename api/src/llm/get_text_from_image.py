import base64
import openai
import os
import json
import time

from dotenv import load_dotenv

# start = time.time()

load_dotenv()
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

openai.api_key = OPENAI_API_KEY
client = openai.OpenAI()

def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')


def get_text_from_table(image_path):
    base64_image = encode_image(image_path)

    response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {
        "role": "user",
        "content": [
            {
            "type": "text",
            "text": "extract the data in this table in russian and kazakh languages and output into raw JSON, don't write a type of your answer, clear JSON",
            },
            {
            "type": "image_url",
            "image_url": {
                "url":  f"data:image/jpeg;base64,{base64_image}"
            },
            },
        ],
        }
    ],
    )
    result = response.choices[0].message.content

    cleaned_json_string = result.replace('```json', '').strip('```').strip()
    print(cleaned_json_string)
    
    data = json.loads(cleaned_json_string)
    return data
    # with open('result.json', 'w', encoding='utf-8') as f:
    #     json.dump(data, f, ensure_ascii=False, indent=4)

    # end = time.time()
    # print(f'execution: {end-start}')

if __name__ == '__main__':
    get_text_from_table('test_photos/2.png')