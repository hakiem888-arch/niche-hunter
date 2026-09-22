import streamlit as st
from googleapiclient.discovery import build
from datetime import datetime, timedelta, timezone
import pandas as pd
import requests
import re
import urllib.parse
import json
import sqlite3
import math
import statistics
import matplotlib.pyplot as plt
from collections import Counter
from pytrends.request import TrendReq
from dateutil.relativedelta import relativedelta

# ==========================================
# 1. KONFIGURASI HALAMAN
# ==========================================
st.set_page_config(page_title="Pro Niche Finder V19.1 (API Fix)", layout="wide", page_icon="🏢")

# --- MULTI API KEY SETUP (SUPER PARSER FIX) ---
raw_keys = ""
if "YOUTUBE_API_KEYS" in st.secrets:
    raw_keys = str(st.secrets["YOUTUBE_API_KEYS"])
elif "YOUTUBE_API_KEY" in st.secrets:
    raw_keys = str(st.secrets["YOUTUBE_API_KEY"])

# Memaksa membelah string berdasarkan koma, walau nama variabelnya salah
API_KEYS = [k.strip() for k in raw_keys.split(",") if k.strip()]

if not API_KEYS:
    st.error("API Key YouTube belum disetting di Secrets!")
    st.stop()

if 'current_api_index' not in st.session_state:
    st.session_state.current_api_index = 0

GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")

# ==========================================
# 2. DATA REFERENSI
# ==========================================
COUNTRY_CODES = {
    "🌍 Global (Semua Negara)": None, "🇮🇩 Indonesia": "ID", "🇺🇸 Amerika Serikat (US)": "US",
    "🇲🇾 Malaysia": "MY", "🇸🇬 Singapura": "SG", "🇯🇵 Jepang": "JP", "🇰🇷 Korea Selatan": "KR",
    "🇬🇧 Inggris (UK)": "GB", "🇦🇺 Australia": "AU", "🇨🇦 Kanada": "CA", "🇸🇦 Arab Saudi": "SA", "🇹🇭 Thailand": "TH"
}

CATEGORIES = {
    "Semua Kategori": None, "Film & Animasi": "1", "Otomotif": "2", "Musik": "10",
    "Hewan & Peliharaan": "15", "Olahraga": "17", "Travel & Acara": "19", "Gaming": "20",
    "Orang & Blog": "22", "Komedi": "23", "Hiburan": "24", "Berita & Politik": "25",
    "How-to & Gaya": "26", "Pendidikan": "27", "Sains & Teknologi": "28"
}

SORT_OPTIONS = {
    "Relevansi": "relevance", "Tanggal Upload (Terbaru)": "date", "Jumlah Views": "viewCount",
    "Rating": "rating", "VPH Tertinggi (Custom)": "vph_custom", "Golden Ratio (Custom)": "ratio_custom",
    "Skor SEO Terbaik (Custom)": "seo_custom"
}

TIME_FILTERS = {
    "Kapan Saja": None, "Hari Ini (24 Jam)": 1, "Minggu Ini": 7, "Bulan Ini": 30, "Tahun Ini": 365
}

LICENSE_OPTIONS = {
    "Semua Lisensi": None, "Creative Commons": "creativeCommon", "Youtube Standar": "youtube"
}

CARD_COLORS = ["#f43f5e", "#fbbf24", "#10b981", "#0ea5e9", "#8b5cf6"]

