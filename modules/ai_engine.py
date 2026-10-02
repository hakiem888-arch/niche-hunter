
import streamlit as st
import requests


def groq_chat(system_prompt, user_prompt):

    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except Exception:
        return "GROQ_API_KEY belum tersedia."

    models = [
        "openai/gpt-oss-20b",
        "llama-3.3-70b-versatile"
    ]

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

        except Exception:
            continue

    return "AI gagal memberikan analisis."


def video_insight(video):

    system = """
Anda adalah Diffic AI YouTube Growth Analyst.

Anda bukan memberikan tips umum.
Anda harus menganalisis seperti seorang analis channel profesional.

Gunakan data yang diberikan.

Wajib membahas:
1. Viral mechanism.
2. Audience psychology.
3. Title strategy.
4. Thumbnail strategy.
5. SEO opportunity.
6. Competitive advantage.
7. Content opportunity.
8. Risiko jika membuat konten serupa.

Gunakan bahasa yang spesifik dan berbasis data.
Berikan rekomendasi yang dapat langsung dipakai creator.
"""

    user = f"""
Analisis video YouTube berikut:

Judul:
{video.get('title','-')}

Channel:
{video.get('channel','-')}

Subscriber:
{video.get('subscriber','-')}

Views:
{video.get('views','-')}

Views Per Hour:
{video.get('vph','-')}

Likes:
{video.get('likes','-')}

Comments:
{video.get('comments','-')}

SEO Score:
{video.get('seo_score','-')}

Tags:
{video.get('tags','-')}

Buat laporan analisis lengkap.
"""

    return groq_chat(system, user)


def channel_insight(channel):

    system = """
Anda adalah YouTube Channel Growth Consultant.

Analisis channel berdasarkan:
- positioning
- content pillar
- audience
- winning pattern
- weakness
- growth opportunity

Jangan memberikan jawaban generik.
"""

    return groq_chat(system, str(channel))


def competitor_insight(channel_a, channel_b):

    system = """
Anda adalah competitive intelligence analyst YouTube.

Bandingkan dua channel.

Analisis:
- kekuatan masing-masing
- pola konten
- peluang yang belum dimanfaatkan
- strategi untuk memenangkan niche.
"""

    user = f"""
Channel A:
{channel_a}

Channel B:
{channel_b}
"""

    return groq_chat(system, user)


def content_strategy(niche, reference=""):

    system = """
Anda adalah content strategist YouTube.

Buat strategi konten berdasarkan niche.

Berikan:
- 10 ide judul
- hook 10 detik pertama
- konsep thumbnail
- target audience
- keyword
- alasan peluang.
"""

    user = f"""
Niche:
{niche}

Referensi:
{reference}
"""

    return groq_chat(system, user)
