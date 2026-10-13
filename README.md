# Niche Hunter 2.0 — riset, optimasi dan produksi konten

Versi 14 Oktober 2026 (WIB). Aplikasi riset YouTube pribadi berbasis Streamlit dengan 16 mode. Upgrade menambahkan Keyword Lab, Radar kompetitor, Rank Tracker, Kalender konten, Eksperimen CTR dan Audit massal.

Mulai dari [UPGRADE_GUIDE.md](UPGRADE_GUIDE.md). Perbandingan dengan vidIQ/TubeBuddy dan temuan audit ada di [COMPARISON_REPORT.md](COMPARISON_REPORT.md). Hasil pengujian ada di [VALIDATION.md](VALIDATION.md).

## Mulai

Gunakan Python 3.10 atau lebih baru, lalu jalankan dari direktori proyek:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Tanpa kunci API, SEO Studio, brief dasar, watchlist dan impor CSV tetap dapat dibuka. Riset data YouTube memerlukan kunci YouTube. Paket konten AI memerlukan Gemini.

Simpan kunci pada `.streamlit/secrets.toml`, pengaturan Secrets hosting, atau environment Anda:

```toml
YOUTUBE_API_KEY = "ISI_KUNCI_ANDA"
GEMINI_API_KEY = "ISI_KUNCI_ANDA"
GROQ_API_KEY = "ISI_KUNCI_ANDA"
```

`YOUTUBE_API_KEYS` juga menerima daftar atau string kunci dipisahkan koma seperti versi sebelumnya. Jangan memasukkan Secrets ke git. Pilih kunci aktif di Pengaturan dan bantuan bila perlu. Aplikasi tidak merotasi kunci otomatis saat kuota habis; pergantian kunci bukan pengganti penambahan kuota dari penyedia.

## Pembaruan proyek lama

1. Cadangkan folder proyek dan Secrets.
2. Ganti `app.py`, `modules/`, `tests/`, `requirements.txt`, serta dokumentasi dengan isi paket ini. Pertahankan Secrets nyata dan pengaturan deployment Anda.
3. Pertahankan direktori `data/` dari versi ini ketika melakukan pembaruan berikutnya. Jangan menggantinya dengan data dari perangkat lain.
4. Jika database snapshot versi lama berada pada `niche_hunter_snapshots.db` di akar proyek, aplikasi menyalin database tersebut ke direktori data saat pertama dijalankan, apabila database tujuan belum ada.
5. Jalankan pengujian dan aplikasi secara lokal, kemudian perbarui deployment Anda.

Paket ini tidak mengubah deployment publik atau repositori eksternal secara otomatis.

## Pembaruan kemudahan penggunaan

Untuk pengguna paket sebelumnya, perubahan aplikasi ada pada `modules/growth_ui.py` dan `modules/growth_engine.py`. Ganti kedua file tersebut atau folder `modules/`, kemudian restart aplikasi. Sebelum memperbarui hosting, unduh cadangan JSON dari Ruang riset > Cadangan. Pertahankan folder data serta Secrets.

Tombol Hapus sekarang terlihat di samping setiap referensi watchlist. Penghapusan dilakukan sebelum daftar dirender ulang dan menampilkan pesan keberhasilan atau kegagalan. Menghapus watchlist tidak menghapus rekaman sumber pada riwayat riset.

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

Unduh cadangan JSON dari tab Cadangan. Pemulihan schema 2 menggabungkan watchlist, brief, riwayat, riset keyword, rank tracking, kalender dan eksperimen berdasarkan ID. Schema 1 lama tetap dapat dipulihkan. Entri dengan ID yang sama diperbarui. Cadangan JSON tidak memuat database snapshot; untuk memindahkan seluruh histori snapshot, cadangkan direktori data saat aplikasi berhenti.

### Evaluasi channel sendiri

Untuk mencoba tanpa data channel, buka **Studio > Evaluasi channel**, pilih **Coba contoh simulasi**, kemudian klik **Analisis laporan**. Data contoh diberi label simulasi dan dapat diunduh sebagai contoh format.

Untuk memakai data sendiri:

1. Buka YouTube Studio di komputer. Pilih Analytics > Mode lanjutan atau Lihat lainnya.
2. Pilih rentang tanggal, misalnya 28 hari terakhir, dan pengelompokan Konten/video. Setiap baris harus mewakili satu video.
3. Sertakan Penayangan (Views). Tambahkan Impresi/Tayangan, CTR, serta persentase rata-rata ditonton bila tersedia.
4. Pilih Ekspor tampilan saat ini > CSV. Jika unduhan berupa ZIP, ekstrak lalu pilih CSV tabel per video, bukan laporan harian.
5. Buka Studio > Evaluasi channel > Unggah CSV saya pada aplikasi. Periksa pratinjau, cocokkan kolom, pilih format angka, lalu klik Analisis laporan.

Kolom wajib adalah Video ID atau Judul dan Views. Kolom lain opsional. Grafik serta saran peninjauan memerlukan CTR dan persentase rata-rata ditonton. Total views yang ditampilkan merupakan total baris video dalam CSV, bukan otomatis total channel.

