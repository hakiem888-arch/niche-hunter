import streamlit as st
from googleapiclient.discovery import build
import google.generativeai as genai
from datetime import datetime, timedelta, timezone
import pandas as pd
import requests
import re
from collections import Counter

# ==========================================
# 1. KONFIGURASI HALAMAN
# ==========================================
st.set_page_config(page_title="Pro Niche Finder V6.0 (AI Edition)", layout="wide", page_icon="🤖")

# --- API KEY SETUP ---
try:
    YOUTUBE_API_KEY = st.secrets["YOUTUBE_API_KEY"]
except:
    st.error("API Key YouTube belum disetting di Secrets!")
    st.stop()

# Inisialisasi Gemini AI (Tidak akan error jika belum dipasang, hanya memberi warning nanti)
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

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
    "VPH Tertinggi (Custom)": "vph_custom",
    "Golden Ratio (Custom)": "ratio_custom",
    "Skor SEO Terbaik (Custom)": "seo_custom"
}

TIME_FILTERS = {
    "Kapan Saja": None,
    "Hari Ini (24 Jam)": 1,
    "Minggu Ini": 7,
    "Bulan Ini": 30,
    "Tahun Ini": 365
}

# ==========================================
# 3. CUSTOM CSS
# ==========================================
st.markdown("""
<style>
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: var(--secondary-background-color);
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-radius: 12px; padding: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
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
    .seo-count { background: rgba(128, 128, 128, 0.2); padding: 0 5px; border-radius: 4px; font-size: 10px; font-weight: bold; margin-left: 5px; }
    .desc-box { font-size: 12px; background: var(--background-color); padding: 10px; border-radius: 6px; border: 1px dashed rgba(128, 128, 128, 0.3); line-height: 1.5; margin-bottom: 10px; }
    .ai-box { background: linear-gradient(145deg, #1e1e2f, #2a2a40); color: #e2e8f0; padding: 20px; border-radius: 12px; border: 1px solid #4f46e5; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(79, 70, 229, 0.2); }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 4. FUNGSI LOGIKA (BACKEND)
# ==========================================

# --- FITUR BARU: AI DAILY IDEAS GENERATOR ---
def generate_ai_ideas(niche_query):
    if not GEMINI_API_KEY:
        return "⚠️ **Error:** GEMINI_API_KEY belum diisi di Streamlit Secrets. Silakan tambahkan kuncinya terlebih dahulu."
    
    prompt = f"""
    Kamu adalah pakar YouTube SEO dan Content Strategist profesional setingkat ahli dari vidIQ.
    Pengguna sedang mencari referensi konten dengan kata kunci/niche: "{niche_query}"
    
    Tugasmu adalah memberikan 5 ide konten video YouTube yang unik, punya potensi viral tinggi, dan masih jarang dibuat orang di niche tersebut. 
    Untuk setiap ide, wajib sertakan format berikut:
    
    ### Ide [Nomor]
    * **💡 Judul Video:** (Buat clickbait tapi jujur, maksimalkan CTR)
    * **🖼️ Konsep Thumbnail:** (Jelaskan elemen visual, teks/tulisan, dan warna kontras yang harus ada di gambar)
    * **🔥 Alasan Menang:** (Kenapa ide ini bakal disukai algoritma & penonton dibandingkan video kompetitor)
    
    Gunakan bahasa Indonesia yang asik, jelas, dan mudah dipahami.
    """
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ Gagal menghasilkan ide dari AI. Error: {e}"

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

def calculate_seo_score(title, desc, tags):
    score = 0
    checks = []
    if 20 <= len(title) <= 60:
        score += 40
        checks.append("✅ Panjang Judul Ideal (20-60 karakter)")
    else:
        score += 20
        checks.append(f"❌ Judul Kurang Optimal ({len(title)} karakter)")
        
    if len(desc) > 200:
        score += 30
        checks.append("✅ Deskripsi Panjang & Informatif")
    elif len(desc) > 0:
        score += 10
        checks.append("❌ Deskripsi Terlalu Pendek")
    else:
        checks.append("❌ Tidak Ada Deskripsi")
        
    if tags and len(tags) >= 3:
        score += 30
        checks.append(f"✅ Menggunakan Tags ({len(tags)} tags terdeteksi)")
    else:
        checks.append("❌ Minim / Tidak Ada Tags")
    return score, checks

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

def extract_keywords(text):
    words = re.findall(r'\w+', text.lower())
    common_stops = ['yang', 'dan', 'di', 'ke', 'dari', 'ini', 'itu', 'untuk', 'dengan', 'adalah', 'video', 'saya', 'aku']
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
             recent_videos, avg_recent_views = [], 0
        else:
            recent_stats_res = youtube.videos().list(id=','.join(vid_ids), part='statistics').execute()
            recent_videos, total_recent_views = [], 0
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
            'title': snippet['title'], 'thumb': snippet['thumbnails']['medium']['url'],
            'custom_url': snippet.get('customUrl', ''), 'subs': format_number(int(stats.get('subscriberCount', 0))),
            'total_views': format_number(int(stats.get('viewCount', 0))), 'video_count': format_number(int(stats.get('videoCount', 0))),
            'avg_recent_views': format_number(avg_recent_views), 'recent_videos': recent_videos
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
        vph = calculate_vph(snippet['publishedAt'], views)
        tags = snippet.get('tags', [])[:10]
        desc = snippet.get('description', '')
        seo_score, seo_checks = calculate_seo_score(snippet['title'], desc, tags)

        results.append({
            'rank': i + 1, 'id': item['id'], 'channel_id': channel_id,
            'title': snippet['title'], 'thumbnail': snippet['thumbnails'].get('high', snippet['thumbnails'].get('medium'))['url'],
            'channel': snippet['channelTitle'], 'published_simple': snippet['publishedAt'][:10],
            'duration': parse_duration(content.get('duration', 'PT0S')), 'description': desc[:150]+"...",
            'views': views, 'views_fmt': format_number(views), 'likes': format_number(likes), 'comments': format_number(comments),
            'vph': vph, 'vph_fmt': f"{vph:,.0f}", 'earnings': estimate_earnings(views, region_code),
            'er': calculate_er(views, likes, comments), 'subs': format_number(subs),
            'ratio': ratio, 'ratio_label': f"{ratio:.1f}x", 'is_gem': ratio > 1.5,
            'tags': tags, 'seo_score': seo_score, 'seo_checks': seo_checks,
            'link': f"https://youtu.be/{item['id']}" if isinstance(item['id'], str) else f"https://youtu.be/{item['id']['videoId']}"
        })
    return results

def search_youtube(query, region_code='ID', duration='any', category_id=None, published_after=None, sort_order='relevance', max_results=12):
    try:
        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
        api_order = 'viewCount' if sort_order in ['vph_custom', 'ratio_custom', 'seo_custom'] else sort_order
        search_params = {'q': query, 'part': 'snippet', 'type': 'video', 'maxResults': max_results, 'order': api_order}
        if region_code: search_params['regionCode'] = region_code
        if duration != 'any': search_params['videoDuration'] = duration
        if category_id: search_params['videoCategoryId'] = category_id
        if published_after: search_params['publishedAfter'] = published_after
        
        search_response = youtube.search().list(**search_params).execute()
        video_ids = [item['id']['videoId'] for item in search_response['items']]
        if not video_ids: return []

        stats_response = youtube.videos().list(part='snippet,statistics,contentDetails', id=','.join(video_ids)).execute()
        results = process_video_response(stats_response['items'], youtube, region_code)
        
        if sort_order == 'vph_custom': return sorted(results, key=lambda x: x['vph'], reverse=True)
        elif sort_order == 'ratio_custom': return sorted(results, key=lambda x: x['ratio'], reverse=True)
        elif sort_order == 'seo_custom': return sorted(results, key=lambda x: x['seo_score'], reverse=True)
        return results
    except Exception as e: return []

# ==========================================
# 5. UI FRONTEND
# ==========================================

with st.sidebar:
    st.title("🎛️ Menu Navigasi")
    mode = st.radio("Pilih Mode:", ["🔍 Pencarian Kata Kunci", "🔥 Trending (Viral)"])
    st.markdown("---")
    
    if mode == "🔍 Pencarian Kata Kunci":
        query = st.text_input("Kata Kunci", placeholder="Misal: Tutorial Python")
        country_name = st.selectbox("🌍 Lokasi Negara", list(COUNTRY_CODES.keys()), index=1)
        dur = st.selectbox("Durasi", ["Semua", "Short (<4m)", "Medium (4-20m)", "Long (>20m)"])
        time_label = st.selectbox("Waktu Publikasi", list(TIME_FILTERS.keys()))
        sort_label = st.selectbox("Urutkan Berdasarkan", list(SORT_OPTIONS.keys()), index=0)
        btn_cari = st.button("🚀 Cari Video", type="primary", use_container_width=True)

st.title(f"🕵️ Niche Hunter V6.0 (AI Edition)")

if 'results' not in st.session_state: st.session_state.results = []
if 'stalk_channel' not in st.session_state: st.session_state.stalk_channel = None

if mode == "🔍 Pencarian Kata Kunci" and 'btn_cari' in locals() and btn_cari and query:
    st.session_state.stalk_channel = None 
    dur_map = {'Short (<4m)': 'short', 'Medium (4-20m)': 'medium', 'Long (>20m)': 'long'}.get(dur, 'any')
    with st.spinner(f"Mencari data untuk '{query}'..."):
        st.session_state.results = search_youtube(
            query=query, region_code=COUNTRY_CODES[country_name], duration=dur_map,
            published_after=get_published_after_rfc3339(TIME_FILTERS[time_label]),
            sort_order=SORT_OPTIONS[sort_label]
        )

# --- BLOK UI AI GENERATOR ---
if mode == "🔍 Pencarian Kata Kunci" and query:
    st.markdown("---")
    with st.expander("✨🤖 AI Daily Ideas: Generate Ide Konten Fresh!", expanded=False):
        st.markdown(f"Minta AI memikirkan ide video *out-of-the-box* berdasarkan kata kunci: **{query}**")
        if st.button("💡 Generate 5 Ide Viral", type="primary"):
            with st.spinner("AI sedang memutar otak menganalisis algoritma..."):
                ai_result = generate_ai_ideas(query)
                st.markdown(f"<div class='ai-box'>{ai_result}</div>", unsafe_allow_html=True)
    st.markdown("---")

results = st.session_state.results

if results:
    st.success(f"Berhasil menemukan {len(results)} Video.")
    cols = st.columns(3)
    for i, vid in enumerate(results):
        with cols[i % 3]:
            border_color = "2px solid #0ea5e9" if vid['is_gem'] else "1px solid rgba(128,128,128,0.2)"
            with st.container(border=True):
                st.markdown(f"""
<div style="border: {border_color}; border-radius:8px; padding:5px; margin-bottom:10px;">
<a href="{vid['link']}" target="_blank">
<img src="{vid['thumbnail']}" style="width:100%; border-radius:8px; margin-bottom:8px;">
</a>
<div class="video-title">{vid["title"]}</div>
<div class="meta-info" style="margin-bottom:5px;">👤 {vid["channel"]} ({vid['subs']} Subs)<br>📅 {vid["published_simple"]} • ⏱️ {vid['duration']}</div>
<div style="margin-bottom:8px;">
<span class="money-badge">💰 {vid['earnings']}</span>
<span class="gem-badge">💎 {vid['ratio_label']}</span>
<span class="seo-badge">🎯 SEO: {vid['seo_score']}</span>
</div>
<div class="stats-bar"><span>👁️ {vid['views_fmt']}</span><span>👍 {vid['likes']}</span><span>💬 {vid['comments']}</span></div>
<div class="vph-badge">🔥 {vid['vph_fmt']} VPH</div>
</div>
""", unsafe_allow_html=True)
                with st.expander("SEO Checklist & Info"):
                    checks_html = "".join([f"<div style='font-size:12px;'>{check}</div>" for check in vid['seo_checks']])
                    st.markdown(f'<div class="desc-box">{checks_html}</div>', unsafe_allow_html=True)
                    st.caption("📝 Deskripsi:")
                    st.markdown(f"<div class='desc-box'>{vid['description']}</div>", unsafe_allow_html=True)