# ==========================================
# 3. CUSTOM CSS
# ==========================================
st.markdown("""
<style>
    div[data-testid="stVerticalBlockBorderWrapper"] { background-color: var(--secondary-background-color); border: 1px solid rgba(128, 128, 128, 0.2); border-radius: 12px; padding: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
    .video-title { font-weight: 700; font-size: 14px; color: var(--text-color); line-height: 1.4; height: 40px; overflow: hidden; margin-bottom: 8px; }
    .meta-info { font-size: 11px; color: var(--text-color); opacity: 0.8; margin-bottom: 8px; }
    .stats-bar { display: flex; justify-content: space-between; background-color: var(--background-color); padding: 6px 10px; border-radius: 6px; font-size: 12px; font-weight: 600; margin-bottom: 8px; border: 1px solid rgba(128, 128, 128, 0.1); }
    .vph-badge { background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); color: white; font-weight: 700; font-size: 13px; text-align: center; padding: 6px; border-radius: 6px; margin-top: 5px; }
    .money-badge { background-color: #dcfce7; color: #166534; font-weight: bold; padding: 3px 6px; border-radius: 4px; font-size: 10px; border: 1px solid #bbf7d0; display: inline-block; margin-right: 3px; margin-bottom: 3px; }
    .er-badge { background-color: #ffedd5; color: #9a3412; font-weight: bold; padding: 3px 6px; border-radius: 4px; font-size: 10px; border: 1px solid #fed7aa; display: inline-block; margin-right: 3px; margin-bottom: 3px; }
    .gem-badge { background-color: #e0f2fe; color: #0369a1; font-weight: bold; padding: 3px 6px; border-radius: 4px; font-size: 10px; border: 1px solid #bae6fd; display: inline-block; margin-right: 3px; margin-bottom: 3px; }
    .seo-badge { background-color: #fce7f3; color: #be185d; font-weight: bold; padding: 3px 6px; border-radius: 4px; font-size: 10px; border: 1px solid #fbcfe8; display: inline-block; margin-bottom: 3px; }
    .rank-badge { background-color: #ef4444; color: white; font-weight: bold; padding: 2px 8px; border-radius: 4px; font-size: 10px; display: inline-block; margin-bottom: 5px; }
    .seo-chip { display: inline-block; background: var(--secondary-background-color); padding: 6px 12px; border-radius: 20px; font-size: 12px; margin: 4px; border: 1px solid rgba(128, 128, 128, 0.2); font-weight: 500; }
    .seo-count { background: rgba(128, 128, 128, 0.2); padding: 0 5px; border-radius: 4px; font-size: 10px; font-weight: bold; margin-left: 5px; color: var(--text-color); }
    .desc-box { font-size: 12px; background: var(--background-color); padding: 10px; border-radius: 6px; border: 1px dashed rgba(128, 128, 128, 0.3); line-height: 1.5; margin-bottom: 10px; color: var(--text-color);}
    .summary-bullet { margin-bottom: 5px; display: block; }
    .duration-badge { background-color: rgba(0,0,0,0.8); color: white; padding: 2px 6px; border-radius: 4px; font-size: 11px; font-weight: bold; }
    .ai-box { background: linear-gradient(145deg, #1e1e2f, #2a2a40); color: #e2e8f0; padding: 20px; border-radius: 12px; border: 1px solid #4f46e5; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(79, 70, 229, 0.2); }
    .insight-box { background-color: rgba(14, 165, 233, 0.1); border-left: 4px solid #0ea5e9; padding: 15px; border-radius: 0 8px 8px 0; margin-bottom: 15px; }
    .insight-title { font-weight: bold; color: #0ea5e9; margin-bottom: 5px; display: flex; align-items: center; gap: 8px; }
    .stButton > button[kind="secondary"] { border-radius: 20px; padding: 2px 12px; font-size: 12px; border: 1px solid #0ea5e9; color: #0ea5e9; background: transparent; }
    .stButton > button[kind="secondary"]:hover { background: rgba(14, 165, 233, 0.1); }
    .stalker-highlight { font-size: 16px; font-weight: bold; color: #f43f5e; margin-bottom: 5px; }
    
    /* CSS DASHBOARD CHANNEL ADAPTIVE (FONT JUMBO) */
    .ch-card { 
        background-color: var(--secondary-background-color); 
        border-radius: 12px; 
        padding: 24px; 
        color: var(--text-color); 
        box-shadow: 0 4px 10px rgba(0,0,0,0.15); 
        margin-bottom: 15px; 
        height: 100%; 
        display: flex; 
        flex-direction: column; 
        justify-content: space-between;
        border: 1px solid rgba(128, 128, 128, 0.1);
    }
    .ch-card-header { display: flex; justify-content: space-between; margin-bottom: 24px; align-items: flex-start; }
    .ch-header-left { display: flex; gap: 16px; align-items: center; width: 85%; }
    .ch-avatar { width: 65px; height: 65px; border-radius: 50%; object-fit: cover; border: 2px solid rgba(128, 128, 128, 0.2); }
    .ch-title-wrap { display: flex; flex-direction: column; width: 100%; }
    .ch-title { font-size: 20px; font-weight: 800; margin: 0; color: var(--text-color); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 100%; line-height: 1.2;}
    .ch-handle { font-size: 14px; color: var(--text-color); opacity: 0.7; margin: 0; font-weight: 500; margin-top: 4px;}
    .ch-header-icons { display: flex; gap: 8px; color: var(--text-color); opacity: 0.6; font-size: 22px; }
    .ch-header-icons a { color: var(--text-color); text-decoration: none; transition: opacity 0.2s; }
    .ch-header-icons a:hover { opacity: 1; }
    
    .ch-metrics-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 30px; }
    .ch-metric-item { text-align: center; }
    .ch-metric-label { font-size: 11px; color: var(--text-color); opacity: 0.7; font-weight: 700; letter-spacing: 1px; margin-bottom: 6px; text-transform: uppercase; }
    .ch-metric-value { font-size: 24px; font-weight: 900; color: var(--text-color); margin: 0; }
    
    .ch-footer { display: flex; justify-content: space-between; align-items: center; border-top: 1px solid rgba(128, 128, 128, 0.2); padding-top: 16px; font-size: 13px; color: var(--text-color); opacity: 0.8; font-weight: 500;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 4. FUNGSI LOGIKA (BACKEND)
# ==========================================

def parse_yt_date(date_str):
    try:
        clean_date = re.sub(r'\.\d+', '', date_str)
        return datetime.strptime(clean_date, "%Y-%m-%dT%H:%M:%SZ")
    except Exception:
        return datetime.utcnow()

def format_number(num):
    if num >= 1000000: return f"{num/1000000:.1f}M"
    if num >= 1000: return f"{num/1000:.1f}K"
    return str(num)

def calculate_channel_age(published_at):
    try:
        pub_date = parse_yt_date(published_at)
        now = datetime.utcnow()
        diff = relativedelta(now, pub_date)
        years_decimal = diff.years + (diff.months / 12.0)
        if years_decimal >= 1: return f"{years_decimal:.1f} THN"
        elif diff.months > 0: return f"{diff.months} BLN"
        else: return f"{diff.days} HR"
    except: return "N/A"

def fetch_channel_recent_avg_views(youtube, channel_id):
    try:
        res = youtube.search().list(channelId=channel_id, part='id', type='video', order='date', maxResults=5).execute()
        vid_ids = [item['id']['videoId'] for item in res.get('items', []) if 'videoId' in item['id']]
        if not vid_ids: return "0"
        stats = youtube.videos().list(id=','.join(vid_ids), part='statistics').execute()
        total_views = sum([int(item['statistics'].get('viewCount', 0)) for item in stats.get('items', [])])
        return format_number(total_views / len(vid_ids) if vid_ids else 0)
    except Exception as e:
        if "quota" in str(e).lower() or "403" in str(e): raise e
        return "N/A"

def search_youtube_channels(query, max_results=20, sort_by="Banyak Ditonton (Teratas)", subs_filter="Semua", age_filter="Semua", vph_filter="Semua"):
    for attempt in range(len(API_KEYS)):
        key_idx = (st.session_state.current_api_index + attempt) % len(API_KEYS)
        youtube = build('youtube', 'v3', developerKey=API_KEYS[key_idx])
        try:
            fetch_limit = min(50, max_results * 3) if subs_filter != "Semua" or age_filter != "Semua" else max_results
            res = youtube.search().list(q=query, type='channel', part='snippet', maxResults=fetch_limit).execute()
            ch_ids = [item['snippet']['channelId'] for item in res.get('items', [])]
            
            if not ch_ids: return []
            
            stats_res = youtube.channels().list(id=','.join(ch_ids), part='snippet,statistics,contentDetails').execute()
            channels = []
            
            for item in stats_res.get('items', []):
                raw_subs = int(item['statistics'].get('subscriberCount', 0))
                raw_videos = int(item['statistics'].get('videoCount', 0))
                raw_total_views = int(item['statistics'].get('viewCount', 0))
                published_at = item['snippet']['publishedAt']
                
                if subs_filter == "0-1K" and not (0 <= raw_subs <= 1000): continue
                elif subs_filter == "1K-10K" and not (1000 < raw_subs <= 10000): continue
                elif subs_filter == "10K-100K" and not (10000 < raw_subs <= 100000): continue
                elif subs_filter == "100K-1M" and not (100000 < raw_subs <= 1000000): continue
                elif subs_filter == "> 1M" and raw_subs <= 1000000: continue
                
                pub_date = parse_yt_date(published_at)
                now = datetime.utcnow()
                diff = relativedelta(now, pub_date)
                years_decimal = diff.years + (diff.months / 12.0)
                
                if age_filter == "Kurang dari 1 Tahun" and years_decimal >= 1: continue
                elif age_filter == "1-3 Tahun" and not (1 <= years_decimal <= 3): continue
                elif age_filter == "Lebih dari 3 Tahun" and years_decimal <= 3: continue
                
                if years_decimal > 3: card_color = "#ef4444" 
                elif years_decimal >= 1: card_color = "#facc15" 
                else: card_color = "#10b981" 
                    
                if years_decimal >= 1: age_str = f"{years_decimal:.1f} THN"
                elif diff.months > 0: age_str = f"{diff.months} BLN"
                else: age_str = f"{diff.days} HR"
                
                avg_views_val = "0"
                avg_vph_val = 0
                if vph_filter != "Semua" or sort_by == "Tumbuh Tercepat":
                    avg_views_val = fetch_channel_recent_avg_views(youtube, item['id'])
                    avg_vph_val = int(avg_views_val.replace('K','000').replace('M','000000').replace('.','')) / 24 if 'M' in avg_views_val or 'K' in avg_views_val else 0
                
                    if vph_filter == "> 100" and avg_vph_val <= 100: continue
                    elif vph_filter == "> 500" and avg_vph_val <= 500: continue
                    elif vph_filter == "> 1000" and avg_vph_val <= 1000: continue
                    elif vph_filter == "> 5000" and avg_vph_val <= 5000: continue

                channels.append({
                    'id': item['id'],
                    'title': item['snippet']['title'],
                    'custom_url': item['snippet'].get('customUrl', ''),
                    'thumb': item['snippet']['thumbnails'].get('medium', item['snippet']['thumbnails'].get('default', {}))['url'],
                    'subs': format_number(raw_subs),
                    'raw_subs': raw_subs,
                    'videos': format_number(raw_videos),
                    'raw_videos': raw_videos,
                    'total_views': format_number(raw_total_views),
                    'raw_total_views': raw_total_views,
                    'published_at_str': pub_date.strftime("%d %b %Y"),
                    'pub_date_obj': pub_date,
                    'age': age_str,
                    'card_color': card_color,
                    'avg_views': avg_views_val,
                    'raw_avg_vph': avg_vph_val 
                })
                    
            if sort_by == "Subscriber Terbanyak":
                channels = sorted(channels, key=lambda x: x['raw_subs'], reverse=True)
            elif sort_by == "Video Terbanyak":
                channels = sorted(channels, key=lambda x: x['raw_videos'], reverse=True)
            elif sort_by == "Channel Terbaru":
                channels = sorted(channels, key=lambda x: x['pub_date_obj'], reverse=True)
            elif sort_by == "Tumbuh Tercepat":
                channels = sorted(channels, key=lambda x: x['raw_avg_vph'], reverse=True)
            else:
                channels = sorted(channels, key=lambda x: x['raw_total_views'], reverse=True)
                
            st.session_state.current_api_index = key_idx
            return channels[:max_results]
        
        except Exception as e:
            if "quota" in str(e).lower() or "403" in str(e):
                continue
            else:
                st.error(f"❌ Terjadi kesalahan API YouTube. Detail: {str(e)}")
                return []
            
    st.error("❌ SEMUA API KEY TELAH KEHABISAN KUOTA HARIAN! Silakan tunggu besok atau tambahkan API Key baru di setting.")
    return []

def get_youtube_suggestions(query):
    if not query or len(query) < 2: return []
    try:
        url = f"http://suggestqueries.google.com/complete/search?client=firefox&ds=yt&q={urllib.parse.quote(query)}"
        response = requests.get(url, timeout=3)
        if response.status_code == 200: return json.loads(response.text)[1][:10]
        return []
    except: return []

def estimate_best_time(results):
    if not results: return "Data tidak cukup"
    times = []
    for r in results:
        try:
            dt = parse_yt_date(r['published_full']) + timedelta(hours=7) 
            times.append(dt)
        except: pass
    if not times: return "Data tidak cukup"
    days_indo = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu']
    day_counts = Counter([days_indo[t.weekday()] for t in times])
    hour_counts = Counter([t.hour for t in times])
    return f"{day_counts.most_common(1)[0][0]}, pukul {hour_counts.most_common(1)[0][0]:02d}:00 WIB"

def get_rising_trends(query, geo='ID'):
    try:
        pytrend = TrendReq(hl='id-ID', tz=420, retries=3, backoff_factor=1) 
        pytrend.build_payload(kw_list=[query], timeframe='now 7-d', geo=geo if geo else '', gprop='youtube')
        data = pytrend.related_queries()
        if query in data and data[query]['rising'] is not None:
            return data[query]['rising'].head(8).to_dict('records')
        return []
    except Exception: return None 

def generate_ai_ideas(niche_query):
    if not GEMINI_API_KEY: return "⚠️ **Error:** GEMINI_API_KEY belum diisi di Streamlit Secrets."
    prompt = f"""Kamu pakar YouTube SEO dari vidIQ. Buat 5 ide video viral untuk niche: "{niche_query}". 
    Format wajib: 
    ### Ide [Nomor]
    * **💡 Judul Video:** (Clickbait jujur)
    * **🖼️ Konsep Thumbnail:** (Elemen visual, teks, warna kontras)
    * **🔥 Alasan Menang:** (Kenapa disukai algoritma & penonton)"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    try:
        response = requests.post(url, headers={'Content-Type': 'application/json'}, json={"contents": [{"parts": [{"text": prompt}]}]})
        response.raise_for_status()
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    except Exception as e: return f"❌ Gagal memanggil AI. Detail: {str(e)}"

def calculate_vph(published_at_str, current_views):
    try:
        pub_date = parse_yt_date(published_at_str).replace(tzinfo=timezone.utc)
        hours = (datetime.now(timezone.utc) - pub_date).total_seconds() / 3600
        return int(current_views / max(hours, 1))
    except: return 0

def parse_duration(iso_duration):
    try:
        match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', iso_duration)
        if not match: return "0:00"
        h, m, s = [int(v) if v else 0 for v in match.groups()]
        return f"{h}:{m:02d}:{s:02d}" if h > 0 else f"{m}:{s:02d}"
    except: return "N/A"

def estimate_earnings(views, region_code):
    est = (views / 1000) * (10000 if region_code in ['ID', 'MY'] else 3)
    if region_code in ['ID', 'MY']: return f"Rp {est/1000000:.1f}Jt" if est >= 1000000 else f"Rp {est/1000:.0f}Rb"
    return f"$ {est:,.0f}"

def calculate_er(views, likes, comments): return round(((likes + comments) / views) * 100, 2) if views > 0 else 0

def calculate_seo_score(title, desc, tags):
    score = 0; checks = []
    if 20 <= len(title) <= 60: score += 40; checks.append("✅ Panjang Judul Ideal (20-60 karakter)")
    else: score += 20; checks.append(f"❌ Judul Kurang Optimal ({len(title)} karakter)")
    if len(desc) > 200: score += 30; checks.append("✅ Deskripsi Panjang & Informatif")
    elif len(desc) > 0: score += 10; checks.append("❌ Deskripsi Terlalu Pendek")
    else: checks.append("❌ Tidak Ada Deskripsi")
    if tags and len(tags) >= 3: score += 30; checks.append(f"✅ Menggunakan Tags ({len(tags)} tags terdeteksi)")
    else: checks.append("❌ Minim / Tidak Ada Tags")
    return score, checks

# ==========================================
# VIRAL INTELLIGENCE V2
# New long-form videos + breakout prediction
# ==========================================
SNAPSHOT_DB = "niche_hunter_snapshots.db"


def init_snapshot_db():
    conn = sqlite3.connect(SNAPSHOT_DB)
    conn.execute("""CREATE TABLE IF NOT EXISTS video_snapshots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        video_id TEXT NOT NULL,
        captured_at TEXT NOT NULL,
        views INTEGER DEFAULT 0,
        likes INTEGER DEFAULT 0,
        comments INTEGER DEFAULT 0,
        subscribers INTEGER DEFAULT 0
    )""")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_video_snapshots ON video_snapshots(video_id, captured_at)")
    conn.commit(); conn.close()


init_snapshot_db()


def parse_iso_duration_seconds(iso):
    m = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', iso or '')
    if not m: return 0
    h, mi, sec = [int(x or 0) for x in m.groups()]
    return h * 3600 + mi * 60 + sec


def shorts_confidence(video):
    title = (video.get('title') or '').lower()
    desc = (video.get('description') or '').lower()
    duration = video.get('duration_seconds', 99999)
    score = 0
    if duration <= 60: score += 45
    elif duration <= 180: score += 35
    if '#shorts' in title or '#shorts' in desc: score += 35
    if 'shorts' in title or 'short video' in title or 'vertical' in title: score += 15
    if 'shorts' in desc: score += 10
    return min(score, 100)


def save_video_snapshots(results):
    if not results: return
    now = datetime.utcnow().isoformat()
    conn = sqlite3.connect(SNAPSHOT_DB)
    for v in results:
        conn.execute(
            "INSERT INTO video_snapshots(video_id,captured_at,views,likes,comments,subscribers) VALUES(?,?,?,?,?,?)",
            (v['id'], now, int(v.get('raw_views', v.get('views', 0))), int(v.get('raw_likes', 0)),
             int(v.get('raw_comments', 0)), int(v.get('raw_subs', 0)))
        )
    conn.commit(); conn.close()


def get_snapshot_history(video_id, limit=6):
    conn = sqlite3.connect(SNAPSHOT_DB)
    rows = conn.execute(
        "SELECT captured_at,views,likes,comments,subscribers FROM video_snapshots "
        "WHERE video_id=? ORDER BY captured_at DESC LIMIT ?", (video_id, limit)
    ).fetchall()
    conn.close()
    return rows


def calculate_v2_velocity_and_acceleration(video):
    """Return interval VPH, acceleration and history confidence.
    First scan falls back to lifetime VPH. Later scans use real snapshot deltas.
    """
    rows = get_snapshot_history(video['id'], 6)
    now = datetime.utcnow()
    current_views = int(video.get('raw_views', video.get('views', 0)))

    if not rows:
        return float(video.get('vph', 0)), 1.0, 0, 0

    latest_time = datetime.fromisoformat(rows[0][0])
    elapsed = max((now - latest_time).total_seconds() / 3600, 0.05)
    current_interval_vph = max((current_views - int(rows[0][1])) / elapsed, 0)

    # With only one historical snapshot, we can measure velocity but not true acceleration.
    if len(rows) < 2:
        return current_interval_vph, 1.0, int(video.get('vph', 0)), 1

    prev_time = datetime.fromisoformat(rows[1][0])
    interval_hours = max((latest_time - prev_time).total_seconds() / 3600, 0.05)
    previous_interval_vph = max((int(rows[0][1]) - int(rows[1][1])) / interval_hours, 0)
    if previous_interval_vph <= 0:
        acceleration = 3.0 if current_interval_vph > 0 else 1.0
    else:
        acceleration = current_interval_vph / previous_interval_vph
    return current_interval_vph, max(0.1, acceleration), int(previous_interval_vph), len(rows)


def normalize_score(value, low, high):
    if high <= low: return 50
    return max(0, min(100, (value - low) / (high - low) * 100))


def median_safe(values, default=0):
    vals = [float(x) for x in values if x is not None and float(x) >= 0]
    return statistics.median(vals) if vals else default


def fetch_channel_baselines(youtube, channel_ids, max_videos=8, max_channels=20):
    """Build a channel-normal baseline from recent uploads.
    Capped to the strongest discovered channels to protect YouTube API quota.
    Results are cached in Streamlit session for the current run/session.
    """
    cache = st.session_state.setdefault('viral_baseline_cache', {})
    baselines = {}
    unique_ids = list(dict.fromkeys([x for x in channel_ids if x]))[:max_channels]
    for channel_id in unique_ids:
        cached = cache.get(channel_id)
        if cached and (datetime.utcnow() - cached['captured_at']).total_seconds() < 1800:
            baselines[channel_id] = cached['data']
            continue
        try:
            search_res = youtube.search().list(
                channelId=channel_id, part='id,snippet', type='video', order='date',
                maxResults=min(10, max_videos)
            ).execute()
            ids = [x['id']['videoId'] for x in search_res.get('items', []) if x.get('id', {}).get('videoId')]
            if not ids:
                continue
            stats_res = youtube.videos().list(id=','.join(ids), part='snippet,statistics').execute()
            views_list, vph_list = [], []
            for item in stats_res.get('items', []):
                stt = item.get('statistics', {})
                sn = item.get('snippet', {})
                views = int(stt.get('viewCount', 0))
                published = sn.get('publishedAt', '')
                if not published:
                    continue
                age_hours = max((datetime.utcnow() - parse_yt_date(published)).total_seconds() / 3600, 1)
                views_list.append(views); vph_list.append(views / age_hours)
            if views_list:
                data = {
                    'sample_size': len(views_list),
                    'median_views': median_safe(views_list),
                    'median_vph': median_safe(vph_list),
                    'avg_views': sum(views_list) / len(views_list),
                }
                cache[channel_id] = {'captured_at': datetime.utcnow(), 'data': data}
                baselines[channel_id] = data
        except Exception as e:
            if 'quota' in str(e).lower() or '403' in str(e): raise
            continue
    return baselines



# ==========================================
# LEGACY / SHARED YOUTUBE FUNCTIONS
# ==========================================

def get_channel_subs(youtube, channel_ids):
    try:
        result = {}
        # YouTube channel ID filters are safest in batches of 50.
        for start in range(0, len(channel_ids), 50):
            batch = channel_ids[start:start + 50]
            res = youtube.channels().list(id=','.join(batch), part='statistics').execute()
            result.update({
                item['id']: int(item['statistics'].get('subscriberCount', 0))
                for item in res.get('items', [])
            })
        return result
    except Exception as e:
        if "quota" in str(e).lower() or "403" in str(e): raise e
        return {}

def smart_summarize(text):
    if not text: return ["Tidak ada deskripsi."]
    lines = [l.strip() for l in re.sub(r'http\S+', '', text).split('\n') if len(l.strip()) > 5]
    spam = ['subscribe', 'follow', 'instagram', 'tiktok', 'donasi', 'saweria', 'copyright']
    important = [l for l in lines if len(l) > 15 and not any(s in l.lower() for s in spam)]
    return important[:4] if important else (lines[:3] if lines else ["Deskripsi terlalu pendek."])

def extract_keywords(text):
    words = [w for w in re.findall(r'\w+', text.lower()) if len(w) > 3 and w not in ['yang', 'dan', 'di', 'ke', 'dari', 'ini', 'itu', 'untuk', 'dengan', 'adalah', 'video', 'saya', 'aku', 'the', 'and', 'to', 'of', 'in', 'is', 'for', 'with']]
    return [item[0] for item in Counter(words).most_common(5)]

def analyze_channel_deep(channel_id):
    for attempt in range(len(API_KEYS)):
        key_idx = (st.session_state.current_api_index + attempt) % len(API_KEYS)
        youtube = build('youtube', 'v3', developerKey=API_KEYS[key_idx])
        try:
            ch_data = youtube.channels().list(id=channel_id, part='snippet,statistics,contentDetails').execute()['items'][0]
            uploads_id = ch_data['contentDetails']['relatedPlaylists']['uploads']
            
            pl_res = youtube.playlistItems().list(playlistId=uploads_id, part='snippet', maxResults=15).execute()
            vid_ids = [item['snippet']['resourceId']['videoId'] for item in pl_res.get('items', [])]
            
            recent_videos = []
            all_tags = []
            upload_hours = []
            
            if vid_ids:
                stats = youtube.videos().list(id=','.join(vid_ids), part='snippet,statistics').execute()
                for i, item in enumerate(stats['items']):
                    snippet = item['snippet']
                    views = int(item['statistics'].get('viewCount', 0))
                    try:
                        pub_dt = parse_yt_date(snippet['publishedAt']) + timedelta(hours=7)
                        upload_hours.append(pub_dt.hour)
                    except: pass
                    
                    vid_tags = snippet.get('tags', [])
                    all_tags.extend(vid_tags)
                    
                    if i < 5:
                        recent_videos.append({
                            'title': snippet['title'], 
                            'views': format_number(views),
                            'raw_views': views,
                            'date': parse_yt_date(snippet['publishedAt']).strftime("%d %b %Y"), 
                            'thumb': snippet['thumbnails'].get('medium', snippet['thumbnails'].get('default', {}))['url']
                        })
            
            best_hour_str = "Tidak diketahui"
            if upload_hours:
                most_common_hour = Counter(upload_hours).most_common(1)[0][0]
                best_hour_str = f"Pukul {most_common_hour:02d}:00 WIB"
                
            top_tags = Counter(all_tags).most_common(15)
            avg_views_calc = sum([v['raw_views'] for v in recent_videos]) / len(recent_videos) if recent_videos else 0

            st.session_state.current_api_index = key_idx
            return {
                'title': ch_data['snippet']['title'], 
                'thumb': ch_data['snippet']['thumbnails']['medium']['url'],
                'custom_url': ch_data['snippet'].get('customUrl', ''), 
                'subs': format_number(int(ch_data['statistics'].get('subscriberCount', 0))),
                'total_views': format_number(int(ch_data['statistics'].get('viewCount', 0))), 
                'video_count': format_number(int(ch_data['statistics'].get('videoCount', 0))),
                'avg_recent_views': format_number(avg_views_calc),
                'recent_videos': recent_videos,
                'favorite_upload_hour': best_hour_str,
                'top_seo_tags': top_tags
            }
        except Exception as e:
            if "quota" in str(e).lower() or "403" in str(e):
                continue
            else:
                st.error(f"❌ Gagal membedah channel. Detail: {str(e)}")
                return None
    st.error("❌ SEMUA API KEY TELAH KEHABISAN KUOTA HARIAN!")
    return None

def process_video_response(items, youtube, region_code):
    channel_ids = list(set([item['snippet']['channelId'] for item in items]))
    subs_map = get_channel_subs(youtube, channel_ids)
    results = []
    
    for i, item in enumerate(items):
        try:
            stats = item.get('statistics', {})
            snippet = item.get('snippet', {})
            content = item.get('contentDetails', {})
            views = int(stats.get('viewCount', 0))
            likes = int(stats.get('likeCount', 0))
            comments = int(stats.get('commentCount', 0))
            subs = subs_map.get(snippet.get('channelId', ''), 0)
            
            thumbnails = snippet.get('thumbnails', {})
            best_thumb = thumbnails.get('maxres') or thumbnails.get('high') or thumbnails.get('medium') or thumbnails.get('default') or {}
            
            desc = snippet.get('description', '')
            tags = snippet.get('tags', [])[:10]
            seo_score, seo_checks = calculate_seo_score(snippet.get('title', ''), desc, tags)
            video_id = item['id'] if isinstance(item['id'], str) else item['id'].get('videoId', '')

            results.append({
                'rank': i + 1, 'id': video_id, 'channel_id': snippet.get('channelId', ''),
                'title': snippet.get('title', 'Untitled'), 'thumbnail': best_thumb.get('url', ''),
                'channel': snippet.get('channelTitle', 'Unknown'), 
                'published_full': snippet.get('publishedAt', ''),
                'published_simple': parse_yt_date(snippet['publishedAt']).strftime("%d %b %Y"),
                'duration': parse_duration(content.get('duration', 'PT0S')), 'duration_iso': content.get('duration','PT0S'), 'duration_seconds': parse_iso_duration_seconds(content.get('duration','PT0S')), 'description': desc,
                'summary': smart_summarize(desc), 'keywords': extract_keywords(desc + " " + snippet.get('title', '')),
                'views': views, 'raw_views': views, 'views_fmt': format_number(views), 'likes': format_number(likes), 'raw_likes': likes, 'comments': format_number(comments), 'raw_comments': comments, 'raw_subs': subs,
                'vph': calculate_vph(snippet.get('publishedAt', ''), views), 'vph_fmt': f"{calculate_vph(snippet.get('publishedAt', ''), views):,.0f}", 
                'earnings': estimate_earnings(views, region_code), 'er': calculate_er(views, likes, comments), 
                'subs': format_number(subs), 'ratio': (views/subs if subs > 0 else 0), 'ratio_label': f"{(views/subs if subs>0 else 0):.1f}x", 
                'is_gem': (views/subs if subs > 0 else 0) > 1.5, 'tags': tags, 'seo_score': seo_score, 'seo_checks': seo_checks,
                'link': f"https://youtu.be/{video_id}"
            })
        except: continue 
    return results

def search_youtube(query, region_code='ID', duration='any', category_id=None, published_after=None, license_type=None, sort_order='relevance', max_results=12):
    for attempt in range(len(API_KEYS)):
        key_idx = (st.session_state.current_api_index + attempt) % len(API_KEYS)
        youtube = build('youtube', 'v3', developerKey=API_KEYS[key_idx])
        try:
            api_order = 'viewCount' if sort_order in ['vph_custom', 'ratio_custom', 'seo_custom'] else sort_order
            params = {'q': query, 'part': 'snippet', 'type': 'video', 'maxResults': max_results, 'order': api_order}
            
            if region_code: params['regionCode'] = region_code
            if duration != 'any': params['videoDuration'] = duration
            if category_id: params['videoCategoryId'] = category_id
            if published_after: params['publishedAfter'] = published_after
            if license_type: params['videoLicense'] = license_type
            
            search_res = youtube.search().list(**params).execute()
            vid_ids = [item['id']['videoId'] for item in search_res.get('items', []) if 'videoId' in item['id']]
            if not vid_ids: return []

            stats_res = youtube.videos().list(part='snippet,statistics,contentDetails', id=','.join(vid_ids)).execute()
            results = process_video_response(stats_res.get('items', []), youtube, region_code)
            
            if sort_order == 'vph_custom': return sorted(results, key=lambda x: x['vph'], reverse=True)
            elif sort_order == 'ratio_custom': return sorted(results, key=lambda x: x['ratio'], reverse=True)
            elif sort_order == 'seo_custom': return sorted(results, key=lambda x: x['seo_score'], reverse=True)
            
            st.session_state.current_api_index = key_idx
            return results
        except Exception as e:
            if "quota" in str(e).lower() or "403" in str(e):
                continue
            else:
                st.error(f"❌ Terjadi kesalahan API YouTube. Detail: {e}")
                return []
    st.error("❌ SEMUA API KEY TELAH KEHABISAN KUOTA HARIAN!")
    return []

def get_trending_videos(region_code='ID', category_id=None, max_results=12):
    for attempt in range(len(API_KEYS)):
        key_idx = (st.session_state.current_api_index + attempt) % len(API_KEYS)
        youtube = build('youtube', 'v3', developerKey=API_KEYS[key_idx])
        try:
            params = {'part': 'snippet,statistics,contentDetails', 'chart': 'mostPopular', 'regionCode': region_code, 'maxResults': max_results}
            if category_id: params['videoCategoryId'] = category_id
            response = youtube.videos().list(**params).execute()
            
            st.session_state.current_api_index = key_idx
            return process_video_response(response.get('items', []), youtube, region_code)
        except Exception as e:
            if "quota" in str(e).lower() or "403" in str(e):
                continue
            else:
                st.error(f"❌ Error API: {e}")
                return []
    st.error("❌ SEMUA API KEY TELAH KEHABISAN KUOTA HARIAN!")
    return []


def get_published_after_rfc3339(days):
    """Return an RFC3339 UTC timestamp for a freshness window."""
    if not days:
        return None
    return (datetime.utcnow() - timedelta(days=int(days))).isoformat(timespec="seconds") + "Z"

def search_viral_longform(query, region_code='ID', category_id=None, max_results=30,
                          freshness_days=7, min_duration_seconds=240):
    """V2 discovery: fresh + high-performing long-form candidates.
    YouTube API duration buckets are split into medium (4-20m) and long (>20m).
    """
    for attempt in range(len(API_KEYS)):
        key_idx = (st.session_state.current_api_index + attempt) % len(API_KEYS)
        youtube = build('youtube', 'v3', developerKey=API_KEYS[key_idx])
        try:
            published_after = get_published_after_rfc3339(freshness_days)
            collected = []
            discovery_source = {}
            # Fresh discovery catches new uploads that have not accumulated huge lifetime views.
            # Breakout discovery catches videos already gaining unusual view volume.
            for duration_bucket in ['medium', 'long']:
                for order in ['date', 'viewCount']:
                    params = {
                        'q': query, 'part': 'snippet', 'type': 'video',
                        'maxResults': min(50, max(10, max_results)),
                        'order': order, 'videoDuration': duration_bucket,
                    }
                    if region_code: params['regionCode'] = region_code
                    if category_id: params['videoCategoryId'] = category_id
                    if published_after: params['publishedAfter'] = published_after
                    res = youtube.search().list(**params).execute()
                    for x in res.get('items', []):
                        vid = x.get('id', {}).get('videoId')
                        if vid:
                            collected.append(vid)
                            source_name = 'Fresh Uploads' if order == 'date' else 'Recent High-Views'
                            discovery_source[vid] = source_name

            ids = list(dict.fromkeys(collected))[:50]
            if not ids:
                return []

            stats = youtube.videos().list(
                id=','.join(ids), part='snippet,statistics,contentDetails'
            ).execute()
            raw = process_video_response(stats.get('items', []), youtube, region_code)

            # Hard long-form gate. 4 minutes is the default; no Shorts leakage.
            candidates = []
            cutoff_hours = freshness_days * 24
            for v in raw:
                age_hours = max((datetime.utcnow() - parse_yt_date(v.get('published_full', ''))).total_seconds() / 3600, 0)
                duration = int(v.get('duration_seconds', 0))
                if duration < min_duration_seconds:
                    continue
                if age_hours > cutoff_hours + 1:
                    continue
                if v.get('shorts_confidence', 0) >= 45:
                    continue
                candidates.append(v)

            # Channel baseline requires extra calls, so do it only for discovered channels.
            baseline_candidates = sorted(candidates, key=lambda x: x.get('vph', 0), reverse=True)[:20]
            channel_ids = [v.get('channel_id') for v in baseline_candidates if v.get('channel_id')]
            baselines = fetch_channel_baselines(youtube, channel_ids, max_videos=8, max_channels=20)
            for v in candidates:
                v['discovery_source'] = discovery_source.get(v.get('id'), 'Recent Candidate')
            enrich_viral_longform(candidates, query, baselines)
            save_video_snapshots(candidates)
            st.session_state.current_api_index = key_idx
            return sorted(candidates, key=lambda x: x.get('breakout_score', 0), reverse=True)[:max_results]
        except Exception as e:
            if 'quota' in str(e).lower() or '403' in str(e):
                continue
            st.error(f'❌ Viral Intelligence V2 API error: {e}')
            return []
    st.error('❌ SEMUA API KEY TELAH KEHABISAN KUOTA HARIAN!')
    return []


def calculate_breakout_score(v):
    velocity_score = normalize_score(math.log10(max(v.get('velocity_vph', 0), 1)), 1, 5)
    acceleration_score = normalize_score(math.log10(max(v.get('acceleration', 1), 0.1)), -1, 1)
    baseline_multiple = v.get('channel_breakout_multiple', 0)
    baseline_score = normalize_score(math.log10(max(baseline_multiple, 0.1)), -1, 1.5)
    ratio_score = normalize_score(math.log10(max(v.get('ratio', 0.01), 0.01)), -1, 2)
    er_score = normalize_score(v.get('er', 0), 0, 10)
    freshness_score = max(0, min(100, 100 - (v.get('age_hours', 999) / 168) * 100))
    relevance_score = v.get('query_relevance', 70)

    score = (
        0.30 * velocity_score +
        0.20 * acceleration_score +
        0.15 * baseline_score +
        0.10 * ratio_score +
        0.10 * er_score +
        0.10 * freshness_score +
        0.05 * relevance_score
    )
    return round(max(0, min(100, score)), 1)


def breakout_label(score):
    if score >= 90: return '💥 EXPLOSIVE'
    if score >= 80: return '🚨 BREAKOUT'
    if score >= 70: return '🔥 HOT'
    if score >= 55: return '🚀 RISING'
    if score >= 40: return '📈 EARLY'
    return 'NORMAL'


def enrich_viral_longform(results, query='', baselines=None):
    baselines = baselines or {}
    now = datetime.utcnow()
    q_words = set(re.findall(r'\w+', query.lower()))
    for v in results:
        pub = parse_yt_date(v.get('published_full', ''))
        age_hours = max((now - pub).total_seconds() / 3600, 0.05)
        v['age_hours'] = age_hours
        v['duration_seconds'] = v.get('duration_seconds', parse_iso_duration_seconds(v.get('duration_iso', '')))
        v['shorts_confidence'] = shorts_confidence(v)

        velocity, acceleration, previous_vph, snapshot_count = calculate_v2_velocity_and_acceleration(v)
        v['velocity_vph'] = int(max(0, velocity))
        v['vph'] = v['velocity_vph']
        v['vph_fmt'] = f"{v['velocity_vph']:,}"
        v['previous_vph'] = previous_vph
        v['acceleration'] = round(acceleration, 2)
        v['snapshot_count'] = snapshot_count

        baseline = baselines.get(v.get('channel_id'), {})
        baseline_views = float(baseline.get('median_views', 0))
        baseline_vph = float(baseline.get('median_vph', 0))
        v['channel_baseline_views'] = int(baseline_views)
        v['channel_baseline_vph'] = int(baseline_vph)
        v['channel_baseline_samples'] = int(baseline.get('sample_size', 0))
        velocity_multiple = velocity / baseline_vph if baseline_vph > 0 else 0
        views_multiple = v.get('raw_views', 0) / baseline_views if baseline_views > 0 else 0
        v['velocity_baseline_multiple'] = round(velocity_multiple, 2)
        v['views_baseline_multiple'] = round(views_multiple, 2)
        if velocity_multiple > 0 and views_multiple > 0:
            v['channel_breakout_multiple'] = round(0.7 * velocity_multiple + 0.3 * views_multiple, 2)
        else:
            v['channel_breakout_multiple'] = round(max(velocity_multiple, views_multiple), 2)

        title_words = set(re.findall(r'\w+', (v.get('title', '') + ' ' + v.get('description', '')).lower()))
        v['query_relevance'] = min(100, 40 + 20 * len(q_words & title_words)) if q_words else 70
        v['breakout_score'] = calculate_breakout_score(v)
        v['viral_score'] = v['breakout_score']  # backwards-compatible export
        v['viral_label'] = breakout_label(v['breakout_score'])
        v['breakout'] = v['breakout_score'] >= 70

        reasons = []
        if velocity_multiple >= 5: reasons.append(f"{velocity_multiple:.1f}x di atas velocity normal channel")
        elif velocity > 0 and baseline_vph <= 0: reasons.append("channel baseline belum cukup terbentuk")
        if acceleration >= 2: reasons.append(f"velocity naik {acceleration:.1f}x")
        if v.get('ratio', 0) >= 2: reasons.append(f"views {v['ratio']:.1f}x subscriber")
        if age_hours <= 24: reasons.append(f"baru {age_hours:.1f} jam")
        elif age_hours <= 72: reasons.append(f"baru {age_hours/24:.1f} hari")
        if v.get('er', 0) >= 5: reasons.append(f"engagement {v['er']:.1f}%")
        if not reasons: reasons.append("velocity awal sedang dipantau")
        v['breakout_reasons'] = reasons[:4]
    return sorted(results, key=lambda x: x.get('breakout_score', 0), reverse=True)


def search_viral_shorts(query, region_code='ID', category_id=None, max_results=30):
    """Backward-compatible alias. Viral Intelligence now means NEW LONG-FORM."""
    return search_viral_longform(query, region_code, category_id, max_results, freshness_days=7, min_duration_seconds=240)


def analyze_winning_patterns(results):
    if not results: return {}
    top = sorted(results, key=lambda x: x.get('breakout_score', 0), reverse=True)[:20]
    words, title_patterns, durations, scores = Counter(), Counter(), [], []
    for v in top:
        words.update(re.findall(r'\w+', v.get('title', '').lower()))
        durations.append(v.get('duration_seconds', 0)); scores.append(v.get('breakout_score', 0))
        t = v.get('title', '')
        if '?' in t: title_patterns['Question'] += 1
        if any(c.isdigit() for c in t): title_patterns['Number/List'] += 1
        if re.search(r'\b(you|your|how|why|what|cara|ternyata|rahasia|jangan)\b', t, re.I): title_patterns['Curiosity/Promise'] += 1
        if '!' in t: title_patterns['Emotional punctuation'] += 1
    common = [w for w, c in words.most_common(15) if len(w) > 3]
    return {
        'top_count': len(top),
        'avg_duration': round(sum(durations) / len(durations), 1) if durations else 0,
        'avg_score': round(sum(scores) / len(scores), 1) if scores else 0,
        'keywords': common[:10], 'title_patterns': title_patterns, 'top_videos': top
    }


def channel_outliers(results):
    groups = {}
    for v in results: groups.setdefault(v.get('channel_id'), []).append(v)
    out = []
    for cid, vids in groups.items():
        avg = sum(x.get('views', 0) for x in vids) / len(vids)
        for v in vids:
            ratio = v.get('views', 0) / max(avg, 1)
            if ratio >= 3: out.append({**v, 'outlier_multiple': round(ratio, 1)})
    return sorted(out, key=lambda x: x['outlier_multiple'], reverse=True)


def small_channel_gems(results):
    return sorted([
        v for v in results
        if int(v.get('raw_subs', 0)) <= 100000 and v.get('channel_breakout_multiple', 0) >= 3
        and v.get('breakout_score', 0) >= 55
    ], key=lambda x: x.get('breakout_score', 0), reverse=True)


def radar_chart(video):
    labels = ['Velocity', 'Acceleration', 'Channel\nBreakout', 'Views/Subs', 'Engagement', 'Freshness']
    values = [
        normalize_score(math.log10(max(video.get('velocity_vph', 0), 1)), 1, 5),
        normalize_score(math.log10(max(video.get('acceleration', 1), 0.1)), -1, 1),
        normalize_score(math.log10(max(video.get('channel_breakout_multiple', 0.1), 0.1)), -1, 1.5),
        normalize_score(math.log10(max(video.get('ratio', 0.01), 0.01)), -1, 2),
        normalize_score(video.get('er', 0), 0, 10),
        max(0, min(100, 100 - (video.get('age_hours', 999) / 168) * 100)),
    ]
    angles = [i * 2 * math.pi / len(labels) for i in range(len(labels))]
    values += values[:1]; angles += angles[:1]
    fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))
    ax.plot(angles, values, linewidth=2)
    ax.fill(angles, values, alpha=0.15)
    ax.set_ylim(0, 100); ax.set_yticks([25, 50, 75, 100]); ax.set_yticklabels(['25', '50', '75', '100'])
    ax.set_xticks(angles[:-1]); ax.set_xticklabels(labels)
    ax.set_title(f"Breakout Radar — {video.get('breakout_score', 0):.0f}/100", pad=20, fontweight='bold')
    ax.grid(alpha=0.25)
    return fig


