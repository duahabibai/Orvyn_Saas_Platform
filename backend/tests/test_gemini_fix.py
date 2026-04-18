import requests
import json

def test_gemini_openai_compatible():
    # Testing the EXACT configuration now in the code
    key = "AIzaSyCfdNJhuQBqn3szQFjnSbgSPI3agHNTBSU"
    url = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {key}'
    }
    data = {
        "model": "gemini-2.0-flash",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello, are you working through the OpenAI-compatible endpoint?"}
        ]
    }
    
    print(f"Testing Gemini OpenAI-compatible endpoint...")
    try:
        response = requests.post(url, headers=headers, json=data, verify=False)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            res_data = response.json()
            print(f"Response Content: {res_data['choices'][0]['message']['content']}")
        else:
            print(f"Error Response: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_gemini_openai_compatible()
