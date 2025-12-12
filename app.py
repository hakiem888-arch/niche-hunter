import streamlit as st
from googleapiclient.discovery import build
from datetime import datetime, timedelta, timezone
import pandas as pd
import requests
import re
from collections import Counter

# ==========================================
# 1. KONFIGURASI HALAMAN
# ==========================================
st.set_page_config(page_title="Pro Niche Finder V5.1 (Dark)", layout="wide", page_icon="🌙")

# --- API KEY (Mengambil dari Secrets) ---
try:
    YOUTUBE_API_KEY = st.secrets["YOUTUBE_API_KEY"]
except:
    st.error("API Key belum disetting di Secrets!")
    st.stop()

# ==========================================
# 2. DATA REFERENSI
# ==========================================
COUNTRY_CODES = {
    "🌍 Global (Semua Negara)": None,
    "🇮🇩 Indonesia": "ID",
    "🇺🇸 Amerika Serikat (US)": "US",
    "🇲🇾 Malaysia": "MY",
    "🇸🇬 Singapura": "SG",
    "🇯🇵 Jepang": "JP",
    "🇰🇷 Korea Selatan": "KR",
    "🇬🇧 Inggris (UK)": "GB",
    "🇦🇺 Australia": "AU",
    "🇨🇦 Kanada": "CA",
    "🇸🇦 Arab Saudi": "SA",
    "🇹🇭 Thailand": "TH"
}

CATEGORIES = {
    "Semua Kategori": None,
    "Film & Animasi": "1",
    "Otomotif": "2",
    "Musik": "10",
    "Hewan & Peliharaan": "15",
    "Olahraga": "17",
    "Travel & Acara": "19",
    "Gaming": "20",
    "Orang & Blog": "22",
    "Komedi": "23",
    "Hiburan": "24",
    "Berita & Politik": "25",
    "How-to & Gaya": "26",
    "Pendidikan": "27",
    "Sains & Teknologi": "28"
}

SORT_OPTIONS = {
    "Relevansi": "relevance",
    "Tanggal Upload (Terbaru)": "date",
    "Jumlah Views": "viewCount",
    "Rating": "rating",
    "VPH Tertinggi (Custom)": "vph_custom",
    "Golden Ratio (Custom)": "ratio_custom"
}

TIME_FILTERS = {
    "Kapan Saja": None,
    "Hari Ini (24 Jam)": 1,
    "Minggu Ini": 7,
    "Bulan Ini": 30,
    "Tahun Ini": 365
}

LICENSE_OPTIONS = {
    "Semua Lisensi": None,
    "Creative Commons": "creativeCommon",
    "Youtube Standar": "youtube"
}

