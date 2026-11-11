"""
Logika database SQLite untuk Sistem Peminjaman & Pengembalian Buku
Perpustakaan Politeknik Negeri Semarang (studi kasus Kelompok 7).
"""

import sqlite3
from contextlib import closing
from datetime import date, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "perpustakaan.db"

# ---------------------------------------------------------------------------
# Aturan perpustakaan (sesuai studi kasus)
# ---------------------------------------------------------------------------
MASA_PINJAM = 7                 # hari
MAKS_PINJAM = 2                 # buku dalam satu waktu
DENDA_PER_HARI = 1_000          # rupiah / buku / hari
DENDA_RUSAK_RINGAN = 10_000
DENDA_RUSAK_BERAT = 50_000
DENDA_HILANG = 100_000

KONDISI_BUKU = ["Baik", "Rusak Ringan", "Rusak Berat", "Hilang"]
BOBOT_KONDISI = {"Baik": 0, "Rusak Ringan": 1, "Rusak Berat": 2, "Hilang": 3}

JENIS_BUKU = [
    "Buku Teks",
    "Modul Praktikum",
    "Laporan Tugas Akhir",
    "Jurnal Ilmiah",
    "Referensi Umum",
]

PROGRAM_STUDI = [
    "Teknik Informatika",
    "Teknik Elektro",
    "Teknik Mesin",
    "Teknik Sipil",
    "Akuntansi",
    "Administrasi Bisnis",
    "Lainnya",
]

SCHEMA = """
CREATE TABLE IF NOT EXISTS buku (
    id_buku        TEXT PRIMARY KEY,
    judul_buku     TEXT NOT NULL,
    pengarang      TEXT,
    penerbit       TEXT,
    tahun_terbit   INTEGER,
    jenis_buku     TEXT,
    stok_total     INTEGER NOT NULL DEFAULT 1,
    stok_tersedia  INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS anggota (
    id_anggota     TEXT PRIMARY KEY,
    nim            TEXT UNIQUE NOT NULL,
    nama_lengkap   TEXT NOT NULL,
    nomor_telepon  TEXT,
    email          TEXT,
    program_studi  TEXT,
    status_aktif   INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS peminjaman (
    id_peminjaman             INTEGER PRIMARY KEY AUTOINCREMENT,
    id_anggota                TEXT NOT NULL,
    id_buku                   TEXT NOT NULL,
    tanggal_pinjam            TEXT NOT NULL,
    tanggal_wajib_kembali     TEXT NOT NULL,
    tanggal_realisasi_kembali TEXT,
    kondisi_pinjam            TEXT NOT NULL DEFAULT 'Baik',
    kondisi_kembali           TEXT,
    denda_keterlambatan       INTEGER NOT NULL DEFAULT 0,
    denda_kerusakan           INTEGER NOT NULL DEFAULT 0,
    denda_akumulasi           INTEGER NOT NULL DEFAULT 0,
    status                    TEXT NOT NULL DEFAULT 'Dipinjam',
    izin_khusus               INTEGER NOT NULL DEFAULT 0,
    catatan                   TEXT,
    FOREIGN KEY (id_anggota) REFERENCES anggota (id_anggota),
    FOREIGN KEY (id_buku) REFERENCES buku (id_buku)
);

CREATE INDEX IF NOT EXISTS idx_peminjaman_anggota ON peminjaman (id_anggota);
CREATE INDEX IF NOT EXISTS idx_peminjaman_buku ON peminjaman (id_buku);
CREATE INDEX IF NOT EXISTS idx_peminjaman_status ON peminjaman (status);
"""


# ---------------------------------------------------------------------------
# Koneksi & inisialisasi
# ---------------------------------------------------------------------------
def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    with closing(get_conn()) as conn, conn:
        conn.executescript(SCHEMA)
    _seed_if_empty()
    sync_statuses()


