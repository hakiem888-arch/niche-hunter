import streamlit as st
import requests

def groq_analyze(prompt):

    key = st.secrets["GROQ_API_KEY"]

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        },
        json={
            "model": "llama-3.3-70b-versatile",
            "messages":[
                {
                    "role":"system",
                    "content":"Anda adalah YouTube strategist AI."
                },
                {
                    "role":"user",
                    "content":prompt
                }
            ]
        }
    )

    return response.json()["choices"][0]["message"]["content"]
