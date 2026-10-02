
import streamlit as st
import requests


def groq_analyze(prompt):

    if not prompt or not prompt.strip():
        return "❌ Prompt kosong. Tidak ada data yang dianalisis."

    try:
        key = st.secrets["GROQ_API_KEY"]
    except Exception:
        return "❌ GROQ_API_KEY tidak ditemukan di Streamlit Secrets."

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "Anda adalah Diffic AI YouTube Strategist. "
                            "Analisis data YouTube secara profesional."
                        )
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

        # tampilkan error asli jika Groq gagal
        if response.status_code != 200:
            return f"""
❌ GROQ ERROR

Status:
{response.status_code}

Detail:
{response.text}
"""

        data = response.json()

        if "choices" not in data:
            return f"""
❌ Response Groq tidak sesuai.

Response:
{data}
"""

        return data["choices"][0]["message"]["content"]

    except requests.exceptions.Timeout:
        return "❌ Groq timeout. Coba ulangi."

    except Exception as e:
        return f"""
❌ Error sistem:

{str(e)}
"""


def video_insight(video):

    prompt = f"""
Analisis video YouTube berikut.

Judul:
{video.get('title','')}

Views:
{video.get('views','')}

VPH:
{video.get('vph','')}

SEO Score:
{video.get('seo_score','')}

Channel:
{video.get('channel','')}

Berikan:
1. Faktor yang membuat video menarik.
2. Potensi viral.
3. Ide konten turunan.
4. Strategi judul dan thumbnail.
"""

    return groq_analyze(prompt)