def _seed_if_empty() -> None:
    with closing(get_conn()) as conn, conn:
        jumlah = conn.execute("SELECT COUNT(*) AS n FROM buku").fetchone()["n"]
        if jumlah:
            return

        buku = [
            ("B001", "Algoritma dan Pemrograman", "Rinaldi Munir", "Informatika", 2019, "Buku Teks", 4),
            ("B002", "Basis Data", "Fathansyah", "Informatika", 2018, "Buku Teks", 5),
            ("B003", "Pemrograman Python untuk Pemula", "Budi Raharjo", "Andi Publisher", 2021, "Modul Praktikum", 3),
            ("B004", "Jaringan Komputer", "Andrew S. Tanenbaum", "Pearson", 2014, "Buku Teks", 3),
            ("B005", "Matematika Diskrit", "Kenneth H. Rosen", "McGraw-Hill", 2018, "Buku Teks", 4),
            ("B006", "Sistem Operasi", "Abraham Silberschatz", "Wiley", 2017, "Buku Teks", 3),
            ("B007", "Dasar-Dasar Akuntansi", "Mardiasmo", "Andi Publisher", 2016, "Referensi Umum", 2),
            ("B008", "Perancangan Teknik Mesin", "Joseph E. Shigley", "Erlangga", 2015, "Buku Teks", 2),
            ("B009", "Metodologi Penelitian", "Sugiyono", "Alfabeta", 2019, "Referensi Umum", 4),
            ("B010", "Bahasa Indonesia Akademik", "Gorys Keraf", "Gramedia", 2017, "Referensi Umum", 3),
        ]
        conn.executemany(
            """INSERT INTO buku
               (id_buku, judul_buku, pengarang, penerbit, tahun_terbit, jenis_buku, stok_total, stok_tersedia)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            [(b[0], b[1], b[2], b[3], b[4], b[5], b[6], b[6]) for b in buku],
        )

        anggota = [
            ("A001", "20240009", "Chandra Hernaldi", "0812-3456-0009", "chandra@student.polines.ac.id", "Teknik Informatika"),
            ("A002", "20240015", "Jauzaa Lubnaa", "0812-3456-0015", "jauzaa@student.polines.ac.id", "Teknik Informatika"),
            ("A003", "20240018", "Marahita Aldila S", "0812-3456-0018", "marahita@student.polines.ac.id", "Teknik Elektro"),
            ("A004", "20240023", "Ranum Darwari", "0812-3456-0023", "ranum@student.polines.ac.id", "Akuntansi"),
            ("A005", "20240028", "Ulung Galih", "0812-3456-0028", "ulung@student.polines.ac.id", "Teknik Mesin"),
            ("A006", "20230041", "Dimas Prakoso", "0812-3456-0041", "dimas@student.polines.ac.id", "Teknik Sipil"),
            ("A007", "20240052", "Salsabila Putri", "0812-3456-0052", "salsabila@student.polines.ac.id", "Administrasi Bisnis"),
        ]
        conn.executemany(
            """INSERT INTO anggota
               (id_anggota, nim, nama_lengkap, nomor_telepon, email, program_studi, status_aktif)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            [(a[0], a[1], a[2], a[3], a[4], a[5], 0 if a[0] == "A006" else 1) for a in anggota],
        )

        today = date.today()

        def sample(id_anggota, id_buku, pinjam_selisih, kembali_selisih, kondisi_kembali, status):
            tgl_pinjam = today - timedelta(days=pinjam_selisih)
            tgl_wajib = tgl_pinjam + timedelta(days=MASA_PINJAM)
            tgl_kembali = None if kembali_selisih is None else today - timedelta(days=kembali_selisih)
            denda_late = 0
            if tgl_kembali:
                denda_late = max(0, (tgl_kembali - tgl_wajib).days) * DENDA_PER_HARI
            denda_rusak = 0
            if kondisi_kembali in ("Rusak Ringan", "Rusak Berat", "Hilang"):
                denda_rusak = {
                    "Rusak Ringan": DENDA_RUSAK_RINGAN,
                    "Rusak Berat": DENDA_RUSAK_BERAT,
                    "Hilang": DENDA_HILANG,
                }[kondisi_kembali]
            conn.execute(
                """INSERT INTO peminjaman
                   (id_anggota, id_buku, tanggal_pinjam, tanggal_wajib_kembali,
                    tanggal_realisasi_kembali, kondisi_pinjam, kondisi_kembali,
                    denda_keterlambatan, denda_kerusakan, denda_akumulasi, status, catatan)
                   VALUES (?, ?, ?, ?, ?, 'Baik', ?, ?, ?, ?, ?, ?)""",
                (
                    id_anggota, id_buku, tgl_pinjam.isoformat(), tgl_wajib.isoformat(),
                    tgl_kembali.isoformat() if tgl_kembali else None,
                    kondisi_kembali,
                    denda_late, denda_rusak, denda_late + denda_rusak, status,
                    "Data contoh sistem",
                ),
            )
            # Hanya peminjaman yang masih berjalan yang mengurangi stok tersedia.
            if status in ("Dipinjam", "Terlambat"):
                conn.execute(
                    "UPDATE buku SET stok_tersedia = stok_tersedia - 1 WHERE id_buku = ?",
                    (id_buku,),
                )

        sample("A001", "B001", 3, None, None, "Dipinjam")
        sample("A001", "B003", 10, None, None, "Terlambat")
        sample("A002", "B002", 15, 5, "Baik", "Kembali")
        sample("A003", "B004", 2, None, None, "Dipinjam")
        sample("A004", "B005", 20, 13, "Rusak Ringan", "Kembali")


