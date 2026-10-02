
import os
import requests

def groq_analyze(prompt):
    key = os.getenv("GROQ_API_KEY")
    if not key:
        return "GROQ_API_KEY belum tersedia."

    r = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        },
        json={
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role":"system","content":"Anda adalah YouTube strategist AI."},
                {"role":"user","content":prompt}
            ]
        },
        timeout=60
    )

    if r.status_code == 200:
        return r.json()["choices"][0]["message"]["content"]

    return "AI gagal memberikan jawaban."

def video_insight(video):
    return groq_analyze(str(video))