def build_content_opportunity(video, query=''):
    duration = int(video.get('duration_seconds', 0))
    minutes = duration / 60 if duration else 0
    keywords = extract_keywords(video.get('title', '') + ' ' + video.get('description', ''))[:6]
    angle = 'angle yang sama dengan diferensiasi lebih kuat'
    if '?' in video.get('title', ''): angle = 'ubah menjadi format problem → experiment → result'
    elif any(c.isdigit() for c in video.get('title', '')): angle = 'ubah menjadi list dengan hasil yang bisa dibuktikan'
    elif any(w in video.get('title', '').lower() for w in ['how', 'cara', 'tutorial']): angle = 'buat versi lebih spesifik untuk pemula dengan hasil akhir yang jelas'
    return {
        'topic': ', '.join(keywords) or query,
        'recommended_duration': f"{max(6, round(minutes))}-{max(10, round(minutes + 5))} menit" if minutes else '8-15 menit',
        'hook': f"Mulai dari masalah/hasil paling kuat terkait {keywords[0] if keywords else query}, bukan intro panjang.",
        'angle': angle,
        'title_formula': f"{keywords[0].title() if keywords else query.title()}: [hasil/temuan utama] yang tidak banyak orang tahu",
        'thumbnail': '1 objek/hasil utama + ekspresi/kontras visual kuat + 2-4 kata besar; hindari menyalin thumbnail asli.',
        'why_now': f"Video referensi masih fresh ({video.get('age_hours', 0):.1f} jam) dan memiliki breakout score {video.get('breakout_score', 0):.0f}/100.",
    }


