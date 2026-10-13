# Niche Hunter, SEO Studio dan ruang riset

Versi pengembangan 13 Oktober 2026. Aplikasi riset YouTube pribadi berbasis Streamlit. Tujuh mode awal tetap tersedia, ditambah SEO Studio, Ruang riset, dan Evaluasi channel.

## Mulai

Gunakan Python 3.10 atau lebih baru, lalu jalankan dari direktori proyek:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Tanpa kunci API, SEO Studio, brief dasar, watchlist dan impor CSV tetap dapat dibuka. Riset data YouTube memerlukan kunci YouTube. Paket konten AI memerlukan Gemini.

Simpan kunci pada `.streamlit/secrets.toml` atau pengaturan Secrets hosting Anda:

```toml
YOUTUBE_API_KEY = "ISI_KUNCI_ANDA"
GEMINI_API_KEY = "ISI_KUNCI_ANDA"
GROQ_API_KEY = "ISI_KUNCI_ANDA"
```

`YOUTUBE_API_KEYS` juga menerima daftar atau string kunci dipisahkan koma seperti versi sebelumnya. Jangan memasukkan Secrets ke git. Pergantian kunci bukan pengganti persetujuan penambahan kuota dari penyedia.

## Pembaruan proyek lama

1. Cadangkan folder proyek dan Secrets.
2. Ganti `app.py`, `modules/`, `tests/`, `requirements.txt`, serta dokumentasi dengan isi paket ini. Pertahankan Secrets nyata dan pengaturan deployment Anda.
3. Pertahankan direktori `data/` dari versi ini ketika melakukan pembaruan berikutnya. Jangan menggantinya dengan data dari perangkat lain.
4. Jika database snapshot versi lama berada pada `niche_hunter_snapshots.db` di akar proyek, aplikasi menyalin database tersebut ke direktori data saat pertama dijalankan, apabila database tujuan belum ada.
5. Jalankan pengujian dan aplikasi secara lokal, kemudian perbarui deployment Anda.

Paket ini tidak mengubah deployment publik atau repositori eksternal secara otomatis.

## Alur fitur baru

### SEO Studio

Dari detail video atau kandidat Viral Intelligence, klik **Optimalkan ide ini**. Judul, deskripsi dan tag referensi akan masuk ke formulir. Kata kunci target dan ringkasan/transkrip diisi sendiri untuk memastikan audit sesuai konteks.

Klik **Audit dan siapkan brief**. Hasil menampilkan komponen rubrik internal dengan saran perbaikan. Rubrik memeriksa cakupan kata kunci pada judul, pembuka deskripsi, dan ringkasan/transkrip. Pemeriksaan bersifat leksikal, tidak mengukur seluruh makna atau maksud pencarian. Skor bukan skor resmi YouTube, probabilitas viral, atau prediksi posisi pencarian.

Tab Riset pendukung memakai hasil pencarian atau Viral Intelligence dari sesi berjalan dengan kata kunci yang sama. Frekuensi kata merupakan frekuensi pada sampel video, bukan volume pencarian resmi. Kandidat celah pembahasan berasal dari cakupan lima kategori maksud pembahasan pada judul/deskripsi sampel. Verifikasi isi video sebelum menyimpulkan celah pasar.

Brief dasar merupakan kerangka kerja berdasarkan masukan pengguna. Paket AI menghasilkan alternatif judul, deskripsi, keyword, tag pendukung, konsep thumbnail, hook dan outline. AI hanya dipanggil ketika tombol dipilih dan ringkasan/transkrip tersedia. Jawaban perlu ditinjau sebelum publikasi. Masukan formulir yang diaudit dikirim ke Gemini, bukan seluruh watchlist atau laporan CSV.

Chapter hanya dibuat dari baris timestamp yang ada pada transkrip, misalnya `00:00 Pembukaan`. Pemeriksaan dasar mensyaratkan minimal tiga bagian, awal 00:00, urutan naik, dan jarak minimal 10 detik. Durasi chapter terakhir perlu diperiksa terhadap durasi video. Aplikasi tidak menciptakan timestamp dari ringkasan.

### Ruang riset

Klik **Simpan watchlist** pada video untuk menyimpan referensi. Niche dan channel dapat ditambahkan secara manual. Catatan dan brief disimpan dalam SQLite, sehingga dapat dibuka kembali setelah sesi browser berakhir pada instalasi yang sama.

Riwayat menyimpan 30 riset terakhir dan maksimal 50 referensi per riset. Referensi dalam riwayat dapat ditambahkan ke watchlist. Data snapshot tersedia sebagai grafik apabila video memiliki setidaknya dua pengukuran dalam database. Snapshot bertambah ketika video dipindai melalui Viral Intelligence, bukan secara otomatis melalui pekerjaan terjadwal.