def sync_statuses() -> None:
    """Selaraskan status keterlambatan dengan tanggal hari ini."""
    today = date.today().isoformat()
    with closing(get_conn()) as conn, conn:
        conn.execute(
            """UPDATE peminjaman SET status = 'Terlambat'
               WHERE status = 'Dipinjam' AND tanggal_wajib_kembali < ?""",
            (today,),
        )
        conn.execute(
            """UPDATE peminjaman SET status = 'Dipinjam'
               WHERE status = 'Terlambat' AND tanggal_wajib_kembali >= ?""",
            (today,),
        )


# ---------------------------------------------------------------------------
# Utilitas
# ---------------------------------------------------------------------------
def _rows(sql: str, params: tuple = ()) -> list[dict]:
    with closing(get_conn()) as conn:
        return [dict(r) for r in conn.execute(sql, params).fetchall()]


def _next_id(prefix: str, table: str, column: str) -> str:
    rows = _rows(f"SELECT {column} AS kode FROM {table}")
    angka = []
    for r in rows:
        kode = str(r["kode"])
        if kode.startswith(prefix) and kode[len(prefix):].isdigit():
            angka.append(int(kode[len(prefix):]))
    return f"{prefix}{max(angka, default=0) + 1:03d}"


# ---------------------------------------------------------------------------
# Buku
# ---------------------------------------------------------------------------
def list_buku(cari: str = "", jenis: str = "Semua") -> list[dict]:
    sql = "SELECT * FROM buku WHERE 1=1"
    params: list = []
    if cari.strip():
        sql += " AND (judul_buku LIKE ? OR pengarang LIKE ? OR penerbit LIKE ? OR id_buku LIKE ?)"
        pola = f"%{cari.strip()}%"
        params += [pola, pola, pola, pola]
    if jenis and jenis != "Semua":
        sql += " AND jenis_buku = ?"
        params.append(jenis)
    sql += " ORDER BY id_buku"
    return _rows(sql, tuple(params))


def get_buku(id_buku: str) -> dict | None:
    data = _rows("SELECT * FROM buku WHERE id_buku = ?", (id_buku,))
    return data[0] if data else None