def generate_ai_content_opportunity(video, query):
    if not GEMINI_API_KEY:
        return build_content_opportunity(video, query)
    compact = {
        'query': query, 'title': video.get('title'), 'duration': video.get('duration'),
        'views': video.get('raw_views'), 'velocity_vph': video.get('velocity_vph'),
        'acceleration': video.get('acceleration'), 'channel_breakout_multiple': video.get('channel_breakout_multiple'),
        'ratio': video.get('ratio'), 'engagement': video.get('er'), 'keywords': video.get('keywords', [])
    }
    prompt = f"""Buat content opportunity dari video YouTube yang sedang breakout. Jangan menyalin video.
Data: {json.dumps(compact, ensure_ascii=False)}
Berikan singkat: 1) topic gap, 2) hook original, 3) angle berbeda, 4) title formula, 5) thumbnail concept, 6) recommended duration, 7) why-now. Jangan mengarang fakta di luar data."""
    url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}'
    try:
        r = requests.post(url, headers={'Content-Type': 'application/json'}, json={'contents': [{'parts': [{'text': prompt}]}]}, timeout=60)
        r.raise_for_status()
        return r.json()['candidates'][0]['content']['parts'][0]['text']
    except Exception:
        return build_content_opportunity(video, query)


def generate_ai_winner_analysis(results, query):
    if not results: return 'Tidak ada data.'
    if not GEMINI_API_KEY: return '⚠️ GEMINI_API_KEY belum diisi.'
    top = sorted(results, key=lambda x: x.get('breakout_score', 0), reverse=True)[:12]
    compact = [{
        'title': v['title'], 'views': v['views'], 'velocity_vph': v.get('velocity_vph', 0),
        'acceleration': v.get('acceleration', 1), 'channel_multiple': v.get('channel_breakout_multiple', 0),
        'ratio': round(v.get('ratio', 0), 1), 'er': v.get('er', 0),
        'duration': v.get('duration'), 'score': v.get('breakout_score', 0)
    } for v in top]
    prompt = f"""Analisis kandidat long-form baru untuk niche '{query}'. Jangan mengarang data. Temukan pola velocity, acceleration, channel baseline, durasi, judul, engagement, dan content opportunity. Berikan: Why breakout, winning formula, 5 content opportunities, red flags. Data: {json.dumps(compact, ensure_ascii=False)}"""
    url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}'
    try:
        r = requests.post(url, headers={'Content-Type': 'application/json'}, json={'contents': [{'parts': [{'text': prompt}]}]}, timeout=60); r.raise_for_status()
        return r.json()['candidates'][0]['content']['parts'][0]['text']
    except Exception as e: return f'❌ Gagal analisis AI: {e}'


