# Sistem Peminjaman & Pengembalian Buku Perpustakaan

Studi kasus **Perpustakaan Politeknik Negeri Semarang (Polines)** — Kelompok 7.

Aplikasi dibangun dengan **Streamlit** (antarmuka) dan **SQLite** (basis data lokal).
Tidak ada fitur login; aplikasi dijalankan langsung oleh petugas perpustakaan.

## Menjalankan aplikasi

Pertama kali (membuat virtual environment dan memasang dependensi):

```powershell
py -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

Menjalankan aplikasi:

```powershell
.\venv\Scripts\python.exe -m streamlit run app.py
```

Aplikasi terbuka pada `http://localhost:8501`.

Cara paling singkat: klik dua kali `jalankan.bat` (venv dan dependensi dibuat otomatis
jika belum ada).

## Fitur

- **Ringkasan** — statistik koleksi, peminjaman aktif, keterlambatan, dan denda.
- **Koleksi Buku** — tambah, edit, hapus, pencarian, filter jenis, dan pengelolaan stok.
- **Anggota** — pendaftaran anggota, NIM unik, status aktif/nonaktif.
- **Peminjaman** — validasi status anggota, stok, maksimal 2 buku, izin khusus Kepala
  Perpustakaan, pencatatan kondisi awal buku, dan jatuh tempo otomatis 7 hari.
- **Pengembalian** — perhitungan denda keterlambatan otomatis (Rp1.000/buku/hari),
  denda kerusakan (Rp10.000 / Rp50.000), dan kehilangan (Rp100.000).
- **Laporan & Denda** — riwayat transaksi, rekap denda per anggota, unduh CSV.

## Aturan yang diterapkan

| Aturan | Nilai |
|---|---|
| Masa peminjaman | 7 hari |
| Maksimal peminjaman | 2 buku per anggota |
| Denda keterlambatan | Rp1.000 per buku per hari |
| Denda rusak ringan | Rp10.000 |
| Denda rusak berat | Rp50.000 |
| Denda buku hilang | Rp100.000 |
| Peminjam | Harus mahasiswa aktif dengan NIM |

## Struktur proyek

```
app.py            # Antarmuka Streamlit
database.py       # Skema, data contoh, dan logika SQLite
requirements.txt  # Dependensi
perpustakaan.db   # Dibuat otomatis saat aplikasi pertama dijalankan
```

## Anggota Kelompok 7

1. Chandra Hernaldi (09)
2. Jauzaa Lubnaa (15)
3. Marahita Aldila S (18)
4. Ranum Darwari (23)
5. Ulung Galih (28)