def add_buku(judul: str, pengarang: str, penerbit: str, tahun: int, jenis: str, stok: int) -> str:
    judul = judul.strip()
    if not judul:
        raise ValueError("Judul buku wajib diisi.")
    if stok < 1:
        raise ValueError("Jumlah eksemplar minimal 1.")
    with closing(get_conn()) as conn, conn:
        new_id = _next_id("B", "buku", "id_buku")
        conn.execute(
            """INSERT INTO buku
               (id_buku, judul_buku, pengarang, penerbit, tahun_terbit, jenis_buku, stok_total, stok_tersedia)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (new_id, judul, pengarang.strip(), penerbit.strip(), tahun, jenis, stok, stok),
        )
        return new_id


def update_buku(id_buku: str, judul: str, pengarang: str, penerbit: str,
                tahun: int, jenis: str, stok_total: int) -> None:
    judul = judul.strip()
    if not judul:
        raise ValueError("Judul buku wajib diisi.")
    with closing(get_conn()) as conn, conn:
        row = conn.execute("SELECT * FROM buku WHERE id_buku = ?", (id_buku,)).fetchone()
        if row is None:
            raise ValueError("Buku tidak ditemukan.")
        dipinjam = row["stok_total"] - row["stok_tersedia"]
        if stok_total < dipinjam:
            raise ValueError(
                f"Stok total tidak boleh kurang dari {dipinjam} eksemplar yang sedang dipinjam."
            )
        stok_tersedia = stok_total - dipinjam
        conn.execute(
            """UPDATE buku SET judul_buku = ?, pengarang = ?, penerbit = ?,
               tahun_terbit = ?, jenis_buku = ?, stok_total = ?, stok_tersedia = ?
               WHERE id_buku = ?""",
            (judul, pengarang.strip(), penerbit.strip(), tahun, jenis,
             stok_total, stok_tersedia, id_buku),
        )


def delete_buku(id_buku: str) -> None:
    with closing(get_conn()) as conn, conn:
        dipakai = conn.execute(
            "SELECT COUNT(*) AS n FROM peminjaman WHERE id_buku = ?", (id_buku,)
        ).fetchone()["n"]
        if dipakai:
            raise ValueError("Buku tidak dapat dihapus karena sudah memiliki riwayat peminjaman.")
        conn.execute("DELETE FROM buku WHERE id_buku = ?", (id_buku,))


# ---------------------------------------------------------------------------
# Anggota
# ---------------------------------------------------------------------------
def list_anggota(cari: str = "", hanya_aktif: bool = False) -> list[dict]:
    sql = "SELECT * FROM anggota WHERE 1=1"
    params: list = []
    if cari.strip():
        sql += " AND (nama_lengkap LIKE ? OR nim LIKE ? OR id_anggota LIKE ?)"
        pola = f"%{cari.strip()}%"
        params += [pola, pola, pola]
    if hanya_aktif:
        sql += " AND status_aktif = 1"
    sql += " ORDER BY id_anggota"
    return _rows(sql, tuple(params))


def get_anggota(id_anggota: str) -> dict | None:
    data = _rows("SELECT * FROM anggota WHERE id_anggota = ?", (id_anggota,))
    return data[0] if data else None


def add_anggota(nim: str, nama: str, telepon: str, email: str, prodi: str, aktif: bool) -> str:
    nim = nim.strip()
    nama = nama.strip()
    if not nim:
        raise ValueError("NIM wajib diisi.")
    if not nama:
        raise ValueError("Nama lengkap wajib diisi.")
    with closing(get_conn()) as conn, conn:
        if conn.execute("SELECT 1 FROM anggota WHERE nim = ?", (nim,)).fetchone():
            raise ValueError(f"NIM {nim} sudah terdaftar.")
        new_id = _next_id("A", "anggota", "id_anggota")
        conn.execute(
            """INSERT INTO anggota
               (id_anggota, nim, nama_lengkap, nomor_telepon, email, program_studi, status_aktif)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (new_id, nim, nama, telepon.strip(), email.strip(), prodi, 1 if aktif else 0),
        )
        return new_id