def get_artist_search_demand(artist, region_code='ID', freshness_days=7, max_results=25):
    """YouTube audience-interest proxy. This is NOT official YouTube search volume."""
    artist = (artist or '').strip()
    if not artist:
        return None
    published_after = get_published_after_rfc3339(freshness_days)
    for attempt in range(len(API_KEYS)):
        key_idx = (st.session_state.current_api_index + attempt) % len(API_KEYS)
        youtube = build('youtube', 'v3', developerKey=API_KEYS[key_idx])
        try:
            ids = []
            discovery = {}
            result_counts = []
            for order in ['relevance', 'date', 'viewCount']:
                params = {
                    'q': artist,
                    'part': 'snippet',
                    'type': 'video',
                    'order': order,
                    'maxResults': min(50, max(10, max_results)),
                }
                if region_code:
                    params['regionCode'] = region_code
                if published_after:
                    params['publishedAfter'] = published_after
                res = youtube.search().list(**params).execute()
                result_counts.append(res.get('pageInfo', {}).get('totalResults', 0))
                for item in res.get('items', []):
                    vid = item.get('id', {}).get('videoId')
                    if vid:
                        ids.append(vid)
                        discovery[vid] = order

            ids = list(dict.fromkeys(ids))[:50]
            if not ids:
                return {
                    'artist': artist, 'search_results_estimate': max(result_counts or [0]),
                    'videos_found': 0, 'recent_videos': 0, 'total_views': 0,
                    'avg_views': 0, 'median_views': 0, 'avg_vph': 0,
                    'engagement_rate': 0, 'longform_count': 0, 'shorts_like_count': 0,
                    'freshness_days': freshness_days, 'error': None
                }

            stats = youtube.videos().list(id=','.join(ids), part='snippet,statistics,contentDetails').execute()
            videos = []
            now = datetime.utcnow()
            for v in stats.get('items', []):
                sn = v.get('snippet', {})
                stt = v.get('statistics', {})
                cd = v.get('contentDetails', {})
                published = sn.get('publishedAt', '')
                try:
                    dt = parse_yt_date(published)
                    age_h = max((now - dt).total_seconds() / 3600, 0.1)
                except Exception:
                    age_h = 999999
                views = int(stt.get('viewCount', 0) or 0)
                likes = int(stt.get('likeCount', 0) or 0)
                comments = int(stt.get('commentCount', 0) or 0)
                duration_s = parse_iso_duration(cd.get('duration', 'PT0S'))
                videos.append({
                    'id': v.get('id'), 'views': views, 'likes': likes, 'comments': comments,
                    'age_h': age_h, 'duration_s': duration_s,
                    'vph': views / max(age_h, 1), 'source': discovery.get(v.get('id'), 'relevance')
                })

            views = [v['views'] for v in videos]
            vphs = [v['vph'] for v in videos]
            engagements = [((v['likes'] + v['comments']) / max(v['views'], 1)) * 100 for v in videos]
            recent = [v for v in videos if v['age_h'] <= 24 * min(freshness_days, 7)]
            longform = [v for v in videos if v['duration_s'] >= 240 and v['duration_s'] > 0]
            shorts_like = [v for v in videos if 0 < v['duration_s'] <= 60]

            # A transparent proxy: recent search-result presence + recent views + velocity + engagement.
            # It intentionally avoids pretending that YouTube exposes exact query search counts.
            freshness_presence = len(recent) / max(len(videos), 1) * 100
            avg_views = statistics.mean(views) if views else 0
            median_views = statistics.median(views) if views else 0
            avg_vph = statistics.mean(vphs) if vphs else 0
            er = statistics.mean(engagements) if engagements else 0
            result_estimate = max(result_counts or [0])
            return {
                'artist': artist,
                'search_results_estimate': result_estimate,
                'videos_found': len(videos),
                'recent_videos': len(recent),
                'total_views': sum(views),
                'avg_views': avg_views,
                'median_views': median_views,
                'avg_vph': avg_vph,
                'engagement_rate': er,
                'longform_count': len(longform),
                'shorts_like_count': len(shorts_like),
                'freshness_presence': freshness_presence,
                'freshness_days': freshness_days,
                'error': None,
            }
        except Exception as e:
            if 'quota' in str(e).lower() or '403' in str(e):
                continue
            return {'artist': artist, 'error': str(e)}
    return {'artist': artist, 'error': 'Semua API key gagal/kuota habis.'}


def normalize_artist_comparison(rows):
    valid = [r for r in rows if not r.get('error')]
    if not valid:
        return rows
    metrics = ['recent_videos', 'total_views', 'median_views', 'avg_vph', 'engagement_rate', 'longform_count']
    for r in valid:
        components = []
        for key in metrics:
            vals = [float(x.get(key, 0) or 0) for x in valid]
            lo, hi = min(vals), max(vals)
            value = float(r.get(key, 0) or 0)
            if hi == lo:
                score = 50.0
            else:
                score = (value - lo) / (hi - lo) * 100
            components.append(score)
        # Search-result estimate is deliberately shown as context, not treated as search volume.
        r['youtube_interest_score'] = round(
            components[0] * 0.20 + components[1] * 0.20 + components[2] * 0.15 +
            components[3] * 0.20 + components[4] * 0.10 + components[5] * 0.15, 1
        )
    return sorted(rows, key=lambda x: x.get('youtube_interest_score', -1), reverse=True)


def render_artist_comparison():
    st.title('🎤 Artist Comparison — YouTube Audience Interest')
    st.caption('Bandingkan beberapa artis menggunakan sinyal yang tersedia dari YouTube Data API.')
    st.info('ℹ️ YouTube Data API tidak menyediakan angka resmi berapa kali nama artis dicari. Jadi aplikasi menampilkan **YouTube Search Demand Proxy** berdasarkan kehadiran di hasil pencarian, video terbaru, views, velocity, engagement, dan long-form activity. Angka ini bukan search volume resmi YouTube.')

    with st.container(border=True):
        a1, a2 = st.columns(2)
        with a1:
            artist_1 = st.text_input('Artis 1', placeholder='Contoh: Taylor Swift', key='artist_1')
            artist_2 = st.text_input('Artis 2', placeholder='Contoh: Bruno Mars', key='artist_2')
            artist_3 = st.text_input('Artis 3', placeholder='Contoh: Adele', key='artist_3')
        with a2:
            artist_4 = st.text_input('Artis 4 (opsional)', placeholder='Contoh: The Weeknd', key='artist_4')
            artist_5 = st.text_input('Artis 5 (opsional)', placeholder='Contoh: Ed Sheeran', key='artist_5')
            region_name = st.selectbox('Region YouTube', list(COUNTRY_CODES.keys()), index=1, key='artist_region')
        freshness_label = st.selectbox('Window analisis', ['24 Jam', '3 Hari', '7 Hari', '30 Hari'], index=2, key='artist_freshness')
        if st.button('🔎 Bandingkan Artis', type='primary', use_container_width=True):
            artists = [x.strip() for x in [artist_1, artist_2, artist_3, artist_4, artist_5] if x.strip()]
            if len(artists) < 2:
                st.warning('Masukkan minimal 2 artis untuk dibandingkan.')
            else:
                days_map = {'24 Jam': 1, '3 Hari': 3, '7 Hari': 7, '30 Hari': 30}
                days = days_map[freshness_label]
                with st.spinner('Mengumpulkan sinyal pencarian dan performa YouTube...'):
                    rows = [get_artist_search_demand(a, COUNTRY_CODES[region_name], days, 25) for a in artists]
                st.session_state.artist_compare_results = normalize_artist_comparison(rows)
                st.session_state.artist_compare_window = freshness_label

    rows = st.session_state.get('artist_compare_results', [])
    if not rows:
        st.info('Masukkan minimal 2 artis lalu jalankan perbandingan.')
        return

    valid = [r for r in rows if not r.get('error')]
    if not valid:
        st.error('Tidak ada data yang berhasil diambil.')
        return

    st.markdown('### 📊 YouTube Search Demand Proxy')
    cols = st.columns(len(valid))
    for i, r in enumerate(valid):
        with cols[i]:
            st.metric(r['artist'], f"{r.get('youtube_interest_score', 0):.1f}/100")
            st.caption(f"{r.get('videos_found', 0)} video ditemukan • {r.get('recent_videos', 0)} video fresh")

    df = pd.DataFrame([{
        'Artist': r['artist'],
        'Interest Proxy': r.get('youtube_interest_score', 0),
        'Search Results (estimate)': r.get('search_results_estimate', 0),
        'Videos Found': r.get('videos_found', 0),
        'Fresh Videos': r.get('recent_videos', 0),
        'Total Views': int(r.get('total_views', 0)),
        'Median Views': int(r.get('median_views', 0)),
        'Avg VPH': int(r.get('avg_vph', 0)),
        'Engagement %': round(r.get('engagement_rate', 0), 2),
        'Long-form': r.get('longform_count', 0),
        'Shorts-like': r.get('shorts_like_count', 0),
    } for r in valid])
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown('### 🔥 Visual Comparison')
    chart_df = df.set_index('Artist')[['Interest Proxy', 'Avg VPH', 'Fresh Videos']]
    st.bar_chart(chart_df, use_container_width=True)

    st.markdown('### 🔎 Cara Membaca Data')
    st.markdown('''
- **Interest Proxy**: indikator relatif untuk membandingkan artis dalam scan yang sama, bukan jumlah pencarian.
- **Search Results (estimate)**: estimasi jumlah hasil yang dikembalikan mesin pencarian YouTube untuk query; ini **bukan** jumlah orang yang mencari.
- **Fresh Videos**: banyaknya video dalam sampel yang masih berada di window analisis.
- **Avg VPH**: rata-rata views per jam dari video sampel.
- **Median Views**: median views, lebih tahan terhadap satu video yang sangat besar.
- **Long-form / Shorts-like**: gambaran bentuk konten yang muncul dalam sampel.
''')

    st.markdown('### 💡 Catatan')
    st.caption('Untuk angka search interest yang benar-benar berasal dari data pencarian, gunakan Google Trends sebagai sumber terpisah. Google Trends juga memberikan indeks relatif, bukan jumlah pencarian absolut.')

    st.download_button('💾 Export Artist Comparison CSV', df.to_csv(index=False), 'artist_comparison.csv', 'text/csv', use_container_width=True)


# --- CALLBACK FUNCTIONS (AMAN) ---
def goto_analyzer(channel_id):
    st.session_state.stalk_channel = channel_id
    st.session_state.app_mode = "🕵️ Analisis Channel"

def add_to_compare_and_go(channel_id):
    if channel_id not in st.session_state.compare_list:
        if len(st.session_state.compare_list) >= 4:
            st.session_state.compare_list.pop(0) 
        st.session_state.compare_list.append(channel_id)
    st.session_state.app_mode = "⚖️ Bandingkan Channel"

def remove_from_compare(channel_id):
    if channel_id in st.session_state.compare_list:
        st.session_state.compare_list.remove(channel_id)

def trigger_dir_search():
    st.session_state.run_dir_search = True

