
import requests

URL = "http://localhost:11434/api/chat"


def post_request(user_input, context):
    payload = {
        "model": "gemma3:4b",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are an executive assistant. "
                    "Answer using the supplied document context. "
                    "If the context does not contain the answer, "
                    "say that the available documents do not provide "
                    "enough information. Do not invent facts. "
                    "For short questions, answer in a few words. "
                    "For longer questions, use 50 to 100 words. "
                    "Always be sympathetic and formal."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Document context:\n{context}\n\n"
                    f"Question: {user_input}"
                )
            }
        ],
        "stream": False
    }

    response = requests.post(URL, json=payload, timeout=120)
    response.raise_for_status()
    return response.json()