def update_anggota(id_anggota: str, nim: str, nama: str, telepon: str,
                   email: str, prodi: str, aktif: bool) -> None:
    nim = nim.strip()
    nama = nama.strip()
    if not nim:
        raise ValueError("NIM wajib diisi.")
    if not nama:
        raise ValueError("Nama lengkap wajib diisi.")
    with closing(get_conn()) as conn, conn:
        duplikat = conn.execute(
            "SELECT 1 FROM anggota WHERE nim = ? AND id_anggota <> ?", (nim, id_anggota)
        ).fetchone()
        if duplikat:
            raise ValueError(f"NIM {nim} sudah digunakan anggota lain.")
        conn.execute(
            """UPDATE anggota SET nim = ?, nama_lengkap = ?, nomor_telepon = ?,
               email = ?, program_studi = ?, status_aktif = ?
               WHERE id_anggota = ?""",
            (nim, nama, telepon.strip(), email.strip(), prodi, 1 if aktif else 0, id_anggota),
        )


def delete_anggota(id_anggota: str) -> None:
    with closing(get_conn()) as conn, conn:
        dipakai = conn.execute(
            "SELECT COUNT(*) AS n FROM peminjaman WHERE id_anggota = ?", (id_anggota,)
        ).fetchone()["n"]
        if dipakai:
            raise ValueError("Anggota tidak dapat dihapus karena sudah memiliki riwayat peminjaman.")
        conn.execute("DELETE FROM anggota WHERE id_anggota = ?", (id_anggota,))


# ---------------------------------------------------------------------------
# Peminjaman
# ---------------------------------------------------------------------------
def hitung_pinjaman_aktif(id_anggota: str) -> int:
    with closing(get_conn()) as conn:
        return conn.execute(
            """SELECT COUNT(*) AS n FROM peminjaman
               WHERE id_anggota = ? AND status IN ('Dipinjam', 'Terlambat')""",
            (id_anggota,),
        ).fetchone()["n"]


def create_loan(id_anggota: str, id_buku: str, tanggal_pinjam: date,
                kondisi_pinjam: str = "Baik", izin_khusus: bool = False,
                catatan: str = "") -> int:
    if tanggal_pinjam > date.today():
        raise ValueError("Tanggal pinjam tidak boleh melebihi hari ini.")

    with closing(get_conn()) as conn, conn:
        anggota = conn.execute(
            "SELECT * FROM anggota WHERE id_anggota = ?", (id_anggota,)
        ).fetchone()
        if anggota is None:
            raise ValueError("Anggota tidak ditemukan.")
        if not anggota["status_aktif"]:
            raise ValueError(
                f"{anggota['nama_lengkap']} berstatus TIDAK AKTIF sehingga tidak dapat meminjam buku."
            )

        buku = conn.execute("SELECT * FROM buku WHERE id_buku = ?", (id_buku,)).fetchone()
        if buku is None:
            raise ValueError("Buku tidak ditemukan.")
        if buku["stok_tersedia"] <= 0:
            raise ValueError(f"Stok buku \"{buku['judul_buku']}\" sedang habis.")

        aktif = conn.execute(
            """SELECT COUNT(*) AS n FROM peminjaman
               WHERE id_anggota = ? AND status IN ('Dipinjam', 'Terlambat')""",
            (id_anggota,),
        ).fetchone()["n"]
        if aktif >= MAKS_PINJAM and not izin_khusus:
            raise ValueError(
                f"{anggota['nama_lengkap']} sudah meminjam {aktif} buku. "
                f"Batas normal adalah {MAKS_PINJAM} buku; peminjaman tambahan "
                "memerlukan izin khusus Kepala Perpustakaan."
            )
        if izin_khusus and not catatan.strip():
            raise ValueError(
                "Catatan persetujuan Kepala Perpustakaan wajib diisi untuk peminjaman izin khusus."
            )

        dobel = conn.execute(
            """SELECT 1 FROM peminjaman
               WHERE id_anggota = ? AND id_buku = ? AND status IN ('Dipinjam', 'Terlambat')""",
            (id_anggota, id_buku),
        ).fetchone()
        if dobel:
            raise ValueError("Buku yang sama masih dipinjam oleh anggota ini dan belum dikembalikan.")

        tgl_wajib = tanggal_pinjam + timedelta(days=MASA_PINJAM)
        cur = conn.execute(
            """INSERT INTO peminjaman
               (id_anggota, id_buku, tanggal_pinjam, tanggal_wajib_kembali,
                kondisi_pinjam, status, izin_khusus, catatan)
               VALUES (?, ?, ?, ?, ?, 'Dipinjam', ?, ?)""",
            (
                id_anggota, id_buku, tanggal_pinjam.isoformat(), tgl_wajib.isoformat(),
                kondisi_pinjam, 1 if izin_khusus else 0, catatan.strip(),
            ),
        )
        conn.execute(
            "UPDATE buku SET stok_tersedia = stok_tersedia - 1 WHERE id_buku = ?",
            (id_buku,),
        )
        return int(cur.lastrowid)