# ==========================================
# 5. UI FRONTEND & STATE MANAGEMENT
# ==========================================

if 'app_mode' not in st.session_state: st.session_state.app_mode = "🔍 Pencarian Video"
if 'search_query' not in st.session_state: st.session_state.search_query = ""
if 'suggestions' not in st.session_state: st.session_state.suggestions = []
if 'results' not in st.session_state: st.session_state.results = []
if 'dir_results' not in st.session_state: st.session_state.dir_results = []
if 'stalk_channel' not in st.session_state: st.session_state.stalk_channel = None
if 'best_time' not in st.session_state: st.session_state.best_time = None
if 'rising_trends' not in st.session_state: st.session_state.rising_trends = None
if 'channel_search_results' not in st.session_state: st.session_state.channel_search_results = []
if 'compare_list' not in st.session_state: st.session_state.compare_list = []
if 'run_dir_search' not in st.session_state: st.session_state.run_dir_search = False
if 'viral_results' not in st.session_state: st.session_state.viral_results = []
if 'dna_results' not in st.session_state: st.session_state.dna_results = []
if 'artist_compare_results' not in st.session_state: st.session_state.artist_compare_results = []
if 'artist_compare_window' not in st.session_state: st.session_state.artist_compare_window = '7 Hari'

with st.sidebar:
    st.title("🎛️ Menu Navigasi")
    
    mode = st.radio("Pilih Mode:", [
        "🔍 Pencarian Video", 
        "🔥 Trending (Viral)",
        "⚡ Viral Intelligence",
        "🧭 Direktori Channel", 
        "🕵️ Analisis Channel", 
        "⚖️ Bandingkan Channel",
        "🎤 Bandingkan Artis"
    ], key="app_mode")
    st.markdown("---")
    
    st.caption(f"🔑 API Key Aktif: **Kunci ke-{st.session_state.current_api_index + 1}** (Dari {len(API_KEYS)})")
    
    if mode == "🔍 Pencarian Video":
        st.header("⚙️ Filter Pencarian")
        col_input, col_btn = st.columns([4, 1])
        with col_input:
            query_input = st.text_input("Kata Kunci Video", value=st.session_state.search_query, placeholder="Misal: ASMR Rain", key="q_input")
        with col_btn:
            st.markdown("<div style='margin-top:28px;'></div>", unsafe_allow_html=True)
            if st.button("💡", help="Klik untuk memunculkan ide Autocomplete dari YouTube"):
                if query_input:
                    with st.spinner("Mencari saran..."):
                        st.session_state.suggestions = get_youtube_suggestions(query_input)
                        st.session_state.search_query = query_input
                        st.rerun()

        if st.session_state.suggestions:
            st.caption("Pilih saran kata kunci:")
            sug_cols = st.columns(3)
            for idx, sug in enumerate(st.session_state.suggestions):
                with sug_cols[idx % 3]:
                    if st.button(sug, key=f"sug_{idx}", use_container_width=True, type="secondary"):
                        st.session_state.search_query = sug
                        st.session_state.suggestions = []
                        st.rerun()
            st.markdown("<div style='margin-bottom:15px;'></div>", unsafe_allow_html=True)

        st.session_state.search_query = query_input
        country_name = st.selectbox("🌍 Lokasi Negara", list(COUNTRY_CODES.keys()), index=1)
        c1, c2 = st.columns(2)
        with c1: dur = st.selectbox("Durasi", ["Semua", "Short (<4m)", "Medium (4-20m)", "Long (>20m)"])
        with c2: cat_name = st.selectbox("Kategori", list(CATEGORIES.keys()))
        time_label = st.selectbox("Waktu Publikasi", list(TIME_FILTERS.keys()))
        lic_label = st.selectbox("Lisensi", list(LICENSE_OPTIONS.keys()))
        sort_label = st.selectbox("Urutkan Berdasarkan", list(SORT_OPTIONS.keys()), index=0)
        max_res = st.slider("Jumlah Video Ditampilkan", min_value=5, max_value=50, value=12, step=1)
        btn_cari = st.button("🚀 Cari Video", type="primary", use_container_width=True)
    
    elif mode == "🔥 Trending (Viral)":
        st.header("⚙️ Filter Trending")
        country_name = st.selectbox("🌍 Negara Trending", list(COUNTRY_CODES.keys()), index=1)
        cat_name = st.selectbox("Kategori (Opsional)", list(CATEGORIES.keys()))
        max_res = st.slider("Jumlah Video Ditampilkan", min_value=5, max_value=50, value=12, step=1)
        btn_trending = st.button("🔥 Lihat Trending", type="primary", use_container_width=True)

    elif mode == "⚡ Viral Intelligence":
        st.header("⚡ Viral Intelligence V2")
        viral_query = st.text_input("Niche / Keyword", value=st.session_state.search_query, placeholder="Misal: AI tools, football, cooking")
        country_name = st.selectbox("🌍 Negara", list(COUNTRY_CODES.keys()), index=1, key="viral_country")
        cat_name = st.selectbox("Kategori", list(CATEGORIES.keys()), key="viral_cat")
        freshness_label = st.selectbox("🕒 Freshness", ["24 Jam", "3 Hari", "7 Hari", "14 Hari", "30 Hari"], index=2, key="viral_freshness")
        freshness_days = {"24 Jam": 1, "3 Hari": 3, "7 Hari": 7, "14 Hari": 14, "30 Hari": 30}[freshness_label]
        min_long_label = st.selectbox("🎬 Minimum Durasi", ["4 Menit+", "8 Menit+", "20 Menit+"], index=0, key="viral_min_duration")
        min_duration_seconds = {"4 Menit+": 240, "8 Menit+": 480, "20 Menit+": 1200}[min_long_label]
        max_res = st.slider("Jumlah Kandidat", 10, 50, 30, key="viral_max")
        btn_viral = st.button("🚀 Scan New Breakout Videos", type="primary", use_container_width=True)

    elif mode == "🧭 Direktori Channel":
        st.info("Pencarian utama direktori telah dipindah ke tengah layar utama.")

    elif mode == "🕵️ Analisis Channel":
        st.header("⚙️ Pencarian Spesifik")
        channel_query = st.text_input("Nama Channel", placeholder="Misal: MrBeast")
        btn_cari_channel = st.button("🔍 Cari Channel", type="primary", use_container_width=True)
        if st.session_state.stalk_channel:
            st.markdown("---")
            if st.button("❌ Tutup Analisis", use_container_width=True):
                st.session_state.stalk_channel = None
                st.session_state.channel_search_results = []
                st.rerun()
                
    elif mode == "⚖️ Bandingkan Channel":
        st.header("⚙️ Status Komparasi")
        st.info(f"Terdapat **{len(st.session_state.compare_list)}/4** channel dalam daftar perbandingan saat ini.")
        if st.button("🗑️ Bersihkan Daftar", use_container_width=True):
            st.session_state.compare_list = []
            st.rerun()

# ==========================================
# 6. LOGIKA HALAMAN UTAMA
# ==========================================

if mode in ["🔍 Pencarian Video", "🔥 Trending (Viral)"]:
    st.title(f"🚀 Niche Hunter: {mode.replace('🔍 ', '').replace('🔥 ', '')}")

    if mode == "🔍 Pencarian Video" and 'btn_cari' in locals() and btn_cari and st.session_state.search_query:
        st.session_state.stalk_channel = None 
        dur_map = {'Short (<4m)': 'short', 'Medium (4-20m)': 'medium', 'Long (>20m)': 'long'}.get(dur, 'any')
        with st.spinner(f"Mencari data video untuk '{st.session_state.search_query}'..."):
            st.session_state.results = search_youtube(
                query=st.session_state.search_query, region_code=COUNTRY_CODES[country_name], duration=dur_map,
                category_id=CATEGORIES[cat_name], published_after=get_published_after_rfc3339(TIME_FILTERS[time_label]),
                license_type=LICENSE_OPTIONS[lic_label], sort_order=SORT_OPTIONS[sort_label], max_results=max_res
            )
            st.session_state.best_time = estimate_best_time(st.session_state.results)
        with st.spinner("Menganalisis Google Trends..."):
            st.session_state.rising_trends = get_rising_trends(st.session_state.search_query, COUNTRY_CODES[country_name])

    if mode == "🔥 Trending (Viral)" and 'btn_trending' in locals() and btn_trending:
        st.session_state.stalk_channel = None
        with st.spinner(f"Mengambil {max_res} data Trending..."):
            st.session_state.results = get_trending_videos(
                region_code=COUNTRY_CODES[country_name], category_id=CATEGORIES[cat_name], max_results=max_res
            )
            st.session_state.best_time = estimate_best_time(st.session_state.results)
            st.session_state.rising_trends = None

    if mode == "🔍 Pencarian Video" and st.session_state.search_query:
        st.markdown("---")
        with st.expander("✨🤖 AI Daily Ideas: Generate Ide Konten Fresh!", expanded=False):
            st.markdown(f"Minta AI memikirkan ide video *out-of-the-box* berdasarkan kata kunci: **{st.session_state.search_query}**")
            if st.button("💡 Generate 5 Ide Viral", type="primary"):
                with st.spinner("AI sedang memutar otak menganalisis algoritma..."):
                    st.markdown(f"<div class='ai-box'>{generate_ai_ideas(st.session_state.search_query)}</div>", unsafe_allow_html=True)
        st.markdown("---")

    results = st.session_state.results
    if results:
        with st.expander("📊 Dasbor Analitik Pasar & SEO (vidIQ Style)", expanded=True):
            c_insight1, c_insight2 = st.columns(2)
            with c_insight1:
                st.markdown(f"""
<div class="insight-box">
<div class="insight-title">⏰ Waktu Upload Paling Ideal</div>
<div>Berdasarkan pola kompetitor teratas yang viral, usahakan melakukan publikasi / live streaming pada hari:</div>
<h3 style="margin-top:10px; color:var(--text-color);">{st.session_state.best_time}</h3>
</div>
""", unsafe_allow_html=True)
            with c_insight2:
                st.markdown(f"""<div class="insight-title" style="margin-bottom:10px;">📈 Google Trends: Rising Keywords (YouTube)</div>""", unsafe_allow_html=True)
                if mode == "🔥 Trending (Viral)":
                    st.info("ℹ️ Fitur Google Trends hanya aktif pada Mode Pencarian Kata Kunci.")
                elif st.session_state.rising_trends is None:
                    encoded_query = urllib.parse.quote(st.session_state.search_query)
                    geo_code = COUNTRY_CODES[country_name] if COUNTRY_CODES[country_name] else ''
                    trends_url = f"https://trends.google.com/trends/explore?date=now%207-d&gprop=youtube&q={encoded_query}&geo={geo_code}"
                    st.warning("⚠️ Server Streamlit sedang dibatasi oleh sistem Google Trends.")
                    st.link_button("📊 Cek Manual Langsung di Google Trends", trends_url, use_container_width=True)
                elif not st.session_state.rising_trends:
                    st.info("ℹ️ Tidak ada lonjakan tren signifikan untuk kata kunci ini dalam 7 hari terakhir.")
                else:
                    trends_html = "".join([f"<span class='seo-chip'>{t['query']}<span class='seo-count'>+{t['value']}%</span></span>" for t in st.session_state.rising_trends])
                    st.markdown(trends_html, unsafe_allow_html=True)
            st.markdown("---")
            df = pd.DataFrame(results)
            c_chart, c_seo = st.columns([2, 1])
            with c_chart:
                st.caption("📈 Performa Video Competitor (VPH)")
                st.bar_chart(df[['title', 'vph']].set_index('title').head(10))
            with c_seo:
                st.caption("🏷️ Top Tags Competitor")
                all_tags = [t for vid in results for t in vid['tags']]
                if all_tags: st.markdown("".join([f"<span class='seo-chip'>{t[0]}<span class='seo-count'>{t[1]}</span></span>" for t in Counter(all_tags).most_common(15)]), unsafe_allow_html=True)

        c_info, c_dl = st.columns([3, 1])
        with c_info: st.success(f"Menampilkan {len(results)} Video.")
        with c_dl: st.download_button("💾 CSV", pd.DataFrame(results).to_csv(index=False), "data_riset.csv", "text/csv", use_container_width=True)

        cols = st.columns(3)
        for i, vid in enumerate(results):
            with cols[i % 3]:
                border_color = "2px solid #0ea5e9" if vid['is_gem'] else "1px solid rgba(128,128,128,0.2)"
                trending_badge = f"<span class='rank-badge'>🔥 Trending #{vid['rank']}</span><br>" if mode == "🔥 Trending (Viral)" else ""
                with st.container(border=True):
                    st.markdown(f"""
<div style="border: {border_color}; border-radius:8px; padding:5px; margin-bottom:10px;">
{trending_badge}<a href="{vid['link']}" target="_blank"><img src="{vid['thumbnail']}" style="width:100%; border-radius:8px; margin-bottom:8px;"></a>
<div class="video-title">{vid["title"]}</div>
<div class="meta-info" style="margin-bottom:5px;">👤 {vid["channel"]} ({vid['subs']} Subs)<br>📅 {vid["published_simple"]} • <span class="duration-badge">⏱️ {vid['duration']}</span></div>
<div style="margin-bottom:8px;"><span class="money-badge" title="Estimasi Pendapatan">💰 {vid['earnings']}</span><span class="er-badge" title="Engagement Rate">📈 {vid['er']}%</span><span class="gem-badge" title="Views vs Subs Ratio">💎 {vid['ratio_label']}</span><span class="seo-badge" title="Skor Optimasi SEO ala vidIQ">🎯 SEO: {vid['seo_score']}</span></div>
<div class="stats-bar"><span>👁️ {vid['views_fmt']}</span><span>👍 {vid['likes']}</span><span>💬 {vid['comments']}</span></div>
<div class="vph-badge">🔥 {vid['vph_fmt']} VPH</div></div>
""", unsafe_allow_html=True)
                    
                    c_btn1, c_btn2 = st.columns(2)
                    with c_btn1:
                        st.button("🕵️ Bedah", key=f"stalk_{vid['id']}", on_click=goto_analyzer, args=(vid['channel_id'],), use_container_width=True)
                    with c_btn2:
                        st.button("⚖️ +Banding", key=f"comp_{vid['id']}", on_click=add_to_compare_and_go, args=(vid['channel_id'],), use_container_width=True)

                    with st.expander("🤖 Ringkasan & SEO Checklist"):
                        st.caption("🎯 **vidIQ SEO Checklist:**")
                        st.markdown(f'<div class="desc-box">{"".join([f"<div style=\'font-size:12px; margin-bottom:4px;\'>{check}</div>" for check in vid["seo_checks"]])}</div>', unsafe_allow_html=True)
                        st.caption("📝 **Ringkasan (Auto):**")
                        if vid['summary'] and vid['summary'] != ["Deskripsi terlalu pendek."]: st.markdown(f'<div class="desc-box">{"".join([f"<span class=\'summary-bullet\'>• {point}</span>" for point in vid["summary"]])}</div>', unsafe_allow_html=True)
                        else: st.markdown(f'<div class="desc-box" style="opacity:0.6;">Tidak ada ringkasan.</div>', unsafe_allow_html=True)
                        st.markdown("---")
                        c_l, c_r = st.columns(2)
                        with c_l: st.link_button("▶ Tonton", vid['link'], use_container_width=True)
                        with c_r:
                            try: st.download_button("⬇️ Thumb", requests.get(vid['thumbnail']).content, f"thumb_{vid['id']}.jpg", "image/jpeg", use_container_width=True)
                            except: pass

