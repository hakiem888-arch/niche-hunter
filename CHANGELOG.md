# Pembaruan watchlist dan evaluasi, 13 Oktober 2026

- Tombol hapus watchlist terlihat langsung pada daftar. Penghapusan memakai callback sebelum perenderan ulang dan menyampaikan hasil operasi.
- Pesan kegagalan database terlihat tanpa menghilangkan referensi dari tampilan.
- Enam pengujian baru mencakup penghapusan video/niche lintas sesi, kegagalan tulis database, mode contoh, angka Indonesia, nilai tidak valid, dan kolom minimum.
- Evaluasi channel memiliki panduan ekspor Studio, mode contoh berlabel simulasi, pratinjau CSV dan pilihan format angka.
- Baris Total pada kolom ID maupun Judul dikeluarkan sebelum validasi angka.
- Pesan kesalahan menjelaskan kolom yang perlu diperiksa; pilihan pemetaan dipisahkan untuk setiap file.
- Koneksi OAuth belum diimplementasikan. Konsep dan persiapannya dijelaskan dalam README.

# Perubahan 13 Oktober 2026

## Ditambahkan

- SEO Studio terhubung dengan detail video dan Viral Intelligence.
- Rubrik relevansi internal dengan penjelasan per komponen.
- Riset kata dan kandidat celah pembahasan berdasarkan sampel sesi.
- Brief dasar, chapter dari timestamp sumber, dan paket konten AI sesuai masukan.
- Watchlist video/niche/channel, catatan, brief dan riwayat riset persisten.
- Ekspor dan pemulihan cadangan JSON dengan validasi sebelum perubahan database.
- Impor CSV YouTube Studio dengan pemetaan kolom serta evaluasi CTR/retensi.
- Simulasi pendapatan berdasarkan asumsi RPM pengguna.
- Pilihan jumlah sampel analisis channel dan median.
- Komponen skor breakout dan status kecukupan bukti.

## Diperbaiki

- Jumlah tag tidak lagi menentukan skor kelengkapan metadata.
- Data tanpa snapshot cukup tidak memberikan poin akselerasi.
- Snapshot berjarak kurang dari lima menit tidak disimpan sebagai pengukuran baru.
- Fungsi lokal dapat digunakan tanpa kunci YouTube.
- Data riset tidak terbatas pada sesi browser jika direktori data dipertahankan.

## Batas versi ini

- OAuth dan pemantauan terjadwal belum diterapkan.
- Skor adalah heuristik yang belum dikalibrasi terhadap peluang sukses.
- Data persisten ditujukan untuk satu pengguna pada instalasi privat.
- Integrasi API nyata perlu diperiksa dengan Secrets pengguna setelah pemasangan.
