
import streamlit as st
import requests


def groq_analyze(prompt):
    """
    Backward compatibility function.
    app.py lama masih memanggil groq_analyze()
    """

    return groq_chat(
        "Anda adalah YouTube Growth Analyst AI.",
        prompt
    )


def groq_chat(system_prompt, user_prompt):

    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except Exception:
        return "GROQ_API_KEY belum tersedia."

    models = [
        "openai/gpt-oss-20b",
        "llama-3.3-70b-versatile"
    ]

    last_error = ""

    for model in models:

        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "messages": [
                        {
                            "role": "system",
                            "content": system_prompt
                        },
                        {
                            "role": "user",
                            "content": user_prompt
                        }
                    ],
                    "temperature": 0.35
                },
                timeout=60
            )

            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]

            last_error = response.text

        except Exception as e:
            last_error = str(e)

    return f"AI gagal memberikan jawaban.\n\n{last_error}"


def video_insight(video):

    return groq_chat(
        """
Anda adalah YouTube Growth Analyst.

Analisis video secara spesifik:
- viral mechanism
- audience psychology
- title strategy
- thumbnail strategy
- SEO opportunity
- competitor advantage
- content opportunity
""",
        f"""
Data Video:

Judul:
{video.get('title','-')}

Channel:
{video.get('channel','-')}

Views:
{video.get('views','-')}

VPH:
{video.get('vph','-')}

SEO:
{video.get('seo_score','-')}

Tags:
{video.get('tags','-')}
"""
    )


def channel_insight(channel):
    return groq_chat(
        "Anda adalah YouTube Channel Growth Consultant.",
        str(channel)
    )


def competitor_insight(channel_a, channel_b):
    return groq_chat(
        "Anda adalah YouTube Competitive Intelligence Analyst.",
        f"""
Channel A:
{channel_a}

Channel B:
{channel_b}
"""
    )


def content_strategy(niche, reference=""):
    return groq_chat(
        "Anda adalah YouTube Content Strategist.",
        f"""
Niche:
{niche}

Referensi:
{reference}

Buat:
- ide judul
- hook
- thumbnail
- keyword
- strategi konten
"""
    )