# --- MODE VIRAL INTELLIGENCE V2 ---
elif mode == "⚡ Viral Intelligence":
    st.title("⚡ Viral Intelligence V2 — Detect Before It Explodes")
    st.caption("Fokus: video panjang yang baru terbit dan menunjukkan sinyal breakout — bukan video Shorts lama.")
    if 'btn_viral' in locals() and btn_viral and viral_query:
        st.session_state.search_query = viral_query
        with st.spinner("🔎 Discovery: mencari video long-form baru + breakout candidates..."):
            st.session_state.viral_results = search_viral_longform(
                viral_query, COUNTRY_CODES[country_name], CATEGORIES[cat_name], max_res,
                freshness_days=freshness_days, min_duration_seconds=min_duration_seconds
            )
    results = st.session_state.get('viral_results', [])
    if results:
        patterns = analyze_winning_patterns(results)
        gems = small_channel_gems(results)
        st.success(f"{len(results)} kandidat long-form baru dianalisis dari window {freshness_label}.")

        top = results[0]
        m1,m2,m3,m4,m5 = st.columns(5)
        m1.metric("🏆 Breakout Score", f"{top.get('breakout_score',0):.0f}/100")
        m2.metric("🔥 Velocity", f"{top.get('velocity_vph',0):,} VPH")
        m3.metric("⚡ Acceleration", f"{top.get('acceleration',1):.1f}x")
        m4.metric("🎯 Channel Breakout", f"{top.get('channel_breakout_multiple',0):.1f}x")
        m5.metric("⏱️ Age", f"{top.get('age_hours',0):.1f}h")

        st.markdown("### 🚨 Breakout Radar")
        radar_left, radar_right = st.columns([1, 1.4])
        with radar_left:
            st.pyplot(radar_chart(top), use_container_width=True)
        with radar_right:
            st.markdown(f"**{top.get('viral_label','NORMAL')} — {top.get('title','')}**")
            st.write(f"**Channel:** {top.get('channel','Unknown')} • **Subscribers:** {top.get('subs','0')}")
            st.write(f"**Views:** {top.get('views_fmt','0')} • **Duration:** {top.get('duration','N/A')}")
            st.write("**Kenapa menarik:**")
            for reason in top.get('breakout_reasons', []):
                st.write(f"• {reason}")
            if top.get('channel_baseline_samples', 0) < 3:
                st.warning("Baseline channel masih tipis. Score sebaiknya dianggap sinyal awal, bukan kepastian viral.")
            st.link_button("▶ Tonton Video", top['link'], use_container_width=True)

        st.markdown("### 🚀 New Breakout Candidates")
        table_rows = []
        for i, x in enumerate(results[:20], 1):
            table_rows.append({
                '#': i, 'Label': x.get('viral_label'), 'Title': x.get('title'),
                'Score': x.get('breakout_score'), 'Age': f"{x.get('age_hours',0):.1f}h",
                'Velocity': f"{x.get('velocity_vph',0):,}", 'Accel': f"{x.get('acceleration',1):.1f}x",
                'Channel': f"{x.get('channel_breakout_multiple',0):.1f}x",
                'Views/Subs': f"{x.get('ratio',0):.1f}x"
            })
        st.dataframe(pd.DataFrame(table_rows), use_container_width=True, hide_index=True)

        st.markdown("### 🧠 Candidate Inspector + Radar")
        pick = st.selectbox("Pilih kandidat", range(min(15, len(results))), format_func=lambda i: results[i]['title'], key="v2_pick")
        selected = results[pick]
        c1,c2 = st.columns([1,1.5])
        with c1:
            st.pyplot(radar_chart(selected), use_container_width=True)
        with c2:
            st.markdown(f"#### {selected['viral_label']} — {selected['breakout_score']:.0f}/100")
            st.write(f"**{selected['channel']}** • {selected['subs']} subs • {selected['views_fmt']} views • {selected['duration']}")
            st.write(f"Velocity **{selected['velocity_vph']:,} VPH** • Acceleration **{selected['acceleration']:.1f}x**")
            st.write(f"Channel baseline: **{selected.get('channel_baseline_vph',0):,} VPH** • Breakout multiple **{selected.get('channel_breakout_multiple',0):.1f}x**")
            for reason in selected.get('breakout_reasons', []): st.write(f"• {reason}")

        st.markdown("### 💎 Small Channel Breakouts")
        if gems:
            st.dataframe(pd.DataFrame([{
                'Title': x['title'], 'Channel': x['channel'], 'Subs': x['subs'], 'Views': x['views_fmt'],
                'Velocity': x['velocity_vph'], 'Channel Breakout': f"{x.get('channel_breakout_multiple',0):.1f}x",
                'Score': x['breakout_score']
            } for x in gems[:15]]), use_container_width=True, hide_index=True)
        else:
            st.info("Belum ada small-channel breakout yang kuat di scan ini.")

        st.markdown("### 🎯 Content Opportunity")
        opp = build_content_opportunity(selected, viral_query)
        oc1, oc2 = st.columns(2)
        with oc1:
            st.markdown(f"**Topic:** {opp['topic']}")
            st.markdown(f"**Hook:** {opp['hook']}")
            st.markdown(f"**Angle:** {opp['angle']}")
            st.markdown(f"**Duration:** {opp['recommended_duration']}")
        with oc2:
            st.markdown(f"**Title Formula:** {opp['title_formula']}")
            st.markdown(f"**Thumbnail:** {opp['thumbnail']}")
            st.markdown(f"**Why Now:** {opp['why_now']}")
        if st.button("🤖 Generate Opportunity dengan AI", key="ai_content_opp"):
            with st.spinner("AI mencari angle original dari sinyal breakout..."):
                ai_opp = generate_ai_content_opportunity(selected, viral_query)
                if isinstance(ai_opp, dict):
                    st.json(ai_opp)
                else:
                    st.markdown(f"<div class='ai-box'>{ai_opp}</div>", unsafe_allow_html=True)

        st.markdown("### 🧬 Winning Pattern Detector")
        p1,p2,p3 = st.columns(3)
        p1.metric("Top Winners", patterns.get('top_count',0))
        p2.metric("Avg Duration", f"{patterns.get('avg_duration',0):.0f}s")
        p3.metric("Avg Breakout Score", patterns.get('avg_score',0))
        st.write("**Keyword:**", ", ".join(patterns.get('keywords',[])) or "—")
        st.write("**Pola judul:**", ", ".join([f"{k} ({v})" for k,v in patterns.get('title_patterns',{}).most_common()]) or "—")

        st.markdown("### 🤖 AI Breakout Analysis")
        if st.button("🧠 Analisis Kenapa Video Ini Berpotensi Meledak", key="ai_winner"):
            with st.spinner("AI membaca pola velocity + baseline + content..."):
                st.markdown(f"<div class='ai-box'>{generate_ai_winner_analysis(results, viral_query)}</div>", unsafe_allow_html=True)

        st.download_button("💾 Export Viral Intelligence V2 CSV", pd.DataFrame(results).to_csv(index=False), "viral_intelligence_v2.csv", "text/csv", use_container_width=True)
    else:
        st.info("Belum ada kandidat. Pilih niche lalu jalankan scan. V2 hanya memasukkan video baru long-form sesuai freshness window.")

