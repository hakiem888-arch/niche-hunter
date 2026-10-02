
import streamlit as st
import requests


def get_groq_key():
    try:
        return st.secrets["GROQ_API_KEY"]
    except Exception:
        return None


def groq_analyze(prompt):

    key = get_groq_key()

    if not key:
        return "❌ GROQ_API_KEY tidak ditemukan."

    models = [
        "openai/gpt-oss-20b",
        "openai/gpt-oss-120b",
        "llama-3.3-70b-versatile"
    ]

    last_error = ""

    for model in models:
        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "Anda adalah YouTube strategist AI."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.4
                },
                timeout=60
            )

            if response.status_code == 200:
                data = response.json()
                return data["choices"][0]["message"]["content"]

            last_error = f"{model}: {response.text}"

        except Exception as e:
            last_error = str(e)

    return f"❌ Semua model Groq gagal.\n\n{last_error}"


def video_insight(video):
    prompt = f"""
Analisis video YouTube berikut.

Judul:
{video.get('title','')}

Channel:
{video.get('channel','')}

Views:
{video.get('views','')}

VPH:
{video.get('vph','')}

SEO Score:
{video.get('seo_score','')}

Berikan:
1. Faktor yang membuat video menarik.
2. Potensi konten.
3. Ide judul baru.
4. Strategi thumbnail.
"""

    return groq_analyze(prompt)