Format numerik dipilih sesuai CSV: titik desimal (contoh 1,234.5) atau koma desimal (contoh 1.234,5). Pemisah ribuan opsional. Periksa pratinjau sebelum memilih format; aplikasi tidak menebak arti angka yang ambigu. CTR menggunakan skala 0 sampai 100. Persentase rata-rata ditonton menerima nilai nonnegatif, termasuk lebih dari 100 bila demikian tercatat pada sumber. Nilai kosong dalam kolom numerik yang dipetakan perlu dibersihkan atau kolom tersebut dibiarkan tidak dipetakan. CSV maksimal 10 MB dan 10.000 baris.

Hasil berisi tabel per video, median, grafik CTR terhadap persentase ditonton, dan saran peninjauan relatif terhadap median sampel. Ini bukan diagnosis sebab-akibat. Baris Total dikeluarkan. Median CTR per video bukan CTR agregat channel. Laporan tinggal dalam sesi aplikasi dan tidak dikirim ke AI atau disimpan secara otomatis ke database.

Koneksi OAuth belum ditambahkan. Pengguna login ke YouTube Studio untuk mengekspor CSV; aplikasi ini tidak meminta login atau password Google.

Jika integrasi otomatis dibangun, aplikasi akan membuka halaman Google melalui OAuth. Pemilik channel memilih akun, memberikan izin baca analitik, lalu kembali ke aplikasi. Aplikasi menggunakan token izin, bukan password pengguna. Pengembang perlu mengaktifkan API, membuat kredensial OAuth dan mengatur alamat callback. API key untuk riset data publik saja tidak memberikan akses analitik pribadi. Metrik yang tersedia melalui API perlu diperiksa sebelum menjanjikan kesetaraan dengan seluruh tampilan Studio.

## Indikator yang diperjelas

- Skor lama pada hasil pencarian sekarang merupakan **kelengkapan metadata**, menggunakan aspek yang dapat diamati tanpa kata kunci target/transkrip. Jumlah tag tidak menambah nilai. Audit relevansi penuh tersedia di SEO Studio.
- VPH pencarian adalah rata-rata views sejak publikasi. Velocity Viral Intelligence memakai selisih snapshot jika interval minimal lima menit tersedia. Scan terlalu dekat kembali ke rata-rata sejak publikasi dan tidak dianggap bukti akselerasi.
- Penyimpanan snapshot memiliki jarak minimal lima menit per video. Akselerasi tidak menyumbang poin breakout ketika kurang dari dua snapshot historis yang dapat digunakan.
- Detail breakout menampilkan komponen, bobot, kontribusi dan kecukupan snapshot/baseline. Bobot tetap heuristik dan belum dikalibrasi lewat studi prediksi.
- Analisis channel menyediakan sampel 5, 15, 30 atau 50 video serta median. Video dengan usia berbeda belum dinormalisasi, sehingga perbandingan perlu mempertimbangkan usia dan format. Baseline Viral Intelligence sekarang menggunakan median VPH sejak publikasi pada video sebanding, tidak dibagi dengan velocity snapshot. Lihat metodologi baru di panduan upgrade.
- Pola jam publikasi menunjukkan kebiasaan channel, bukan bukti waktu publikasi optimal.
- Pendapatan menggunakan simulasi dengan asumsi RPM minimum/maksimum yang diisi sendiri. Data publik tidak mengungkap pendapatan channel.

## Data pribadi dan hosting

Aplikasi ini dirancang untuk satu pengguna pribadi. SQLite tersimpan dalam `data/` secara default. Gunakan variabel lingkungan `NICHE_HUNTER_DATA_DIR` untuk menunjuk direktori/volume persisten. Folder dibuat otomatis dan tidak diikutkan dalam git atau ZIP ini.

Semua sesi yang memakai instalasi dan direktori data yang sama berbagi watchlist, riwayat dan brief. Gunakan akses hosting privat. Jangan memakai versi ini sebagai layanan multiuser publik tanpa autentikasi serta pemisahan database pengguna. Disk sementara pada hosting dapat hilang setelah redeployment. Gunakan cadangan JSON dan volume persisten untuk menjaga data.

## Pengujian

```bash
python -m unittest discover -s tests -v
```

Pengujian menggunakan data simulasi dan tidak memanggil API nyata. Cakupan meliputi tujuh mode awal, state hasil pencarian, AI lama, pagination, perbandingan, SEO Studio, relevansi, chapter, penyimpanan lintas koneksi, pemulihan atomik, batas riwayat, pemetaan CSV, navigasi ke SEO, serta startup tanpa kredensial.

YouTube/Gemini/Groq belum diuji end-to-end dengan kredensial nyata dalam lingkungan pengembangan ini. Interaksi UI diperiksa melalui Streamlit AppTest. Pemeriksaan browser visual belum selesai; lihat VALIDATION.md. Dokumen `ANALISIS_UI_UX.md` merupakan audit versi sebelumnya, bukan laporan validasi fitur baru.

## Rujukan desain audit

- [Cara kerja YouTube Search](https://support.google.com/youtube/answer/16090438?hl=en)
- [Peran tag video](https://support.google.com/youtube/answer/146402?hl=en)
- [Ekspor laporan dari YouTube Studio](https://support.google.com/youtube/answer/9717005?hl=id)
- [Alur OAuth Google](https://developers.google.com/youtube/reporting/guides/authorization/server-side-web-apps)
- [Otorisasi laporan channel](https://developers.google.com/youtube/analytics/channel_reports)
