import requests
import os
from GlobalLink import ClassNames, api_key

def get_prompt(query):
    prompt = ""
    with open(os.path.join(ClassNames, 'prompt.txt'), 'r') as file:
        prompt = file.read()
        prompt = prompt + '\nSentence: \"' + query + "\""
    print(prompt, '\n*********\n')
    return prompt

def generate_response(query):
    reset_request = requests.post(
        'https://api.pawan.krd/resetip',
        headers = {"Authorization" : f"Bearer {api_key}"},
    )
    print(reset_request.json())
    if reset_request.ok:
        print("ipreset success\n")
    else:
        return "I'm sorry, I'm having trouble resetting ip."

    response = requests.post(
        "https://api.pawan.krd/v1/chat/completions",
        headers = {"Authorization" : f"Bearer {api_key}"},
        json={
            "model": "pai-001-light-beta",
            "max_tokens": 50,
            "temperature": 0.8,
            # "prompt": get_prompt(query),
            "messages" : [
                {"role": "user", "content": get_prompt(query)}
            ]
        },
    )

    print(response.json())
    if response.ok:
        result = response.json()["choices"][0]["message"]["content"].strip()   
        # result = response.json()["choices"][0]["text"].strip()   
        # print(result)
        return result
    else:
        return "I'm sorry, I'm having trouble generating a response right now."

if __name__ == "__main__":
    _request = input("Enter query: ")
    print(generate_response(_request))