# --- MODE DIREKTORI CHANNEL ---
elif mode == "🧭 Direktori Channel":
    st.markdown("<h1 style='text-align: center; margin-bottom: 5px;'>Temukan Niche Besar<br>Anda Selanjutnya</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: var(--text-color); opacity: 0.7; font-size:16px; margin-bottom:40px;'>Analisis top channel YouTube, temukan tren terbaru, dan dapatkan ide konten viral dengan bantuan AI.</p>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns([1, 4, 1, 1])
    with col2:
        search_niche_query = st.text_input("Search", placeholder="🔍 Ketik niche (misal: cover musik)", label_visibility="collapsed")
    with col3:
        use_filter = st.checkbox("⚙️ Filter", value=False)
    with col4:
        st.button("Cari Channel", type="primary", on_click=trigger_dir_search, use_container_width=True)

    sort_channel = "Banyak Ditonton (Teratas)"
    subs_filter = "Semua"
    vph_filter = "Semua"
    age_filter = "Semua"
    
    if use_filter:
        with st.container(border=True):
            st.markdown("##### ⚙️ Filter Pencarian & Sorting")
            f1, f2 = st.columns(2)
            with f1:
                subs_filter = st.selectbox("Subscribers", ["Semua", "0-1K", "1K-10K", "10K-100K", "100K-1M", "> 1M"])
                vph_filter = st.selectbox("Views / Jam (VPH)", ["Semua", "> 100", "> 500", "> 1000", "> 5000"])
            with f2:
                age_filter = st.selectbox("Umur Channel", ["Semua", "Kurang dari 1 Tahun", "1-3 Tahun", "Lebih dari 3 Tahun"])
                sort_channel = st.selectbox("Urutkan Berdasarkan", ["Banyak Ditonton (Teratas)", "Subscriber Terbanyak", "Video Terbanyak", "Channel Terbaru", "Tumbuh Tercepat"])

    if st.session_state.run_dir_search:
        if search_niche_query:
            with st.spinner(f"Mencari & menyaring channel untuk '{search_niche_query}'..."):
                st.session_state.dir_results = search_youtube_channels(
                    search_niche_query, max_results=20, sort_by=sort_channel, 
                    subs_filter=subs_filter, age_filter=age_filter, vph_filter=vph_filter
                )
        st.session_state.run_dir_search = False
                
    if st.session_state.dir_results:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""
<div style='display:flex; justify-content:space-between; align-items:flex-end; border-bottom: 1px solid rgba(128, 128, 128, 0.2); padding-bottom: 10px; margin-bottom: 20px;'>
<h3 style='margin:0; font-size:24px;'>Analisis Channel Teratas</h3>
<span style='font-size:14px; color:var(--text-color); opacity:0.7;'>{len(st.session_state.dir_results)} channel ditemukan</span>
</div>
""", unsafe_allow_html=True)
        
        cols = st.columns(4)
        for idx, ch in enumerate(st.session_state.dir_results):
            with cols[idx % 4]:
                safe_url = f"https://youtube.com/channel/{ch['id']}"
                
                st.markdown(f"""
<div class="ch-card" style="border-top: 5px solid {ch['card_color']};">
<div>
<div class="ch-card-header">
<div class="ch-header-left">
<img src="{ch['thumb']}" class="ch-avatar">
<div class="ch-title-wrap">
<p class="ch-title" title="{ch['title']}">{ch['title']}</p>
<p class="ch-handle">{ch.get('custom_url', '')}</p>
</div>
</div>
<div class="ch-header-icons">
<a href="{safe_url}" target="_blank" title="Klik Kanan -> Copy Link">🔗</a>
</div>
</div>
<div class="ch-metrics-grid">
<div class="ch-metric-item">
<div class="ch-metric-label">SUBSCRIBER</div>
<div class="ch-metric-value">{ch['subs']}</div>
</div>
<div class="ch-metric-item">
<div class="ch-metric-label">TOTAL TAYANGAN</div>
<div class="ch-metric-value">{ch['total_views']}</div>
</div>
<div class="ch-metric-item">
<div class="ch-metric-label">TOTAL VIDEO</div>
<div class="ch-metric-value">{ch['videos']}</div>
</div>
<div class="ch-metric-item">
<div class="ch-metric-label">RERATA TAYANGAN</div>
<div class="ch-metric-value">{ch['avg_views']}</div>
</div>
</div>
</div>
<div class="ch-footer">
<span>📅 Dibuat: {ch['published_at_str']}</span>
<span style="color: {ch['card_color']}; font-weight: 800; font-size: 13px; opacity: 1;">{ch['age']}</span>
</div>
</div>
""", unsafe_allow_html=True)
                
                c_b1, c_b2 = st.columns(2)
                with c_b1: st.button("🕵️ Bedah", key=f"dir_stalk_{ch['id']}", on_click=goto_analyzer, args=(ch['id'],), use_container_width=True)
                with c_b2: st.button("⚖️ Banding", key=f"dir_comp_{ch['id']}", on_click=add_to_compare_and_go, args=(ch['id'],), use_container_width=True)
                st.markdown("<br>", unsafe_allow_html=True)

# --- MODE ANALISIS CHANNEL (SATUAN) ---
elif mode == "🕵️ Analisis Channel":
    st.title("🕵️ Dasbor Intelijen Channel")
    
    if 'btn_cari_channel' in locals() and btn_cari_channel and channel_query:
        st.session_state.stalk_channel = None
        with st.spinner(f"Mencari channel dengan nama '{channel_query}'..."):
            st.session_state.channel_search_results = search_youtube_channels(channel_query, max_results=5)
            
    if not st.session_state.stalk_channel and st.session_state.channel_search_results:
        st.write("### Pilihan Channel:")
        
        ch_cols = st.columns(min(len(st.session_state.channel_search_results), 5))
        for idx, ch in enumerate(st.session_state.channel_search_results[:5]):
            with ch_cols[idx]:
                safe_url = f"https://youtube.com/channel/{ch['id']}"
                st.markdown(f"""
<div class="ch-card" style="border-top: 5px solid #0ea5e9;">
<div class="ch-card-header">
<div class="ch-header-left">
<img src="{ch['thumb']}" class="ch-avatar">
<div class="ch-title-wrap">
<p class="ch-title" title="{ch['title']}">{ch['title']}</p>
<p class="ch-handle">{ch.get('custom_url', '')}</p>
</div>
</div>
<div class="ch-header-icons">
<a href="{safe_url}" target="_blank" title="Klik Kanan -> Copy Link">🔗</a>
</div>
</div>
<div class="ch-metrics-grid">
<div class="ch-metric-item">
<div class="ch-metric-label">SUBSCRIBER</div>
<div class="ch-metric-value">{ch['subs']}</div>
</div>
<div class="ch-metric-item">
<div class="ch-metric-label">TOTAL VIDEO</div>
<div class="ch-metric-value">{ch['videos']}</div>
</div>
</div>
</div>
""", unsafe_allow_html=True)
                if st.button("Bedah Channel", key=f"btn_anl_{ch['id']}", use_container_width=True):
                    st.session_state.stalk_channel = ch['id']
                    st.rerun()
                        
    if st.session_state.stalk_channel:
        with st.spinner("Menggali strategi rahasia channel ini..."):
            ch_data = analyze_channel_deep(st.session_state.stalk_channel)
            
        if ch_data:
            safe_url = f"https://youtube.com/channel/{st.session_state.stalk_channel}"
            st.markdown(f"""
<div class="stalker-box" style="border: 2px solid #f43f5e; box-shadow: 0 0 20px rgba(244, 63, 94, 0.2);">
<div style="display:flex; align-items:center; gap:25px; margin-bottom:25px;">
<img src="{ch_data['thumb']}" style="border-radius:50%; width:100px; border:4px solid #f43f5e;">
<div>
<h1 style="margin:0; color:#f43f5e; display:flex; align-items:center; gap:10px;">{ch_data['title']} <a href="{safe_url}" target="_blank" title="Klik Kanan -> Copy Link" style="text-decoration:none; font-size:26px; color:var(--text-color); opacity:0.4;">🔗</a></h1>
<p style="margin:0; opacity:0.8; font-size:18px;">{ch_data['custom_url']} • <b>{ch_data['subs']}</b> Subscribers • <b>{ch_data['video_count']}</b> Videos</p>
</div>
</div>
<div style="display:flex; flex-wrap: wrap; gap:15px; margin-bottom:30px;">
<div style="flex:1; background:rgba(128,128,128,0.1); padding:20px; border-radius:10px; text-align:center;">
<div style="font-size:28px; font-weight:bold; color:#4ade80;">{ch_data['avg_recent_views']}</div>
<div style="font-size:14px; opacity:0.7;">Rata-rata Views (15 Video Terakhir)</div>
</div>
<div style="flex:1; background:rgba(128,128,128,0.1); padding:20px; border-radius:10px; text-align:center;">
<div style="font-size:28px; font-weight:bold; color:#facc15;">{ch_data['total_views']}</div>
<div style="font-size:14px; opacity:0.7;">Total Views Keseluruhan</div>
</div>
<div style="flex:1; background:rgba(244, 63, 94, 0.1); padding:20px; border-radius:10px; text-align:center; border: 1px solid rgba(244,63,94,0.3);">
<div style="font-size:28px; font-weight:bold; color:#f43f5e;">⏰ {ch_data['favorite_upload_hour']}</div>
<div style="font-size:14px; opacity:0.9; color:#f43f5e;">Pola Jam Upload Favorit</div>
</div>
</div>
<div style="margin-bottom: 25px;">
<div class="stalker-highlight" style="font-size:18px;">🎯 Strategi SEO Tersembunyi (Top 15 Tags Terbanyak):</div>
""", unsafe_allow_html=True)
            
            if ch_data['top_seo_tags']:
                tags_html = "".join([f"<span class='seo-chip' style='border-color:#f43f5e; font-size:14px; padding:8px 15px;'>{t[0]}<span class='seo-count' style='background:rgba(244,63,94,0.2); color:#f43f5e;'>{t[1]}x</span></span>" for t in ch_data['top_seo_tags']])
                st.markdown(tags_html, unsafe_allow_html=True)
                
                tags_list = [t[0] for t in ch_data['top_seo_tags']]
                st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
                st.caption("📋 **Copy Semua Tag untuk Videomu:**")
                st.code(", ".join(tags_list), language="text")
            else:
                st.info("Channel ini sangat natural/pelit tag. Mereka jarang menggunakan SEO Tags pada video terbarunya.")
                
            st.markdown(f"""
<hr style="border-color: rgba(128,128,128,0.2); margin-top:30px;">
<h3 style="margin-bottom:15px;">🎥 5 Video Terakhir Channel Ini:</h3>
</div>
""", unsafe_allow_html=True)

            sc1, sc2, sc3, sc4, sc5 = st.columns(5)
            for i, vid in enumerate(ch_data['recent_videos']):
                with [sc1, sc2, sc3, sc4, sc5][i]:
                    st.image(vid['thumb'], use_container_width=True)
                    st.caption(f"📅 {vid['date']}")
                    st.markdown(f"**👁️ {vid['views']} Views**")
                    st.markdown(f"<span style='font-size:12px; opacity:0.8;'>{vid['title']}</span>", unsafe_allow_html=True)

elif mode == "🎤 Bandingkan Artis":
    render_artist_comparison()

elif mode == "⚖️ Bandingkan Channel":
    st.title("⚖️ Perbandingan Channel (Head-to-Head)")
    st.write("Analisis kekuatan kompetitor secara berdampingan untuk melihat siapa yang lebih unggul dalam SEO dan performa.")
    
    if not st.session_state.compare_list:
        st.info("💡 **Daftar perbandingan masih kosong.** Silakan gunakan menu **Pencarian Video** atau **Direktori Channel**, lalu klik tombol **'⚖️ +Banding'** pada channel yang ingin dipelajari.")
    else:
        with st.spinner("Menarik data intelijen dari YouTube..."):
            cols = st.columns(len(st.session_state.compare_list))
            
            for idx, ch_id in enumerate(st.session_state.compare_list):
                with cols[idx]:
                    ch_data = analyze_channel_deep(ch_id)
                    if ch_data:
                        safe_comp_url = f"https://youtube.com/channel/{ch_id}"
                        st.markdown(f"""
<div class="stalker-box" style="border: 2px solid #8b5cf6; box-shadow: 0 0 15px rgba(139, 92, 246, 0.2); padding: 15px;">
<div style="display:flex; align-items:center; gap:15px; margin-bottom:15px;">
<img src="{ch_data['thumb']}" style="border-radius:50%; width:70px; border:3px solid #8b5cf6;">
<div>
<h3 style="margin:0; color:#8b5cf6; font-size:18px; display:flex; align-items:center; gap:8px;">{ch_data['title']} <a href="{safe_comp_url}" target="_blank" title="Klik Kanan -> Copy Link" style="text-decoration:none; font-size:18px; color:var(--text-color); opacity:0.4;">🔗</a></h3>
<p style="margin:0; opacity:0.8; font-size:12px;"><b>{ch_data['subs']}</b> Subs • <b>{ch_data['video_count']}</b> Vids</p>
</div>
</div>
<div style="display:flex; flex-direction: column; gap:10px; margin-bottom:20px;">
<div style="background:rgba(128,128,128,0.1); padding:10px; border-radius:8px; text-align:center;">
<div style="font-size:20px; font-weight:bold; color:#4ade80;">{ch_data['avg_recent_views']}</div>
<div style="font-size:11px; opacity:0.7;">Rata-rata Views</div>
</div>
<div style="background:rgba(128,128,128,0.1); padding:10px; border-radius:8px; text-align:center;">
<div style="font-size:20px; font-weight:bold; color:#facc15;">{ch_data['total_views']}</div>
<div style="font-size:11px; opacity:0.7;">Total Views</div>
</div>
<div style="background:rgba(139, 92, 246, 0.1); padding:10px; border-radius:8px; text-align:center; border: 1px solid rgba(139,92,246,0.3);">
<div style="font-size:20px; font-weight:bold; color:#8b5cf6;">⏰ {ch_data['favorite_upload_hour']}</div>
<div style="font-size:11px; opacity:0.9; color:#8b5cf6;">Jam Upload Favorit</div>
</div>
</div>
<div style="margin-bottom: 15px;">
<div class="stalker-highlight" style="font-size:14px; color:#8b5cf6;">🎯 Top SEO Tags:</div>
""", unsafe_allow_html=True)
                        
                        if ch_data['top_seo_tags']:
                            tags_html = "".join([f"<span class='seo-chip' style='border-color:#8b5cf6; font-size:11px; padding:4px 8px; margin:2px;'>{t[0]}<span class='seo-count' style='background:rgba(139,92,246,0.2); color:#8b5cf6;'>{t[1]}x</span></span>" for t in ch_data['top_seo_tags']])
                            st.markdown(tags_html, unsafe_allow_html=True)
                            
                            tags_list = [t[0] for t in ch_data['top_seo_tags']]
                            st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
                            st.code(", ".join(tags_list), language="text")
                        else:
                            st.info("Tidak menggunakan Tag.")
                            
                        st.markdown("</div></div>", unsafe_allow_html=True)
                        st.button("❌ Hapus dari Daftar", key=f"del_comp_{ch_id}", on_click=remove_from_compare, args=(ch_id,), use_container_width=True)