def list_peminjaman(status: str = "Semua", cari: str = "") -> list[dict]:
    sql = """
        SELECT p.*, a.nama_lengkap, a.nim, b.judul_buku, b.pengarang
        FROM peminjaman p
        JOIN anggota a ON a.id_anggota = p.id_anggota
        JOIN buku b ON b.id_buku = p.id_buku
        WHERE 1=1
    """
    params: list = []
    if status and status != "Semua":
        sql += " AND p.status = ?"
        params.append(status)
    if cari.strip():
        sql += " AND (a.nama_lengkap LIKE ? OR a.nim LIKE ? OR b.judul_buku LIKE ? OR p.id_peminjaman LIKE ?)"
        pola = f"%{cari.strip()}%"
        params += [pola, pola, pola, pola]
    sql += " ORDER BY p.id_peminjaman DESC"
    return _rows(sql, tuple(params))


def get_peminjaman(id_peminjaman: int) -> dict | None:
    data = _rows(
        """SELECT p.*, a.nama_lengkap, a.nim, b.judul_buku, b.pengarang
           FROM peminjaman p
           JOIN anggota a ON a.id_anggota = p.id_anggota
           JOIN buku b ON b.id_buku = p.id_buku
           WHERE p.id_peminjaman = ?""",
        (id_peminjaman,),
    )
    return data[0] if data else None


def list_peminjaman_aktif() -> list[dict]:
    return _rows(
        """SELECT p.*, a.nama_lengkap, a.nim, b.judul_buku
           FROM peminjaman p
           JOIN anggota a ON a.id_anggota = p.id_anggota
           JOIN buku b ON b.id_buku = p.id_buku
           WHERE p.status IN ('Dipinjam', 'Terlambat')
           ORDER BY p.tanggal_wajib_kembali"""
    )


def late_days(tanggal_wajib: str, tanggal_kembali: date | None = None) -> int:
    kembali = tanggal_kembali or date.today()
    return max(0, (kembali - date.fromisoformat(tanggal_wajib)).days)


def estimasi_denda(row: dict) -> int:
    if row["status"] in ("Dipinjam", "Terlambat"):
        return late_days(row["tanggal_wajib_kembali"]) * DENDA_PER_HARI
    return int(row.get("denda_keterlambatan") or 0)


