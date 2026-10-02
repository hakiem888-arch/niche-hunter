import streamlit as st
import requests


def get_available_models():

    key = st.secrets["GROQ_API_KEY"]

    r = requests.get(
        "https://api.groq.com/openai/v1/models",
        headers={
            "Authorization": f"Bearer {key}"
        },
        timeout=30
    )

    if r.status_code == 200:
        return [
            x["id"]
            for x in r.json()["data"]
        ]

    return []


def groq_analyze(prompt):

    key = st.secrets["GROQ_API_KEY"]

    models = [
        "openai/gpt-oss-20b",
        "openai/gpt-oss-120b",
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant"
    ]


    for model in models:

        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json"
            },
            json={
                "model": model,
                "messages":[
                    {
                        "role":"system",
                        "content":
                        "Anda adalah YouTube strategist AI."
                    },
                    {
                        "role":"user",
                        "content":prompt
                    }
                ],
                "temperature":0.4
            },
            timeout=60
        )


        if response.status_code == 200:

            return response.json()[
                "choices"
            ][0][
                "message"
            ][
                "content"
            ]


    return f"""
Semua model gagal.

Model tersedia di akun Anda:

{get_available_models()}
"""
