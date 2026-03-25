import streamlit as st
from googleapiclient.discovery import build
import google.generativeai as genai
from datetime import datetime, timedelta, timezone
import pandas as pd
import requests
import re
import urllib.parse
import json
from collections import Counter
from pytrends.request import TrendReq

# ==========================================
# 1. KONFIGURASI HALAMAN
# ==========================================
st.set_page_config(page_title="Pro Niche Finder V10.0 (Ultimate Compare)", layout="wide", page_icon="🏢")

# --- API KEY SETUP ---
try:
    YOUTUBE_API_KEY = st.secrets["YOUTUBE_API_KEY"]
except:
    st.error("API Key YouTube belum disetting di Secrets!")
    st.stop()

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
    .stalker-box { background-color: var(--secondary-background-color); color: var(--text-color); padding: 20px; border-radius: 15px; margin-bottom: 20px; border: 1px solid rgba(128, 128, 128, 0.2); }
    .stalker-stat { text-align: center; border-right: 1px solid rgba(128, 128, 128, 0.2); }
    .insight-box { background-color: rgba(14, 165, 233, 0.1); border-left: 4px solid #0ea5e9; padding: 15px; border-radius: 0 8px 8px 0; margin-bottom: 15px; }
    .insight-title { font-weight: bold; color: #0ea5e9; margin-bottom: 5px; display: flex; align-items: center; gap: 8px; }
    .stButton > button[kind="secondary"] { border-radius: 20px; padding: 2px 12px; font-size: 12px; border: 1px solid #0ea5e9; color: #0ea5e9; background: transparent; }
    .stButton > button[kind="secondary"]:hover { background: rgba(14, 165, 233, 0.1); }
    .stalker-highlight { font-size: 16px; font-weight: bold; color: #f43f5e; margin-bottom: 5px; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 4. FUNGSI LOGIKA (BACKEND)
# ==========================================

def search_youtube_channels(query, max_results=5):
    try:
        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
        res = youtube.search().list(q=query, type='channel', part='snippet', maxResults=max_results).execute()
        ch_ids = [item['snippet']['channelId'] for item in res.get('items', [])]
        
        if not ch_ids: return []
        
        stats_res = youtube.channels().list(id=','.join(ch_ids), part='snippet,statistics').execute()
        channels = []
        for item in stats_res.get('items', []):
            channels.append({
                'id': item['id'],
                'title': item['snippet']['title'],
                'thumb': item['snippet']['thumbnails'].get('medium', item['snippet']['thumbnails'].get('default', {}))['url'],
                'subs': format_number(int(item['statistics'].get('subscriberCount', 0))),
                'videos': format_number(int(item['statistics'].get('videoCount', 0)))
            })
        return channels
    except: return []

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
            dt = datetime.strptime(r['published_full'], "%Y-%m-%dT%H:%M:%SZ") + timedelta(hours=7) 
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

def format_number(num):
    if num >= 1000000: return f"{num/1000000:.1f}M"
    if num >= 1000: return f"{num/1000:.1f}K"
    return str(num)

def calculate_vph(published_at_str, current_views):
    try:
        pub_date = datetime.strptime(published_at_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
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

def get_published_after_rfc3339(days):
    return (datetime.utcnow() - timedelta(days=days)).isoformat("T") + "Z" if days else None

def get_channel_subs(youtube, channel_ids):
    try:
        res = youtube.channels().list(id=','.join(channel_ids), part='statistics').execute()
        return {item['id']: int(item['statistics'].get('subscriberCount', 0)) for item in res.get('items', [])}
    except: return {}

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
    try:
        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
        ch_data = youtube.channels().list(id=channel_id, part='snippet,statistics').execute()['items'][0]
        search_res = youtube.search().list(channelId=channel_id, part='snippet', type='video', order='date', maxResults=15).execute()
        vid_ids = [item['id']['videoId'] for item in search_res.get('items', [])]
        
        recent_videos = []
        all_tags = []
        upload_hours = []
        
        if vid_ids:
            stats = youtube.videos().list(id=','.join(vid_ids), part='snippet,statistics').execute()
            for i, item in enumerate(stats['items']):
                snippet = item['snippet']
                views = int(item['statistics'].get('viewCount', 0))
                try:
                    pub_dt = datetime.strptime(snippet['publishedAt'], "%Y-%m-%dT%H:%M:%SZ") + timedelta(hours=7)
                    upload_hours.append(pub_dt.hour)
                except: pass
                
                vid_tags = snippet.get('tags', [])
                all_tags.extend(vid_tags)
                
                if i < 5:
                    recent_videos.append({
                        'title': snippet['title'], 
                        'views': format_number(views),
                        'raw_views': views,
                        'date': snippet['publishedAt'][:10], 
                        'thumb': snippet['thumbnails'].get('medium', snippet['thumbnails'].get('default', {}))['url']
                    })
        
        best_hour_str = "Tidak diketahui"
        if upload_hours:
            most_common_hour = Counter(upload_hours).most_common(1)[0][0]
            best_hour_str = f"Pukul {most_common_hour:02d}:00 WIB"
            
        top_tags = Counter(all_tags).most_common(15)
        avg_views_calc = sum([v['raw_views'] for v in recent_videos]) / len(recent_videos) if recent_videos else 0

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
    except: return None

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
                'published_simple': snippet.get('publishedAt', '')[:10],
                'duration': parse_duration(content.get('duration', 'PT0S')), 'description': desc,
                'summary': smart_summarize(desc), 'keywords': extract_keywords(desc + " " + snippet.get('title', '')),
                'views': views, 'views_fmt': format_number(views), 'likes': format_number(likes), 'comments': format_number(comments),
                'vph': calculate_vph(snippet.get('publishedAt', ''), views), 'vph_fmt': f"{calculate_vph(snippet.get('publishedAt', ''), views):,.0f}", 
                'earnings': estimate_earnings(views, region_code), 'er': calculate_er(views, likes, comments), 
                'subs': format_number(subs), 'ratio': (views/subs if subs > 0 else 0), 'ratio_label': f"{(views/subs if subs>0 else 0):.1f}x", 
                'is_gem': (views/subs if subs > 0 else 0) > 1.5, 'tags': tags, 'seo_score': seo_score, 'seo_checks': seo_checks,
                'link': f"https://youtu.be/{video_id}"
            })
        except: continue 
    return results

def search_youtube(query, region_code='ID', duration='any', category_id=None, published_after=None, license_type=None, sort_order='relevance', max_results=12):
    try:
        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
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
        return results
    except Exception as e:
        st.error(f"Error API: {e}")
        return []

def get_trending_videos(region_code='ID', category_id=None, max_results=12):
    try:
        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
        params = {'part': 'snippet,statistics,contentDetails', 'chart': 'mostPopular', 'regionCode': region_code, 'maxResults': max_results}
        if category_id: params['videoCategoryId'] = category_id
        response = youtube.videos().list(**params).execute()
        return process_video_response(response.get('items', []), youtube, region_code)
    except Exception as e: return []

def goto_analyzer(channel_id):
    st.session_state.stalk_channel = channel_id
    st.session_state.app_mode = "🕵️ Analisis Channel"

# ==========================================
# 5. UI FRONTEND & STATE MANAGEMENT
# ==========================================

if 'app_mode' not in st.session_state: st.session_state.app_mode = "🔍 Pencarian Video"
if 'search_query' not in st.session_state: st.session_state.search_query = ""
if 'suggestions' not in st.session_state: st.session_state.suggestions = []
if 'results' not in st.session_state: st.session_state.results = []
if 'stalk_channel' not in st.session_state: st.session_state.stalk_channel = None
if 'best_time' not in st.session_state: st.session_state.best_time = None
if 'rising_trends' not in st.session_state: st.session_state.rising_trends = None
if 'channel_search_results' not in st.session_state: st.session_state.channel_search_results = []
if 'compare_results' not in st.session_state: st.session_state.compare_results = []

with st.sidebar:
    st.title("🎛️ Menu Navigasi")
    
    # 4 MENU UTAMA SEKARANG
    mode = st.radio("Pilih Mode:", ["🔍 Pencarian Video", "🔥 Trending (Viral)", "🕵️ Analisis Channel", "⚖️ Bandingkan Channel"], key="app_mode")
    st.markdown("---")
    
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
            st.caption("Pilih saran kata kunci (Autocomplete):")
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

    elif mode == "🕵️ Analisis Channel":
        st.header("⚙️ Pencarian Channel")
        channel_query = st.text_input("Nama Channel", placeholder="Misal: MrBeast")
        btn_cari_channel = st.button("🔍 Cari Channel", type="primary", use_container_width=True)
        if st.session_state.stalk_channel:
            st.markdown("---")
            if st.button("❌ Tutup Analisis", use_container_width=True):
                st.session_state.stalk_channel = None
                st.session_state.channel_search_results = []
                st.rerun()
                
    elif mode == "⚖️ Bandingkan Channel":
        st.header("⚙️ Head-to-Head")
        compare_input = st.text_input("Masukkan nama channel (Pisahkan dengan koma):", placeholder="Misal: ASMR Bakery, Nona Vlogs")
        btn_compare = st.button("⚖️ Bandingkan Sekarang", type="primary", use_container_width=True)

# ==========================================
# 6. LOGIKA HALAMAN UTAMA
# ==========================================

# --- MODE PENCARIAN & TRENDING ---
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
                    
                    st.button("🕵️ Bedah Channel", key=f"stalk_{vid['id']}", on_click=goto_analyzer, args=(vid['channel_id'],), use_container_width=True)

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

# --- MODE ANALISIS CHANNEL ---
elif mode == "🕵️ Analisis Channel":
    st.title("🕵️ Dasbor Intelijen Channel")
    
    if 'btn_cari_channel' in locals() and btn_cari_channel and channel_query:
        st.session_state.stalk_channel = None
        with st.spinner(f"Mencari channel dengan nama '{channel_query}'..."):
            st.session_state.channel_search_results = search_youtube_channels(channel_query)
            
    if not st.session_state.stalk_channel and st.session_state.channel_search_results:
        st.write("### Pilihan Channel:")
        ch_cols = st.columns(min(len(st.session_state.channel_search_results), 5))
        for idx, ch in enumerate(st.session_state.channel_search_results[:5]):
            with ch_cols[idx]:
                with st.container(border=True):
                    st.image(ch['thumb'], width=80)
                    st.markdown(f"**{ch['title'][:20]}**")
                    st.caption(f"👥 {ch['subs']} | 🎥 {ch['videos']}")
                    if st.button("Analisis", key=f"btn_anl_{ch['id']}", use_container_width=True):
                        st.session_state.stalk_channel = ch['id']
                        st.rerun()
                        
    if st.session_state.stalk_channel:
        with st.spinner("Menggali strategi rahasia channel ini..."):
            ch_data = analyze_channel_deep(st.session_state.stalk_channel)
            
        if ch_data:
            st.markdown(f"""
<div class="stalker-box" style="border: 2px solid #f43f5e; box-shadow: 0 0 20px rgba(244, 63, 94, 0.2);">
<div style="display:flex; align-items:center; gap:25px; margin-bottom:25px;">
<img src="{ch_data['thumb']}" style="border-radius:50%; width:100px; border:4px solid #f43f5e;">
<div>
<h1 style="margin:0; color:#f43f5e;">{ch_data['title']}</h1>
<p style="margin:0; opacity:0.8; font-size:18px;">{ch_data['custom_url']} • <b>{ch_data['subs']}</b> Subscribers • <b>{ch_data['video_count']}</b> Videos</p>
</div>
</div>
<div style="display:flex; gap:15px; margin-bottom:30px;">
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
                tags_html = "".join([f"<span class='seo-chip' style='border-color:#f43f5e; font-size:14px; padding:8px 15px;'>{t[0]}<span class='seo-count' style='background:rgba(244,63,94,0.2); color:#f43f5e;'>{t[1]}x dipakai</span></span>" for t in ch_data['top_seo_tags']])
                st.markdown(tags_html, unsafe_allow_html=True)
                
                # --- FITUR BARU: COPY TAGS MUDAH ---
                tags_list = [t[0] for t in ch_data['top_seo_tags']]
                tags_string = ", ".join(tags_list)
                st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
                st.caption("📋 **Copy Semua Tag untuk Videomu:**")
                st.code(tags_string, language="text")
                # ------------------------------------
                
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
                    
        else:
            st.error("Gagal menarik data mendalam untuk channel ini. Mungkin ID tidak valid atau sedang dibatasi oleh YouTube.")
            
    elif not st.session_state.channel_search_results:
        st.info("👈 Silakan gunakan menu **Pencarian Channel** di sidebar kiri untuk mencari nama YouTuber yang ingin dianalisis, atau gunakan tombol **'Bedah Channel'** saat sedang meriset video.")

# --- MODE BARU: BANDINGKAN CHANNEL ---
elif mode == "⚖️ Bandingkan Channel":
    st.title("⚖️ Perbandingan Channel (Head-to-Head)")
    st.write("Analisis kekuatan kompetitor secara berdampingan untuk melihat siapa yang lebih unggul dalam SEO dan performa.")
    
    if 'btn_compare' in locals() and btn_compare and compare_input:
        channel_names = [name.strip() for name in compare_input.split(",") if name.strip()]
        
        if len(channel_names) < 2:
            st.warning("⚠️ Masukkan minimal 2 nama channel yang dipisahkan dengan koma.")
        else:
            with st.spinner("Mengumpulkan data intelijen dari YouTube..."):
                st.session_state.compare_results = []
                for name in channel_names[:4]: # Batasi maksimal 4 channel agar tidak berat
                    ch_search = search_youtube_channels(name, max_results=1)
                    if ch_search:
                        ch_deep = analyze_channel_deep(ch_search[0]['id'])
                        if ch_deep:
                            st.session_state.compare_results.append(ch_deep)
                            
    if st.session_state.compare_results:
        cols = st.columns(len(st.session_state.compare_results))
        for idx, ch in enumerate(st.session_state.compare_results):
            with cols[idx]:
                with st.container(border=True):
                    st.image(ch['thumb'], width=80)
                    st.markdown(f"<h3 style='color:#0ea5e9; margin-bottom:0;'>{ch['title']}</h3>", unsafe_allow_html=True)
                    st.caption(f"{ch['custom_url']}")
                    st.markdown("---")
                    
                    st.metric("👥 Subscribers", ch['subs'])
                    st.metric("📈 Total Views", ch['total_views'])
                    st.metric("🔥 Rata-rata Views (Terbaru)", ch['avg_recent_views'])
                    st.metric("🎥 Total Video", ch['video_count'])
                    st.metric("⏰ Jam Upload Favorit", ch['favorite_upload_hour'].replace("Pukul ", ""))
                    
                    st.markdown("---")
                    st.markdown("**🏷️ Top 5 Strategi Tag:**")
                    if ch['top_seo_tags']:
                        tags_str = ", ".join([t[0] for t in ch['top_seo_tags'][:5]])
                        st.info(tags_str)
                    else:
                        st.warning("Tidak menggunakan Tag SEO.")
