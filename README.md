# Niche Hunter, tampilan sederhana

Revisi antarmuka untuk penggunaan pribadi. Tujuh mode aplikasi asli tetap tersedia, dikelompokkan menjadi Video, Channel, dan Artis. Mesin pengambilan data dan 45 fungsi kalkulasi/layanan asli dipertahankan. Detail audit terdapat pada ANALISIS_UI_UX.md.

## Menjalankan

Gunakan Python 3.10 atau lebih baru. Pemeriksaan revisi dilakukan dengan Python 3.12.14 dan Streamlit 1.65.0.

```bash
pip install -r requirements.txt
streamlit run app.py
```

Gunakan konfigurasi Secrets milik aplikasi Anda, dengan nama yang tetap sama:

- `YOUTUBE_API_KEYS`, string berisi kunci yang dipisahkan koma, atau daftar kunci.
- `YOUTUBE_API_KEY`, alternatif untuk satu kunci.
- `GEMINI_API_KEY`, untuk ide konten dan analisis breakout.
- `GROQ_API_KEY`, untuk Channel DNA.

Pada komputer sendiri, gunakan `.streamlit/secrets.toml`. Pada Streamlit Community Cloud, pertahankan Secrets yang sudah ada. Tidak ada kunci API nyata di dalam paket ini.

## Menerapkan ke proyek yang sudah ada

1. Buat commit atau cadangan proyek saat ini.
2. Ganti `app.py` dan `requirements.txt` dari paket ini.
3. Tambahkan `modules/simple_ui.py` dan `modules/simple_ui.css`.
4. Pertahankan `modules/ai_engine.py` serta `modules/opportunity_engine.py`. Salinan di paket ini identik dengan sumber unggahan.
5. Tambahkan atau gabungkan pengaturan warna `.streamlit/config.toml` jika menginginkan aksen hijau dan latar terang. Jangan menimpa pengaturan proyek lain yang Anda butuhkan.
6. Jalankan dahulu, kemudian perbarui deployment melalui repositori yang terhubung apabila hasilnya sudah sesuai.

Aplikasi pada tautan publik belum diubah oleh revisi ini. Folder `tests` hanya diperlukan untuk pengujian, bukan untuk menjalankan aplikasi.

## Alur penggunaan

- Video > Pencarian: kata kunci, wilayah, urutan, lalu Cari video. Filter lainnya tersedia di Filter lanjutan.
- Video > Trending: wilayah dan kategori, kemudian Lihat trending.
- Video > Viral Intelligence: niche, wilayah, rentang publikasi. Hasil dipisah menjadi Kandidat, Detail dan radar, serta Peluang konten.
- Channel > Direktori: pencarian channel beserta seluruh filter asli.
- Channel > Analisis: statistik, lima video sampel terbaru, pola publikasi, dan tag.
- Channel > Perbandingan: hingga empat channel dalam tabel yang sama.
- Artis: dua nama utama. Tiga nama tambahan dan pengaturan analisis bisa dibuka sesuai kebutuhan.

Kartu video menampilkan data pokok. Buka Detail, SEO, dan tindakan untuk seluruh indikator, ringkasan, analisis channel, perbandingan, Channel DNA, serta unduhan thumbnail. Pagination menampilkan enam kartu per halaman. Semua hasil tetap tersedia pada halaman lain, tampilan tabel, dan CSV.

Saran kata kunci tetap tersedia. Google Trends baru diambil ketika tombol Muat tren kata kunci dipilih. Fungsi AI dijalankan lewat tombol masing-masing. Detail yang tertutup tidak otomatis menunda eksekusi kode Streamlit, sehingga panggilan jaringan tetap diberi pemicu tombol secara eksplisit.

Hasil pencarian dan trending memiliki penyimpanan sesi yang terpisah. Hasil AI terikat pada referensinya dan tetap tampil setelah interaksi lain. Data analisis channel dipakai ulang selama maksimal 15 menit dalam sesi, dengan tombol Perbarui data. Penyimpanan sesi tidak bertahan setelah sesi browser berakhir; unduh CSV jika ingin menyimpan hasil riset.

## Pengujian

```bash
python -m unittest tests.test_ui -v
```

Pengujian memakai data simulasi dan tidak menggunakan kuota YouTube atau AI. Sepuluh skenario mencakup navigasi tujuh mode, filter, autocomplete, pagination, pemisahan hasil, persistensi AI, cache analisis channel, kapasitas perbandingan, Viral Intelligence, dan perbandingan artis.

Pencarian aplikasi asli juga diperiksa melalui browser dan berhasil. Entry point revisi diperiksa dengan AppTest dan kunci dummy tanpa memanggil API. Akses YouTube/Gemini/Groq pada revisi belum diuji end-to-end dengan kredensial nyata. Pemeriksaan visual aplikasi revisi melalui cloud browser belum dapat dilakukan karena browser tersebut tidak dapat menjangkau server lokal. CSS responsif disertakan, tetapi belum merupakan hasil uji perangkat seluler.