def return_loan(id_peminjaman: int, tanggal_kembali: date, kondisi_kembali: str,
                catatan: str = "") -> dict:
    with closing(get_conn()) as conn, conn:
        loan = conn.execute(
            "SELECT * FROM peminjaman WHERE id_peminjaman = ?", (id_peminjaman,)
        ).fetchone()
        if loan is None:
            raise ValueError("Data peminjaman tidak ditemukan.")
        if loan["status"] not in ("Dipinjam", "Terlambat"):
            raise ValueError("Peminjaman ini sudah diselesaikan sebelumnya.")

        tgl_pinjam = date.fromisoformat(loan["tanggal_pinjam"])
        if tanggal_kembali < tgl_pinjam:
            raise ValueError("Tanggal kembali tidak boleh sebelum tanggal pinjam.")
        if tanggal_kembali > date.today():
            raise ValueError("Tanggal kembali tidak boleh melebihi hari ini.")

        hari_terlambat = max(
            0, (tanggal_kembali - date.fromisoformat(loan["tanggal_wajib_kembali"])).days
        )
        denda_telat = hari_terlambat * DENDA_PER_HARI

        denda_rusak = 0
        if BOBOT_KONDISI[kondisi_kembali] > BOBOT_KONDISI[loan["kondisi_pinjam"]]:
            denda_rusak = {
                "Baik": 0,
                "Rusak Ringan": DENDA_RUSAK_RINGAN,
                "Rusak Berat": DENDA_RUSAK_BERAT,
                "Hilang": DENDA_HILANG,
            }[kondisi_kembali]
        elif kondisi_kembali == "Hilang":
            denda_rusak = DENDA_HILANG
        total = denda_telat + denda_rusak
        status_baru = "Hilang" if kondisi_kembali == "Hilang" else "Kembali"

        gabungan_catatan = loan["catatan"] or ""
        if catatan.strip():
            gabungan_catatan = (gabungan_catatan + " | " if gabungan_catatan else "") + catatan.strip()

        conn.execute(
            """UPDATE peminjaman
               SET tanggal_realisasi_kembali = ?, kondisi_kembali = ?,
                   denda_keterlambatan = ?, denda_kerusakan = ?, denda_akumulasi = ?,
                   status = ?, catatan = ?
               WHERE id_peminjaman = ?""",
            (
                tanggal_kembali.isoformat(), kondisi_kembali, denda_telat, denda_rusak,
                total, status_baru, gabungan_catatan, id_peminjaman,
            ),
        )

        if kondisi_kembali == "Hilang":
            # Koleksi hilang: total eksemplar berkurang, stok tersedia tidak bertambah.
            conn.execute(
                """UPDATE buku SET stok_total = MAX(stok_total - 1, 0),
                   stok_tersedia = MIN(stok_tersedia, MAX(stok_total - 1, 0))
                   WHERE id_buku = ?""",
                (loan["id_buku"],),
            )
        else:
            conn.execute(
                """UPDATE buku SET stok_tersedia = MIN(stok_tersedia + 1, stok_total)
                   WHERE id_buku = ?""",
                (loan["id_buku"],),
            )

        return {
            "hari_terlambat": hari_terlambat,
            "denda_keterlambatan": denda_telat,
            "denda_kerusakan": denda_rusak,
            "total": total,
            "status": status_baru,
        }


def statistik() -> dict:
    with closing(get_conn()) as conn:
        def scalar(sql: str, params: tuple = ()):
            return conn.execute(sql, params).fetchone()[0]

        total_judul = scalar("SELECT COUNT(*) FROM buku") or 0
        total_eksemplar = scalar("SELECT COALESCE(SUM(stok_total), 0) FROM buku") or 0
        stok_tersedia = scalar("SELECT COALESCE(SUM(stok_tersedia), 0) FROM buku") or 0
        anggota_aktif = scalar("SELECT COUNT(*) FROM anggota WHERE status_aktif = 1") or 0
        dipinjam = scalar(
            "SELECT COUNT(*) FROM peminjaman WHERE status IN ('Dipinjam', 'Terlambat')"
        ) or 0
        terlambat = scalar("SELECT COUNT(*) FROM peminjaman WHERE status = 'Terlambat'") or 0
        denda_terkumpul = scalar(
            "SELECT COALESCE(SUM(denda_akumulasi), 0) FROM peminjaman WHERE status IN ('Kembali', 'Hilang')"
        ) or 0
        total_transaksi = scalar("SELECT COUNT(*) FROM peminjaman") or 0

    estimasi = sum(estimasi_denda(l) for l in list_peminjaman_aktif())
    return {
        "total_judul": total_judul,
        "total_eksemplar": total_eksemplar,
        "stok_tersedia": stok_tersedia,
        "anggota_aktif": anggota_aktif,
        "dipinjam": dipinjam,
        "terlambat": terlambat,
        "denda_terkumpul": int(denda_terkumpul),
        "estimasi_denda_aktif": int(estimasi),
        "total_transaksi": total_transaksi,
    }