Unduh cadangan JSON dari tab Cadangan. Pemulihan menggabungkan watchlist, brief dan riwayat berdasarkan ID. Entri dengan ID yang sama diperbarui. Cadangan JSON tidak memuat database snapshot; untuk memindahkan seluruh histori snapshot, cadangkan direktori data saat aplikasi berhenti.

### Evaluasi channel sendiri

Ekspor CSV per video dari YouTube Studio, pilih periode yang konsisten, lalu unggah melalui menu **Studio > Evaluasi channel**. Petakan Video ID atau Judul, Views, dan kolom opsional Impresi, CTR (%) dan persentase rata-rata ditonton (%).

Format numerik: angka tanpa pemisah ribuan dan titik sebagai pemisah desimal. CTR menggunakan skala 0 sampai 100. Persentase rata-rata ditonton menerima nilai nonnegatif, termasuk lebih dari 100 bila demikian tercatat pada sumber. Nilai kosong dalam kolom numerik yang dipetakan perlu dibersihkan atau kolom tersebut dibiarkan tidak dipetakan. CSV maksimal 10 MB dan 10.000 baris.

Hasil berisi tabel per video, median, grafik CTR terhadap persentase ditonton, dan saran peninjauan relatif terhadap median sampel. Ini bukan diagnosis sebab-akibat. Baris Total dikeluarkan. Median CTR per video bukan CTR agregat channel. Laporan tinggal dalam sesi aplikasi dan tidak dikirim ke AI atau disimpan secara otomatis ke database.

Koneksi OAuth belum ditambahkan. Impor CSV merupakan jalur evaluasi channel sendiri pada versi ini.

## Indikator yang diperjelas

- Skor lama pada hasil pencarian sekarang merupakan **kelengkapan metadata**, menggunakan aspek yang dapat diamati tanpa kata kunci target/transkrip. Jumlah tag tidak menambah nilai. Audit relevansi penuh tersedia di SEO Studio.
- VPH pencarian adalah rata-rata views sejak publikasi. Velocity Viral Intelligence memakai selisih snapshot jika interval minimal lima menit tersedia. Scan terlalu dekat kembali ke rata-rata sejak publikasi dan tidak dianggap bukti akselerasi.
- Penyimpanan snapshot memiliki jarak minimal lima menit per video. Akselerasi tidak menyumbang poin breakout ketika kurang dari dua snapshot historis yang dapat digunakan.
- Detail breakout menampilkan komponen, bobot, kontribusi dan kecukupan snapshot/baseline. Bobot tetap heuristik dan belum dikalibrasi lewat studi prediksi.
- Analisis channel menyediakan sampel 5, 15, 30 atau 50 video serta median. Video dengan usia berbeda belum dinormalisasi, sehingga perbandingan perlu mempertimbangkan usia dan format. Baseline Viral Intelligence juga menggunakan VPH rata-rata sejak publikasi; perbandingan dengan velocity interval belum menggunakan jendela waktu yang setara.
- Pola jam publikasi menunjukkan kebiasaan channel, bukan bukti waktu publikasi optimal.
- Pendapatan menggunakan simulasi dengan asumsi RPM minimum/maksimum yang diisi sendiri. Data publik tidak mengungkap pendapatan channel.

## Data pribadi dan hosting

Aplikasi ini dirancang untuk satu pengguna pribadi. SQLite tersimpan dalam `data/` secara default. Gunakan variabel lingkungan `NICHE_HUNTER_DATA_DIR` untuk menunjuk direktori/volume persisten. Folder dibuat otomatis dan tidak diikutkan dalam git atau ZIP ini.

Semua sesi yang memakai instalasi dan direktori data yang sama berbagi watchlist, riwayat dan brief. Gunakan akses hosting privat. Jangan memakai versi ini sebagai layanan multiuser publik tanpa autentikasi serta pemisahan database pengguna. Disk sementara pada hosting dapat hilang setelah redeployment. Gunakan cadangan JSON dan volume persisten untuk menjaga data.

## Pengujian

```bash
python -m unittest tests.test_ui tests.test_growth -v
```

Pengujian menggunakan data simulasi dan tidak memanggil API nyata. Cakupan meliputi tujuh mode awal, state hasil pencarian, AI lama, pagination, perbandingan, SEO Studio, relevansi, chapter, penyimpanan lintas koneksi, pemulihan atomik, batas riwayat, pemetaan CSV, navigasi ke SEO, serta startup tanpa kredensial.

YouTube/Gemini/Groq belum diuji end-to-end dengan kredensial nyata dalam lingkungan pengembangan ini. Layout diperiksa melalui struktur widget AppTest, bukan tangkapan layar browser. Dokumen `ANALISIS_UI_UX.md` merupakan audit versi sebelumnya, bukan laporan validasi fitur baru.

## Rujukan desain audit

- [Cara kerja YouTube Search](https://support.google.com/youtube/answer/16090438?hl=en)
- [Peran tag video](https://support.google.com/youtube/answer/146402?hl=en)
- [Otorisasi laporan channel](https://developers.google.com/youtube/analytics/channel_reports)
