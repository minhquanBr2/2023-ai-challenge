import requests
import os
from GlobalLink import ClassNames, api_key

def get_prompt():
    with open(os.path.join(ClassNames, 'prompt.txt'), 'r') as file:
        prompt = file.read()
    print(prompt, '\n\nAnswer: ')
    return prompt

def generate_response():
    response = requests.post(
        "https://api.pawan.krd/v1/chat/completions",
        headers = {"Authorization" : f"Bearer {api_key}"},
        json={
            "model": "pai-001-light-beta",
            "max_tokens": 50,
            "temperature": 0.1,
            "messages" : [
                {"role": "user", "content": get_prompt()}
            ]
        },
    )

    if response.ok:
        result = response.json()["choices"][0]["message"]["content"].strip()   
        return result
    else:
        return "I'm sorry, I'm having trouble generating a response right now."

if __name__ == "__main__":
    print(generate_response())