# ==========================================
# 3. CUSTOM CSS (FULL DARK MODE)
# ==========================================
st.markdown("""
<style>
    /* 1. BACKGROUND UTAMA GELAP */
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    
    /* 2. SIDEBAR AGAK TERANG DIKIT */
    section[data-testid="stSidebar"] {
        background-color: #262730;
        border-right: 1px solid #333;
    }
    
    /* 3. KARTU VIDEO (DARK GREY) */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #1E1E1E; /* Warna kartu */
        border: 1px solid #444;
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    
    /* 4. TEKS JUDUL PUTIH */
    .video-title {
        font-family: sans-serif;
        font-weight: 700;
        font-size: 14px;
        color: #FFFFFF; /* Putih */
        line-height: 1.4;
        height: 40px;
        overflow: hidden;
        margin-bottom: 8px;
    }
    
    /* 5. TEKS META (ABU-ABU TERANG) */
    .meta-info {
        font-size: 11px;
        color: #BBBBBB;
        margin-bottom: 8px;
    }
    
    /* 6. STATS BAR (HITAM) */
    .stats-bar {
        display: flex;
        justify-content: space-between;
        background: #000000;
        padding: 6px 10px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 600;
        color: #CCCCCC;
        margin-bottom: 8px;
        border: 1px solid #333;
    }
    
    /* BADGES (TETAP SAMA TAPI BORDER LEBIH GELAP) */
    .vph-badge {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white; font-weight: 700; font-size: 13px; text-align: center;
        padding: 6px; border-radius: 6px; margin-top: 5px;
    }
    .money-badge {
        background-color: #064e3b; color: #6ee7b7; font-weight: bold; /* Hijau Gelap */
        padding: 3px 6px; border-radius: 4px; font-size: 10px;
        border: 1px solid #065f46; display: inline-block; margin-right: 3px;
    }
    .er-badge {
        background-color: #7c2d12; color: #fdba74; font-weight: bold; /* Oranye Gelap */
        padding: 3px 6px; border-radius: 4px; font-size: 10px;
        border: 1px solid #9a3412; display: inline-block; margin-right: 3px;
    }
    .gem-badge {
        background-color: #0c4a6e; color: #7dd3fc; font-weight: bold; /* Biru Gelap */
        padding: 3px 6px; border-radius: 4px; font-size: 10px;
        border: 1px solid #075985; display: inline-block;
    }
    .rank-badge {
        background-color: #ef4444; color: white; font-weight: bold;
        padding: 2px 8px; border-radius: 4px; font-size: 10px;
        display: inline-block; margin-bottom: 5px;
    }
    
    /* CHIPS & TAGS */
    .tag-pill {
        display: inline-block; background: #333; color: #AAA;
        padding: 2px 8px; border-radius: 10px; font-size: 10px;
        margin: 2px; border: 1px solid #555;
    }
    .seo-chip {
        display: inline-block; background: #333; color: #DDD;
        padding: 6px 12px; border-radius: 20px; font-size: 12px;
        margin: 4px; border: 1px solid #555; font-weight: 500;
    }
    .seo-count {
        background: #555; padding: 0 5px; border-radius: 4px; 
        font-size: 10px; font-weight: bold; margin-left: 5px; color: white;
    }
    
    /* BOX DESKRIPSI */
    .desc-box {
        font-size: 12px; color: #CCC; background: #222;
        padding: 10px; border-radius: 6px; border: 1px dashed #555;
        line-height: 1.5;
    }
    
    .summary-bullet { margin-bottom: 5px; display: block; }
    
    .duration-badge {
        background-color: rgba(255,255,255,0.2); color: white;
        padding: 2px 6px; border-radius: 4px; font-size: 11px; font-weight: bold;
    }
    
    .stalker-box {
        background-color: #111; color: white; padding: 20px; border-radius: 15px;
        margin-bottom: 20px; border: 1px solid #444; box-shadow: 0 4px 10px rgba(0,0,0,0.5);
    }
    .stalker-stat {
        text-align: center; border-right: 1px solid #444;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 4. FUNGSI LOGIKA (BACKEND)
# ==========================================

def format_number(num):
    if num >= 1000000: return f"{num/1000000:.1f}M"
    if num >= 1000: return f"{num/1000:.1f}K"
    return str(num)

def calculate_vph(published_at_str, current_views):
    try:
        pub_date = datetime.strptime(published_at_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        hours = (now - pub_date).total_seconds() / 3600
        if hours < 1: hours = 1
        return int(current_views / hours)
    except: return 0

def parse_duration(iso_duration):
    try:
        match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', iso_duration)
        if not match: return "0:00"
        hours, minutes, seconds = match.groups()
        hours = int(hours) if hours else 0
        minutes = int(minutes) if minutes else 0
        seconds = int(seconds) if seconds else 0
        if hours > 0: return f"{hours}:{minutes:02d}:{seconds:02d}"
        else: return f"{minutes}:{seconds:02d}"
    except: return "N/A"

def estimate_earnings(views, region_code):
    is_indo = region_code == 'ID' or region_code == 'MY'
    if is_indo:
        est = (views / 1000) * 10000 
        return f"Rp {est/1000000:.1f}Jt" if est >= 1000000 else f"Rp {est/1000:.0f}Rb"
    else:
        est = (views / 1000) * 3
        return f"$ {est:,.0f}"

def calculate_er(views, likes, comments):
    if views == 0: return 0
    interactions = likes + comments
    return round((interactions / views) * 100, 2)

def get_published_after_rfc3339(days):
    if days is None: return None
    dt = datetime.utcnow() - timedelta(days=days)
    return dt.isoformat("T") + "Z"

def get_channel_subs(youtube, channel_ids):
    try:
        ids_string = ','.join(channel_ids)
        res = youtube.channels().list(id=ids_string, part='statistics').execute()
        subs_map = {}
        for item in res['items']:
            subs_count = int(item['statistics'].get('subscriberCount', 0)) if not item['statistics'].get('hiddenSubscriberCount') else 0
            subs_map[item['id']] = subs_count
        return subs_map
    except: return {}

def smart_summarize(text):
    if not text: return ["Tidak ada deskripsi."]
    clean_text = re.sub(r'http\S+', '', text)
    lines = clean_text.split('\n')
    spam_words = ['subscribe', 'follow', 'instagram', 'tiktok', 'donasi', 'saweria', 'copyright', 'business']
    important_lines = []
    for line in lines:
        line = line.strip()
        lower_line = line.lower()
        if len(line) > 15 and not any(spam in lower_line for spam in spam_words):
            important_lines.append(line)
    if not important_lines:
        fallback_lines = [line.strip() for line in lines if len(line.strip()) > 5]
        return fallback_lines[:3] if fallback_lines else ["Deskripsi terlalu pendek."]
    return important_lines[:4]

def extract_keywords(text):
    words = re.findall(r'\w+', text.lower())
    common_stops = ['yang', 'dan', 'di', 'ke', 'dari', 'ini', 'itu', 'untuk', 'dengan', 'adalah', 'video', 'saya', 'aku', 'the', 'and', 'to', 'of', 'in', 'is', 'for', 'with', 'https', 'http', 'com']
    filtered = [w for w in words if w not in common_stops and len(w) > 3]
    return [item[0] for item in Counter(filtered).most_common(5)]

def analyze_channel(channel_id):
    try:
        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
        ch_res = youtube.channels().list(id=channel_id, part='snippet,statistics').execute()
        if not ch_res['items']: return None
        ch_data = ch_res['items'][0]
        stats = ch_data['statistics']
        snippet = ch_data['snippet']
        search_res = youtube.search().list(channelId=channel_id, part='snippet', type='video', order='date', maxResults=5).execute()
        vid_ids = [item['id']['videoId'] for item in search_res['items']]
        if not vid_ids:
             recent_videos = []
             avg_recent_views = 0
        else:
            recent_stats_res = youtube.videos().list(id=','.join(vid_ids), part='statistics').execute()
            recent_videos = []
            total_recent_views = 0
            for i, item in enumerate(recent_stats_res['items']):
                views = int(item['statistics'].get('viewCount', 0))
                total_recent_views += views
                recent_videos.append({
                    'title': search_res['items'][i]['snippet']['title'],
                    'views': format_number(views),
                    'date': search_res['items'][i]['snippet']['publishedAt'][:10],
                    'thumb': search_res['items'][i]['snippet']['thumbnails']['default']['url']
                })
            avg_recent_views = total_recent_views / len(recent_videos) if recent_videos else 0
        
        return {
            'title': snippet['title'],
            'thumb': snippet['thumbnails']['medium']['url'],
            'custom_url': snippet.get('customUrl', ''),
            'subs': format_number(int(stats.get('subscriberCount', 0))),
            'total_views': format_number(int(stats.get('viewCount', 0))),
            'video_count': format_number(int(stats.get('videoCount', 0))),
            'avg_recent_views': format_number(avg_recent_views),
            'recent_videos': recent_videos
        }
    except Exception as e: return None

def process_video_response(items, youtube, region_code):
    channel_ids = list(set([item['snippet']['channelId'] for item in items]))
    subs_map = get_channel_subs(youtube, channel_ids)
    results = []
    for i, item in enumerate(items):
        stats = item['statistics']
        snippet = item['snippet']
        content = item['contentDetails']
        channel_id = snippet['channelId']
        
        views = int(stats.get('viewCount', 0))
        likes = int(stats.get('likeCount', 0))
        comments = int(stats.get('commentCount', 0))
        subs = subs_map.get(channel_id, 0)
        
        ratio = views / subs if subs > 0 else 0
        ratio_label = f"{ratio:.1f}x"
        is_gem = ratio > 1.5
        vph = calculate_vph(snippet['publishedAt'], views)
        earnings = estimate_earnings(views, region_code)
        er = calculate_er(views, likes, comments)
        tags = snippet.get('tags', [])[:10]
        desc = snippet.get('description', '')
        summary_points = smart_summarize(desc)
        top_keywords = extract_keywords(desc + " " + snippet['title'])
        thumbnails = snippet['thumbnails']
        thumb_url = thumbnails.get('maxres', thumbnails.get('high', thumbnails.get('medium')))['url']
        duration_fmt = parse_duration(content.get('duration', 'PT0S'))

        results.append({
            'rank': i + 1,
            'id': item['id'],
            'channel_id': channel_id,
            'title': snippet['title'],
            'thumbnail': thumb_url,
            'channel': snippet['channelTitle'],
            'published_simple': snippet['publishedAt'][:10],
            'duration': duration_fmt,
            'description': desc,
            'summary': summary_points,
            'keywords': top_keywords,
            'views': views,
            'views_fmt': format_number(views),
            'likes': format_number(likes),
            'comments': format_number(comments),
            'vph': vph,
            'vph_fmt': f"{vph:,.0f}",
            'earnings': earnings,
            'er': er,
            'subs': format_number(subs),
            'ratio': ratio,
            'ratio_label': ratio_label,
            'is_gem': is_gem,
            'tags': tags,
            'link': f"https://youtu.be/{item['id']}" if isinstance(item['id'], str) else f"https://youtu.be/{item['id']['videoId']}"
        })
    return results

def search_youtube(query, region_code='ID', duration='any', 
                   category_id=None, published_after=None, 
                   license_type=None, sort_order='relevance', max_results=12):
    try:
        youtube = build('youtube', 'v3', developerKey=Y
