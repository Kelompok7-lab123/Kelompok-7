"""
Sistem Peminjaman dan Pengembalian Buku Perpustakaan
Perpustakaan Politeknik Negeri Semarang — Studi Kasus Kelompok 7.

Menjalankan aplikasi:
    .\\venv\\Scripts\\python.exe -m streamlit run app.py
"""

import inspect
from datetime import date, datetime, timedelta

import pandas as pd
import streamlit as st

import database as db

# ---------------------------------------------------------------------------
# Konfigurasi halaman & gaya
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Perpustakaan Polines — Kelompok 7",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

db.init_db()

# Parameter lebar dataframe mengikuti versi Streamlit yang terpasang.
_DF_PARAMS = inspect.signature(st.dataframe).parameters
_DF_WIDTH = {"width": "stretch"} if "width" in _DF_PARAMS else {"use_container_width": True}

CUSTOM_CSS = """
<style>
.stApp {
    background:
        radial-gradient(circle at 92% 2%, rgba(47, 107, 87, 0.10), transparent 34%),
        radial-gradient(circle at 4% 98%, rgba(190, 155, 82, 0.09), transparent 30%),
        #f7f4ec;
}
[data-testid="stHeader"] { background: transparent; }
.block-container { padding-top: 2rem; padding-bottom: 2.5rem; max-width: 1220px; }

h1, h2, h3, h4 {
    font-family: Georgia, 'Times New Roman', serif;
    color: #173d32;
    letter-spacing: -0.01em;
}
p, li, label, .stMarkdown { font-family: 'Segoe UI', Tahoma, sans-serif; }

/* ---------- Sidebar ---------- */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #123a30 0%, #0c271f 100%);
    border-right: 1px solid rgba(255,255,255,0.08);
}
[data-testid="stSidebar"] * { color: #efe9db; }
[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.13); }
[data-testid="stSidebar"] [role="radiogroup"] label {
    padding: 0.48rem 0.75rem;
    border-radius: 10px;
    transition: background 0.15s ease;
}
[data-testid="stSidebar"] [role="radiogroup"] label:hover { background: rgba(255,255,255,0.08); }
[data-testid="stSidebar"] [role="radiogroup"] p { font-size: 0.92rem; }
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] { display: none; }

.brand { display: flex; align-items: center; gap: 0.7rem; padding: 0.25rem 0 0.75rem; }
.brand-icon {
    width: 44px; height: 44px; border-radius: 12px;
    background: rgba(232, 200, 122, 0.16);
    border: 1px solid rgba(232, 200, 122, 0.32);
    display: flex; align-items: center; justify-content: center;
    font-size: 1.35rem;
}
.brand-title { font-family: Georgia, serif; font-size: 1.02rem; line-height: 1.2; color: #f6f1e4; }
.brand-sub { font-size: 0.72rem; letter-spacing: 0.08em; color: #bdb8a5; text-transform: uppercase; }

.side-label {
    font-size: 0.68rem; letter-spacing: 0.14em; text-transform: uppercase;
    color: #b9b29b; margin: 0.2rem 0 0.5rem; font-weight: 600;
}
.side-list { font-size: 0.82rem; line-height: 1.65; color: #ded8c7; }
.side-list b { color: #f3edde; font-weight: 600; }
.side-group { font-size: 0.81rem; line-height: 1.7; color: #ded8c7; }
.side-group span { color: #a9a28c; font-size: 0.74rem; margin-left: 0.15rem; }
.sidebar-foot {
    font-size: 0.7rem; color: #8f8a77; line-height: 1.5;
    border-top: 1px solid rgba(255,255,255,0.1); padding-top: 0.8rem;
}

/* ---------- Header halaman ---------- */
.page-head { display: flex; align-items: center; gap: 1rem; margin-bottom: 1.4rem; }
.page-ico {
    width: 56px; height: 56px; flex: 0 0 56px; border-radius: 15px;
    background: #e3efe8; border: 1px solid #cfe2d8;
    display: flex; align-items: center; justify-content: center; font-size: 1.55rem;
}
.page-head h1 { margin: 0; font-size: 1.85rem; line-height: 1.15; }
.page-head p { margin: 0.2rem 0 0; color: #66746d; font-size: 0.94rem; }

/* ---------- Hero ---------- */
.hero {
    position: relative; overflow: hidden;
    background: linear-gradient(120deg, #174a3b 0%, #1f5c4a 62%, #2b6d57 100%);
    border-radius: 22px; padding: 2.1rem 2.3rem; margin-bottom: 1.5rem;
    box-shadow: 0 14px 34px rgba(18, 58, 48, 0.18);
}
.hero::after {
    content: ""; position: absolute; right: -80px; top: -90px;
    width: 320px; height: 320px; border-radius: 50%;
    background: rgba(232, 200, 122, 0.12);
    border: 1px solid rgba(232, 200, 122, 0.2);
}
.hero::before {
    content: ""; position: absolute; right: 30px; bottom: -120px;
    width: 240px; height: 240px; border-radius: 50%;
    border: 1px solid rgba(255,255,255,0.12);
}
.hero-eyebrow { font-size: 0.7rem; letter-spacing: 0.2em; color: #e8c87a; font-weight: 600; }
.hero h1 { color: #fbf8ef; font-size: 2.05rem; margin: 0.35rem 0 0.4rem; }
.hero p { color: #cfe0d7; margin: 0; max-width: 650px; font-size: 0.95rem; line-height: 1.55; }
.hero-tags { display: flex; gap: 0.5rem; flex-wrap: wrap; margin-top: 1.1rem; }
.hero-tags span {
    background: rgba(255,255,255,0.09); border: 1px solid rgba(255,255,255,0.16);
    color: #f0ead9; border-radius: 999px; padding: 0.26rem 0.75rem; font-size: 0.75rem;
}

/* ---------- Metrik & kartu ---------- */
[data-testid="stMetric"] {
    background: #fffdf8; border: 1px solid #e4ddcc; border-radius: 15px;
    padding: 0.9rem 1rem; box-shadow: 0 3px 12px rgba(23, 61, 50, 0.045);
}
[data-testid="stMetricLabel"] p {
    color: #6d786f; font-size: 0.78rem; font-weight: 600; letter-spacing: 0.02em;
}
[data-testid="stMetricValue"] { color: #173d32; font-family: Georgia, serif; font-size: 1.42rem; }
[data-testid="stMetricDelta"] { font-size: 0.71rem; }

[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(255, 253, 248, 0.72);
    border-radius: 16px;
}

/* ---------- Tombol, tab, input ---------- */
.stButton > button, [data-testid="stBaseButton-secondary"] {
    border-radius: 9px; border-color: #d6cdb9; color: #244a3d; font-weight: 600;
}
.stButton > button[kind="primary"], [data-testid="stBaseButton-primary"] {
    background: #1f5c4a; border-color: #1f5c4a; color: #fdfbf4;
}
.stButton > button[kind="primary"]:hover, [data-testid="stBaseButton-primary"]:hover {
    background: #174a3b; border-color: #174a3b;
}
[data-baseweb="tab-list"] { gap: 0.35rem; }
[data-baseweb="tab"] {
    border-radius: 9px 9px 0 0; padding: 0.45rem 1rem; color: #5f6d66;
}
[aria-selected="true"][data-baseweb="tab"] { color: #174a3b; font-weight: 600; }

/* ---------- Notifikasi ---------- */
.alert {
    background: #fdf1e3; border: 1px solid #efd2ae; border-left: 4px solid #d28a37;
    border-radius: 12px; padding: 0.85rem 1rem; margin: 0.4rem 0 1.1rem;
    color: #74491c; font-size: 0.9rem;
}
.alert b { color: #5c3610; }
.info-strip {
    background: #edf4ef; border: 1px solid #d3e4da; border-left: 4px solid #2f6b57;
    border-radius: 12px; padding: 0.75rem 1rem; margin: 0 0 1.1rem;
    color: #2a5042; font-size: 0.87rem;
}
.app-footer {
    text-align: center; color: #8a938c; font-size: 0.75rem;
    border-top: 1px solid #e4ddcc; margin-top: 2.4rem; padding-top: 1.1rem;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

STATUS_LABEL = {
    "Dipinjam": "🟠 Dipinjam",
    "Terlambat": "🔴 Terlambat",
    "Kembali": "🟢 Kembali",
    "Hilang": "⚫ Hilang",
}
DENDA_KONDISI = {
    "Baik": 0,
    "Rusak Ringan": db.DENDA_RUSAK_RINGAN,
    "Rusak Berat": db.DENDA_RUSAK_BERAT,
    "Hilang": db.DENDA_HILANG,
}
NAV_ITEMS = [
    "Ringkasan",
    "Koleksi Buku",
    "Anggota",
    "Peminjaman",
    "Pengembalian",
    "Laporan & Denda",
    "Tentang Sistem",
]


# ---------------------------------------------------------------------------
# Utilitas tampilan
# ---------------------------------------------------------------------------
def rp(nilai) -> str:
    return "Rp " + f"{int(nilai or 0):,}".replace(",", ".")


def tgl_short(iso: str | None) -> str:
    if not iso:
        return "—"
    try:
        return date.fromisoformat(iso).strftime("%d/%m/%Y")
    except ValueError:
        return iso


def flash(pesan: str) -> None:
    st.session_state["_flash"] = pesan


def show_flash() -> None:
    pesan = st.session_state.pop("_flash", None)
    if pesan:
        st.success(pesan, icon="✅")


def page_header(icon: str, title: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <div class="page-head">
            <div class="page-ico">{icon}</div>
            <div>
                <h1>{title}</h1>
                <p>{subtitle}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def tampil_tabel(df: pd.DataFrame, height: int | None = None) -> None:
    if df.empty:
        st.info("Belum ada data untuk ditampilkan.")
        return
    kwargs = {"hide_index": True, **_DF_WIDTH}
    if height:
        kwargs["height"] = height
    st.dataframe(df, **kwargs)


def df_buku(rows: list[dict]) -> pd.DataFrame:
    data = []
    for b in rows:
        tersedia = int(b["stok_tersedia"])
        data.append(
            {
                "ID": b["id_buku"],
                "Judul Buku": b["judul_buku"],
                "Pengarang": b["pengarang"] or "—",
                "Penerbit": b["penerbit"] or "—",
                "Tahun": b["tahun_terbit"],
                "Jenis": b["jenis_buku"] or "—",
                "Stok": f"{tersedia} / {b['stok_total']}",
                "Status": "🟢 Tersedia" if tersedia > 0 else "🔴 Habis",
            }
        )
    return pd.DataFrame(data)


def df_anggota(rows: list[dict]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "ID": a["id_anggota"],
                "NIM": a["nim"],
                "Nama Lengkap": a["nama_lengkap"],
                "Program Studi": a["program_studi"] or "—",
                "No. Telepon": a["nomor_telepon"] or "—",
                "Email": a["email"] or "—",
                "Status": "🟢 Aktif" if a["status_aktif"] else "🔴 Nonaktif",
            }
            for a in rows
        ]
    )


def denda_tampil(row: dict) -> int:
    if row["status"] in ("Dipinjam", "Terlambat"):
        return db.estimasi_denda(row)
    return int(row.get("denda_akumulasi") or 0)


def df_peminjaman(rows: list[dict]) -> pd.DataFrame:
    data = []
    for r in rows:
        keterangan = []
        if r["status"] == "Terlambat":
            keterangan.append(f"Terlambat {db.late_days(r['tanggal_wajib_kembali'])} hari")
        if r.get("izin_khusus"):
            keterangan.append("Izin khusus")
        if r.get("kondisi_kembali") and r["kondisi_kembali"] != "Baik":
            keterangan.append(f"Kembali: {r['kondisi_kembali']}")
        data.append(
            {
                "ID": f"TRX-{int(r['id_peminjaman']):04d}",
                "NIM": r["nim"],
                "Anggota": r["nama_lengkap"],
                "Buku": r["judul_buku"],
                "Pinjam": tgl_short(r["tanggal_pinjam"]),
                "Jatuh Tempo": tgl_short(r["tanggal_wajib_kembali"]),
                "Kembali": tgl_short(r["tanggal_realisasi_kembali"]),
                "Status": STATUS_LABEL.get(r["status"], r["status"]),
                "Denda": rp(denda_tampil(r)),
                "Keterangan": "; ".join(keterangan) or "—",
            }
        )
    return pd.DataFrame(data)


def ringkasan_denda(rows: list[dict]) -> dict:
    selesai = [r for r in rows if r["status"] in ("Kembali", "Hilang")]
    return {
        "terkumpul": sum(int(r["denda_akumulasi"] or 0) for r in selesai),
        "telat": sum(int(r["denda_keterlambatan"] or 0) for r in selesai),
        "kerusakan": sum(int(r["denda_kerusakan"] or 0) for r in selesai),
        "estimasi": sum(db.estimasi_denda(r) for r in rows if r["status"] in ("Dipinjam", "Terlambat")),
    }


# ---------------------------------------------------------------------------
# Halaman: Ringkasan
# ---------------------------------------------------------------------------
def halaman_ringkasan() -> None:
    st.markdown(
        """
        <div class="hero">
            <div class="hero-eyebrow">SISTEM PERPUSTAKAAN · KELOMPOK 7</div>
            <h1>Perpustakaan Politeknik Negeri Semarang</h1>
            <p>Sistem peminjaman dan pengembalian buku untuk mengelola koleksi, anggota,
            transaksi, serta perhitungan denda keterlambatan secara otomatis.</p>
            <div class="hero-tags">
                <span>📖 Masa pinjam 7 hari</span>
                <span>📚 Maksimal 2 buku</span>
                <span>💰 Denda Rp1.000/hari/buku</span>
                <span>✅ Cek status anggota</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    show_flash()

    s = db.statistik()

    c1, c2, c3 = st.columns(3)
    c1.metric("Judul Buku", s["total_judul"], f"{s['total_eksemplar']} eksemplar")
    c2.metric("Stok Tersedia", s["stok_tersedia"], f"{s['total_eksemplar'] - s['stok_tersedia']} dipinjam")
    c3.metric("Anggota Aktif", s["anggota_aktif"], "orang")

    c4, c5, c6 = st.columns(3)
    c4.metric("Peminjaman Aktif", s["dipinjam"], "belum kembali")
    c5.metric(
        "Terlambat",
        s["terlambat"],
        "perlu tindakan" if s["terlambat"] else "tepat waktu",
        delta_color="inverse",
    )
    c6.metric("Denda Terkumpul", rp(s["denda_terkumpul"]), f"aktif {rp(s['estimasi_denda_aktif'])}")

    if s["terlambat"]:
        st.markdown(
            f"""
            <div class="alert">
                ⚠️ <b>{s['terlambat']} peminjaman terlambat.</b>
                Estimasi denda berjalan saat ini <b>{rp(s['estimasi_denda_aktif'])}</b>.
                Buka menu <b>Pengembalian</b> untuk memproses pengembalian dan menghitung denda.
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown('<div class="info-strip">💡 Denda dihitung otomatis: Rp1.000 × jumlah buku × jumlah hari keterlambatan. Kondisi buku dicatat sebelum dan sesudah dipinjam.</div>', unsafe_allow_html=True)

    st.markdown("---")

    semua = db.list_peminjaman()
    kiri, kanan = st.columns(2, gap="large")

    with kiri:
        st.subheader("📈 Peminjaman 7 Hari Terakhir")
        tanggal_7 = [date.today() - timedelta(days=i) for i in range(6, -1, -1)]
        hitung = {d: 0 for d in tanggal_7}
        for r in semua:
            try:
                d = date.fromisoformat(r["tanggal_pinjam"])
            except (ValueError, TypeError):
                continue
            if d in hitung:
                hitung[d] += 1
        chart = pd.DataFrame(
            {
                "Peminjaman": [hitung[d] for d in tanggal_7],
            },
            index=[d.strftime("%d/%m") for d in tanggal_7],
        )
        st.bar_chart(chart, height=250, color="#2f6b57")

    with kanan:
        st.subheader("🏆 Buku Paling Sering Dipinjam")
        if semua:
            populer = (
                pd.DataFrame(semua)
                .groupby("judul_buku")
                .size()
                .sort_values(ascending=False)
                .head(5)
            )
            populer_df = pd.DataFrame({"Jumlah": populer.values}, index=populer.index)
            st.bar_chart(populer_df, height=250, color="#be9b52", horizontal=True)
        else:
            st.info("Belum ada data peminjaman.")

    st.markdown("---")

    st.subheader("⏳ Peminjaman Sedang Berjalan")
    aktif = db.list_peminjaman_aktif()
    if aktif:
        tampil_tabel(df_peminjaman(aktif), height=260)
    else:
        st.success("Tidak ada peminjaman aktif. Semua buku sudah kembali.", icon="🎉")

    st.subheader("🕘 Transaksi Terbaru")
    terbaru = semua[:6]
    if terbaru:
        tampil_tabel(df_peminjaman(terbaru), height=270)
    else:
        st.info("Belum ada transaksi peminjaman.")


# ---------------------------------------------------------------------------
# Halaman: Koleksi Buku
# ---------------------------------------------------------------------------
def halaman_buku() -> None:
    page_header("📚", "Koleksi Buku", "Kelola data buku, stok eksemplar, pengarang, penerbit, dan jenis koleksi.")
    show_flash()

    semua_buku = db.list_buku()
    c1, c2, c3 = st.columns(3)
    c1.metric("Judul Terdaftar", len(semua_buku))
    c2.metric("Total Eksemplar", sum(int(b["stok_total"]) for b in semua_buku))
    c3.metric("Stok Tersedia", sum(int(b["stok_tersedia"]) for b in semua_buku))

    tab_daftar, tab_kelola = st.tabs(["📖 Daftar Buku", "➕ Kelola Buku"])

    with tab_daftar:
        f1, f2 = st.columns([2, 1])
        cari = f1.text_input("Cari buku", placeholder="Judul, pengarang, penerbit, atau ID...", key="cari_buku")
        jenis = f2.selectbox("Jenis buku", ["Semua"] + db.JENIS_BUKU, key="filter_jenis")
        rows = db.list_buku(cari, jenis)
        st.caption(f"{len(rows)} buku ditemukan")
        tampil_tabel(df_buku(rows))

    with tab_kelola:
        kiri, kanan = st.columns(2, gap="large")

        with kiri:
            with st.container(border=True):
                st.markdown("#### Tambah Buku Baru")
                st.caption("ID buku dibuat otomatis oleh sistem (contoh: B011).")
                with st.form("form_tambah_buku", clear_on_submit=True):
                    judul = st.text_input("Judul buku *", placeholder="Contoh: Struktur Data")
                    c1, c2 = st.columns(2)
                    pengarang = c1.text_input("Pengarang", placeholder="Nama pengarang")
                    penerbit = c2.text_input("Penerbit", placeholder="Nama penerbit")
                    c3, c4, c5 = st.columns([1.1, 1.6, 1])
                    tahun = c3.number_input(
                        "Tahun terbit", min_value=1900, max_value=date.today().year,
                        value=date.today().year, step=1,
                    )
                    jenis_baru = c4.selectbox("Jenis buku", db.JENIS_BUKU)
                    stok = c5.number_input("Eksemplar", min_value=1, max_value=100, value=1, step=1)
                    simpan = st.form_submit_button("Simpan Buku", type="primary")

                if simpan:
                    try:
                        new_id = db.add_buku(judul, pengarang, penerbit, int(tahun), jenis_baru, int(stok))
                    except ValueError as e:
                        st.error(str(e))
                    else:
                        flash(f"Buku \"{judul.strip()}\" ({new_id}) berhasil ditambahkan.")
                        st.rerun()

        with kanan:
            with st.container(border=True):
                st.markdown("#### Edit Data Buku")
                if not semua_buku:
                    st.info("Belum ada buku untuk diedit.")
                else:
                    opsi = {b["id_buku"]: b for b in semua_buku}
                    pilih = st.selectbox(
                        "Pilih buku",
                        list(opsi.keys()),
                        format_func=lambda k: f"{k} — {opsi[k]['judul_buku']}",
                        key="edit_buku_pilih",
                    )
                    b = opsi[pilih]
                    with st.form(f"form_edit_buku_{pilih}"):
                        judul_e = st.text_input("Judul buku *", value=b["judul_buku"], key=f"eb_judul_{pilih}")
                        c1, c2 = st.columns(2)
                        pengarang_e = c1.text_input("Pengarang", value=b["pengarang"] or "", key=f"eb_pengarang_{pilih}")
                        penerbit_e = c2.text_input("Penerbit", value=b["penerbit"] or "", key=f"eb_penerbit_{pilih}")
                        c3, c4, c5 = st.columns([1.1, 1.6, 1])
                        tahun_e = c3.number_input(
                            "Tahun terbit", min_value=1900, max_value=date.today().year,
                            value=int(b["tahun_terbit"] or date.today().year), step=1,
                            key=f"eb_tahun_{pilih}",
                        )
                        jenis_e = c4.selectbox(
                            "Jenis buku", db.JENIS_BUKU,
                            index=db.JENIS_BUKU.index(b["jenis_buku"]) if b["jenis_buku"] in db.JENIS_BUKU else 0,
                            key=f"eb_jenis_{pilih}",
                        )
                        stok_e = c5.number_input(
                            "Stok total", min_value=0, max_value=100,
                            value=int(b["stok_total"]), step=1, key=f"eb_stok_{pilih}",
                        )
                        update = st.form_submit_button("Simpan Perubahan", type="primary")

                    if update:
                        try:
                            db.update_buku(pilih, judul_e, pengarang_e, penerbit_e, int(tahun_e), jenis_e, int(stok_e))
                        except ValueError as e:
                            st.error(str(e))
                        else:
                            flash(f"Data buku {pilih} berhasil diperbarui.")
                            st.rerun()

                    with st.expander("🗑️ Hapus buku"):
                        st.caption("Buku yang sudah memiliki riwayat peminjaman tidak dapat dihapus.")
                        yakin = st.checkbox("Saya yakin ingin menghapus buku ini", key=f"cek_hapus_buku_{pilih}")
                        if st.button("Hapus Buku", key=f"btn_hapus_buku_{pilih}", disabled=not yakin):
                            try:
                                db.delete_buku(pilih)
                            except ValueError as e:
                                st.error(str(e))
                            else:
                                flash(f"Buku {pilih} berhasil dihapus.")
                                st.rerun()


# ---------------------------------------------------------------------------
# Halaman: Anggota
# ---------------------------------------------------------------------------
def halaman_anggota() -> None:
    page_header("👥", "Data Anggota", "Kelola anggota perpustakaan dan status keaktifannya sebelum bertransaksi.")
    show_flash()

    semua = db.list_anggota()
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Anggota", len(semua))
    c2.metric("Anggota Aktif", sum(1 for a in semua if a["status_aktif"]))
    c3.metric("Nonaktif", sum(1 for a in semua if not a["status_aktif"]))

    tab_daftar, tab_kelola = st.tabs(["📋 Daftar Anggota", "➕ Kelola Anggota"])

    with tab_daftar:
        cari = st.text_input("Cari anggota", placeholder="Nama, NIM, atau ID anggota...", key="cari_anggota")
        rows = db.list_anggota(cari)
        st.caption(f"{len(rows)} anggota ditemukan")
        tampil_tabel(df_anggota(rows))

    with tab_kelola:
        kiri, kanan = st.columns(2, gap="large")

        with kiri:
            with st.container(border=True):
                st.markdown("#### Tambah Anggota")
                st.caption("NIM wajib diisi dan tidak boleh sama antaranggota.")
                with st.form("form_tambah_anggota", clear_on_submit=True):
                    c1, c2 = st.columns(2)
                    nim = c1.text_input("NIM *", placeholder="Contoh: 20240099")
                    nama = c2.text_input("Nama lengkap *", placeholder="Nama mahasiswa")
                    c3, c4 = st.columns(2)
                    telepon = c3.text_input("Nomor telepon", placeholder="08xx-xxxx-xxxx")
                    prodi = c4.selectbox("Program studi", db.PROGRAM_STUDI)
                    email = st.text_input("Email", placeholder="nama@student.polines.ac.id")
                    aktif = st.checkbox("Anggota aktif (boleh meminjam buku)", value=True)
                    simpan = st.form_submit_button("Simpan Anggota", type="primary")

                if simpan:
                    try:
                        new_id = db.add_anggota(nim, nama, telepon, email, prodi, aktif)
                    except ValueError as e:
                        st.error(str(e))
                    else:
                        flash(f"Anggota \"{nama.strip()}\" ({new_id}) berhasil ditambahkan.")
                        st.rerun()

        with kanan:
            with st.container(border=True):
                st.markdown("#### Edit Data Anggota")
                if not semua:
                    st.info("Belum ada anggota untuk diedit.")
                else:
                    opsi = {a["id_anggota"]: a for a in semua}
                    pilih = st.selectbox(
                        "Pilih anggota",
                        list(opsi.keys()),
                        format_func=lambda k: f"{k} — {opsi[k]['nim']} — {opsi[k]['nama_lengkap']}",
                        key="edit_anggota_pilih",
                    )
                    a = opsi[pilih]
                    with st.form(f"form_edit_anggota_{pilih}"):
                        c1, c2 = st.columns(2)
                        nim_e = c1.text_input("NIM *", value=a["nim"], key=f"ea_nim_{pilih}")
                        nama_e = c2.text_input("Nama lengkap *", value=a["nama_lengkap"], key=f"ea_nama_{pilih}")
                        c3, c4 = st.columns(2)
                        telepon_e = c3.text_input("Nomor telepon", value=a["nomor_telepon"] or "", key=f"ea_telp_{pilih}")
                        prodi_e = c4.selectbox(
                            "Program studi", db.PROGRAM_STUDI,
                            index=db.PROGRAM_STUDI.index(a["program_studi"]) if a["program_studi"] in db.PROGRAM_STUDI else 0,
                            key=f"ea_prodi_{pilih}",
                        )
                        email_e = st.text_input("Email", value=a["email"] or "", key=f"ea_email_{pilih}")
                        aktif_e = st.checkbox(
                            "Anggota aktif (boleh meminjam buku)",
                            value=bool(a["status_aktif"]), key=f"ea_aktif_{pilih}",
                        )
                        st.caption("Menonaktifkan anggota tidak membatalkan peminjaman yang masih berjalan.")
                        update = st.form_submit_button("Simpan Perubahan", type="primary")

                    if update:
                        try:
                            db.update_anggota(pilih, nim_e, nama_e, telepon_e, email_e, prodi_e, aktif_e)
                        except ValueError as e:
                            st.error(str(e))
                        else:
                            flash(f"Data anggota {pilih} berhasil diperbarui.")
                            st.rerun()

                    with st.expander("🗑️ Hapus anggota"):
                        st.caption("Anggota yang memiliki riwayat peminjaman tidak dapat dihapus.")
                        yakin = st.checkbox("Saya yakin ingin menghapus anggota ini", key=f"cek_hapus_anggota_{pilih}")
                        if st.button("Hapus Anggota", key=f"btn_hapus_anggota_{pilih}", disabled=not yakin):
                            try:
                                db.delete_anggota(pilih)
                            except ValueError as e:
                                st.error(str(e))
                            else:
                                flash(f"Anggota {pilih} berhasil dihapus.")
                                st.rerun()


# ---------------------------------------------------------------------------
# Halaman: Peminjaman
# ---------------------------------------------------------------------------
def halaman_peminjaman() -> None:
    page_header("📝", "Peminjaman Buku", "Catat transaksi peminjaman dengan validasi stok, status anggota, dan batas jumlah buku.")
    show_flash()

    s = db.statistik()
    c1, c2, c3 = st.columns(3)
    c1.metric("Peminjaman Aktif", s["dipinjam"])
    c2.metric("Terlambat", s["terlambat"])
    c3.metric("Buku Tersedia", s["stok_tersedia"])

    st.markdown(
        '<div class="info-strip">📌 Aturan: peminjam harus <b>mahasiswa aktif</b>, masa pinjam <b>7 hari</b>, '
        'maksimal <b>2 buku</b> dalam satu waktu, dan denda <b>Rp1.000 per buku per hari</b> keterlambatan.</div>',
        unsafe_allow_html=True,
    )

    anggota_aktif = db.list_anggota(hanya_aktif=True)
    buku_tersedia = [b for b in db.list_buku() if int(b["stok_tersedia"]) > 0]

    with st.container(border=True):
        st.markdown("#### Formulir Peminjaman Baru")
        if not anggota_aktif:
            st.warning("Belum ada anggota aktif. Tambahkan atau aktifkan anggota terlebih dahulu.")
        elif not buku_tersedia:
            st.warning("Tidak ada buku dengan stok tersedia. Tambahkan stok buku terlebih dahulu.")
        else:
            opsi_a = {a["id_anggota"]: a for a in anggota_aktif}
            pilih_a = st.selectbox(
                "Pilih anggota",
                list(opsi_a.keys()),
                format_func=lambda k: f"{k} — {opsi_a[k]['nim']} — {opsi_a[k]['nama_lengkap']}",
                key="pinjam_anggota",
            )
            a = opsi_a[pilih_a]
            aktif_ke = db.hitung_pinjaman_aktif(pilih_a)
            st.caption(
                f"Program studi: {a['program_studi'] or '—'}  ·  "
                f"Peminjaman aktif: {aktif_ke}/{db.MAKS_PINJAM} buku"
            )
            if aktif_ke >= db.MAKS_PINJAM:
                st.warning(
                    f"Anggota ini sudah meminjam {aktif_ke} buku. Peminjaman berikutnya "
                    "memerlukan centang izin khusus Kepala Perpustakaan."
                )

            opsi_b = {b["id_buku"]: b for b in buku_tersedia}
            pilih_b = st.selectbox(
                "Pilih buku",
                list(opsi_b.keys()),
                format_func=lambda k: f"{k} — {opsi_b[k]['judul_buku']} (stok: {opsi_b[k]['stok_tersedia']})",
                key="pinjam_buku",
            )
            b = opsi_b[pilih_b]
            st.caption(f"Pengarang: {b['pengarang'] or '—'}  ·  Penerbit: {b['penerbit'] or '—'}  ·  Jenis: {b['jenis_buku'] or '—'}")

            c1, c2 = st.columns(2)
            tanggal_pinjam = c1.date_input(
                "Tanggal pinjam",
                value=date.today(),
                max_value=date.today(),
                format="DD/MM/YYYY",
                key="pinjam_tanggal",
            )
            c2.text_input(
                "Tanggal wajib kembali",
                value=(tanggal_pinjam + timedelta(days=db.MASA_PINJAM)).strftime("%d/%m/%Y"),
                disabled=True,
            )

            kondisi_pinjam = st.selectbox(
                "Kondisi buku sebelum dipinjam",
                ["Baik", "Rusak Ringan", "Rusak Berat"],
                key="pinjam_kondisi",
                help="Catat kondisi awal agar perubahan kondisi saat kembali dapat diketahui.",
            )

            with st.expander("🔑 Izin khusus / catatan"):
                izin = st.checkbox(
                    "Ada persetujuan khusus dari Kepala Perpustakaan (boleh lebih dari 2 buku)",
                    key="pinjam_izin",
                )
                catatan = st.text_area(
                    "Catatan persetujuan / keterangan",
                    placeholder="Contoh: Disetujui Kepala Perpustakaan untuk keperluan lomba karya tulis.",
                    key="pinjam_catatan",
                )

            if st.button("Proses Peminjaman", type="primary", key="btn_pinjam"):
                try:
                    id_loan = db.create_loan(
                        pilih_a, pilih_b, tanggal_pinjam, kondisi_pinjam, izin, catatan
                    )
                except ValueError as e:
                    st.error(str(e))
                else:
                    flash(
                        f"Peminjaman TRX-{id_loan:04d} berhasil. \"{b['judul_buku']}\" "
                        f"dipinjam oleh {a['nama_lengkap']} hingga "
                        f"{(tanggal_pinjam + timedelta(days=db.MASA_PINJAM)).strftime('%d/%m/%Y')}."
                    )
                    st.rerun()

    st.markdown("---")
    st.subheader("⏳ Daftar Peminjaman Aktif")
    aktif = db.list_peminjaman_aktif()
    if aktif:
        st.caption(f"{len(aktif)} transaksi belum dikembalikan. Denda pada tabel adalah estimasi jika dikembalikan hari ini.")
        tampil_tabel(df_peminjaman(aktif), height=300)
    else:
        st.success("Tidak ada peminjaman aktif.", icon="🎉")

    with st.expander("ℹ️ Catatan validasi sistem"):
        st.markdown(
            """
            - Anggota dengan status **nonaktif** ditolak oleh sistem.
            - Buku dengan **stok 0** tidak muncul pada pilihan peminjaman.
            - Peminjaman **lebih dari 2 buku** ditolak kecuali dicentang izin khusus dan diberi catatan.
            - Buku yang **masih dipinjam** oleh anggota yang sama tidak dapat dipinjam ulang.
            - Tanggal wajib kembali dihitung otomatis **7 hari** dari tanggal pinjam.
            """
        )


# ---------------------------------------------------------------------------
# Halaman: Pengembalian
# ---------------------------------------------------------------------------
def halaman_pengembalian() -> None:
    page_header("🔄", "Pengembalian Buku", "Proses pengembalian, catat kondisi akhir buku, dan hitung denda secara otomatis.")
    show_flash()

    aktif = db.list_peminjaman_aktif()
    if not aktif:
        st.success("Tidak ada buku yang perlu dikembalikan saat ini. Semua peminjaman sudah selesai.", icon="🎉")
        return

    opsi = {int(r["id_peminjaman"]): r for r in aktif}

    def label(loan_id: int) -> str:
        r = opsi[loan_id]
        return (
            f"TRX-{loan_id:04d} — {r['nama_lengkap']} ({r['nim']}) — "
            f"{r['judul_buku']} — jatuh tempo {tgl_short(r['tanggal_wajib_kembali'])}"
        )

    pilih = st.selectbox("Pilih transaksi peminjaman", list(opsi.keys()), format_func=label, key="ret_pilih")
    loan = opsi[pilih]

    pinjam = date.fromisoformat(loan["tanggal_pinjam"])
    wajib = date.fromisoformat(loan["tanggal_wajib_kembali"])

    st.markdown(
        f"""
        <div class="info-strip">
            👤 <b>{loan['nama_lengkap']}</b> · NIM {loan['nim']} · 📖 <b>{loan['judul_buku']}</b><br>
            Tanggal pinjam {tgl_short(loan['tanggal_pinjam'])} · Wajib kembali {tgl_short(loan['tanggal_wajib_kembali'])}
            · Kondisi saat dipinjam: <b>{loan['kondisi_pinjam']}</b>
            {'· <b>Izin khusus</b>' if loan['izin_khusus'] else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        st.markdown("#### Formulir Pengembalian")
        c1, c2 = st.columns(2)
        tanggal_kembali = c1.date_input(
            "Tanggal realisasi kembali",
            value=date.today(),
            min_value=pinjam,
            max_value=date.today(),
            format="DD/MM/YYYY",
            key=f"ret_tanggal_{pilih}",
        )
        kondisi_kembali = c2.selectbox(
            "Kondisi buku setelah dipinjam",
            db.KONDISI_BUKU,
            key=f"ret_kondisi_{pilih}",
            help="Jika kondisi memburuk, denda kerusakan/kehilangan akan ditambahkan otomatis.",
        )

        hari_telat = max(0, (tanggal_kembali - wajib).days)
        denda_telat = hari_telat * db.DENDA_PER_HARI
        denda_rusak = 0
        if db.BOBOT_KONDISI[kondisi_kembali] > db.BOBOT_KONDISI[loan["kondisi_pinjam"]]:
            denda_rusak = DENDA_KONDISI[kondisi_kembali]
        elif kondisi_kembali == "Hilang":
            denda_rusak = db.DENDA_HILANG

        m1, m2 = st.columns(2)
        m1.metric("Hari Terlambat", f"{hari_telat} hari")
        m2.metric("Denda Keterlambatan", rp(denda_telat))
        m3, m4 = st.columns(2)
        m3.metric("Denda Kerusakan", rp(denda_rusak))
        m4.metric("Total Denda", rp(denda_telat + denda_rusak))

        if hari_telat:
            st.warning(
                f"Terlambat {hari_telat} hari. Denda = {hari_telat} hari × "
                f"{rp(db.DENDA_PER_HARI)} = {rp(denda_telat)}."
            )
        if db.BOBOT_KONDISI[kondisi_kembali] > db.BOBOT_KONDISI[loan["kondisi_pinjam"]]:
            st.warning(
                f"Kondisi buku berubah dari **{loan['kondisi_pinjam']}** menjadi "
                f"**{kondisi_kembali}**, dikenakan denda kerusakan {rp(denda_rusak)}."
            )
        if kondisi_kembali == "Hilang":
            st.error(
                f"Buku dinyatakan **hilang**. Denda kehilangan {rp(db.DENDA_HILANG)} dan "
                "jumlah eksemplar koleksi akan dikurangi satu."
            )

        catatan = st.text_area(
            "Catatan petugas (opsional)",
            placeholder="Contoh: Halaman sobek, sudah dilaporkan ke petugas.",
            key=f"ret_catatan_{pilih}",
        )

        if st.button("Proses Pengembalian", type="primary", key=f"btn_ret_{pilih}"):
            try:
                hasil = db.return_loan(pilih, tanggal_kembali, kondisi_kembali, catatan)
            except ValueError as e:
                st.error(str(e))
            else:
                flash(
                    f"Pengembalian TRX-{pilih:04d} berhasil dengan status {hasil['status']}. "
                    f"Denda keterlambatan {rp(hasil['denda_keterlambatan'])}, "
                    f"denda kerusakan/kehilangan {rp(hasil['denda_kerusakan'])}, "
                    f"total {rp(hasil['total'])}."
                )
                st.rerun()

    st.caption(
        "Kebijakan denda: Rusak Ringan Rp10.000 · Rusak Berat Rp50.000 · "
        "Hilang Rp100.000 · Terlambat Rp1.000/buku/hari."
    )


# ---------------------------------------------------------------------------
# Halaman: Laporan & Denda
# ---------------------------------------------------------------------------
def halaman_laporan() -> None:
    page_header("📊", "Laporan & Denda", "Pantau seluruh riwayat transaksi, rekap denda, dan unduh laporan.")
    show_flash()

    semua = db.list_peminjaman()
    ringkas = ringkasan_denda(semua)

    c1, c2 = st.columns(2)
    c1.metric("Total Transaksi", len(semua))
    c2.metric("Denda Terkumpul", rp(ringkas["terkumpul"]))
    c3, c4 = st.columns(2)
    c3.metric("Denda Keterlambatan", rp(ringkas["telat"]))
    c4.metric("Denda Kerusakan", rp(ringkas["kerusakan"]))

    st.caption(
        f"Estimasi denda dari peminjaman yang masih berjalan: **{rp(ringkas['estimasi'])}**."
    )

    with st.container(border=True):
        f1, f2 = st.columns([1, 2])
        status = f1.selectbox(
            "Filter status", ["Semua", "Dipinjam", "Terlambat", "Kembali", "Hilang"], key="lap_status"
        )
        cari = f2.text_input(
            "Cari transaksi", placeholder="Nama, NIM, judul buku, atau ID transaksi...", key="lap_cari"
        )
        rows = db.list_peminjaman(status, cari)

    st.caption(f"{len(rows)} transaksi ditemukan")
    tampil_tabel(df_peminjaman(rows))

    if rows:
        ekspor = pd.DataFrame(
            [
                {
                    "ID_Peminjaman": r["id_peminjaman"],
                    "NIM": r["nim"],
                    "Nama_Anggota": r["nama_lengkap"],
                    "ID_Buku": r["id_buku"],
                    "Judul_Buku": r["judul_buku"],
                    "Tanggal_Pinjam": r["tanggal_pinjam"],
                    "Tanggal_Wajib_Kembali": r["tanggal_wajib_kembali"],
                    "Tanggal_Realisasi_Kembali": r["tanggal_realisasi_kembali"] or "",
                    "Status": r["status"],
                    "Kondisi_Pinjam": r["kondisi_pinjam"],
                    "Kondisi_Kembali": r["kondisi_kembali"] or "",
                    "Denda_Keterlambatan": int(r["denda_keterlambatan"] or 0),
                    "Denda_Kerusakan": int(r["denda_kerusakan"] or 0),
                    "Denda_Akumulasi": int(r["denda_akumulasi"] or 0),
                    "Izin_Khusus": "Ya" if r["izin_khusus"] else "Tidak",
                    "Catatan": r["catatan"] or "",
                }
                for r in rows
            ]
        )
        st.download_button(
            "⬇️ Unduh Laporan CSV",
            data=ekspor.to_csv(index=False).encode("utf-8-sig"),
            file_name=f"laporan_perpustakaan_{date.today():%Y%m%d}.csv",
            mime="text/csv",
        )

    st.markdown("---")
    st.subheader("💰 Rekap Denda per Anggota")

    data_denda = []
    for r in semua:
        nilai = denda_tampil(r)
        if nilai:
            data_denda.append(
                {
                    "NIM": r["nim"],
                    "Anggota": r["nama_lengkap"],
                    "Denda": nilai,
                }
            )
    if data_denda:
        rekap = (
            pd.DataFrame(data_denda)
            .groupby(["NIM", "Anggota"], as_index=False)
            .agg({"Denda": "sum"})
            .sort_values("Denda", ascending=False)
        )
        rekap["Denda"] = rekap["Denda"].apply(rp)
        tampil_tabel(rekap)
    else:
        st.info("Belum ada denda yang tercatat.")

    with st.expander("ℹ️ Keterangan perhitungan"):
        st.markdown(
            """
            | Komponen | Nilai |
            |---|---|
            | Denda keterlambatan | Rp1.000 × jumlah hari terlambat (per buku) |
            | Rusak ringan | Rp10.000 |
            | Rusak berat | Rp50.000 |
            | Buku hilang | Rp100.000 |
            | Masa pinjam | 7 hari |
            | Batas peminjaman | 2 buku per anggota |
            """
        )


# ---------------------------------------------------------------------------
# Halaman: Tentang
# ---------------------------------------------------------------------------
def halaman_tentang() -> None:
    page_header("🏛️", "Tentang Sistem", "Studi kasus Perpustakaan Politeknik Negeri Semarang — Kelompok 7.")
    show_flash()

    st.markdown(
        """
        ### Studi Kasus
        Perpustakaan Politeknik Negeri Semarang (Polines) mendukung kegiatan akademik mahasiswa,
        dosen, dan tenaga kependidikan. Koleksi meliputi buku teks perkuliahan, modul praktikum,
        laporan tugas akhir, jurnal ilmiah, dan referensi umum. Perpustakaan dikelola oleh Kepala
        Perpustakaan dan dua staf layanan sirkulasi.

        ### Aturan Peminjaman
        - Peminjam harus **mahasiswa aktif** dan mencantumkan **NIM**.
        - Masa peminjaman **7 hari**.
        - Maksimal **2 buku** dalam satu waktu.
        - Denda keterlambatan **Rp1.000 per buku per hari**.
        - Buku harus dikembalikan dalam kondisi baik.
        """
    )

    st.markdown("### Permasalahan & Solusi")
    st.dataframe(
        pd.DataFrame(
            [
                ("Buku dikembalikan rusak", "Petugas mencatat kondisi buku sebelum dan setelah dipinjam; denda kerusakan dihitung otomatis."),
                ("Mahasiswa terlambat mengembalikan", "Sistem menghitung denda Rp1.000 per buku per hari secara otomatis."),
                ("Ingin meminjam lebih dari 2 buku", "Diperlukan izin khusus Kepala Perpustakaan yang dicatat pada transaksi."),
                ("Mahasiswa tidak aktif ingin meminjam", "Sistem memeriksa status keaktifan sebelum transaksi diproses."),
                ("Buku hilang", "Petugas mencatat kehilangan, denda kehilangan diterapkan, stok koleksi dikurangi."),
            ],
            columns=["Permasalahan", "Solusi pada Sistem"],
        ),
        hide_index=True,
        **_DF_WIDTH,
    )

    st.markdown("### Alur Utama Sistem")
    st.markdown(
        """
        1. **Pendaftaran** — anggota memperoleh `ID_Anggota` dan NIM yang unik.
        2. **Peminjaman** — petugas memeriksa status anggota dan stok buku; sistem mencatat tanggal
           pinjam dan menghitung wajib kembali 7 hari kemudian.
        3. **Pengembalian** — sistem menghitung selisih tanggal, denda keterlambatan, dan denda
           kerusakan/kehilangan; stok tersedia diperbarui.
        4. **Pelaporan** — seluruh transaksi dan rekap denda dapat dilihat dan diunduh sebagai CSV.
        """
    )

    st.markdown("### Skema Basis Data (SQLite)")
    st.code(
        """buku(id_buku PK, judul_buku, pengarang, penerbit, tahun_terbit,
      jenis_buku, stok_total, stok_tersedia)

anggota(id_anggota PK, nim UNIQUE, nama_lengkap, nomor_telepon,
        email, program_studi, status_aktif)

peminjaman(id_peminjaman PK, id_anggota FK, id_buku FK,
           tanggal_pinjam, tanggal_wajib_kembali,
           tanggal_realisasi_kembali, kondisi_pinjam, kondisi_kembali,
           denda_keterlambatan, denda_kerusakan, denda_akumulasi,
           status, izin_khusus, catatan)""",
        language="text",
    )

    st.markdown("### Anggota Kelompok 7")
    st.dataframe(
        pd.DataFrame(
            [
                ("09", "Chandra Hernaldi"),
                ("15", "Jauzaa Lubnaa"),
                ("18", "Marahita Aldila S"),
                ("23", "Ranum Darwari"),
                ("28", "Ulung Galih"),
            ],
            columns=["No. Absen", "Nama Anggota"],
        ),
        hide_index=True,
        **_DF_WIDTH,
    )

    st.markdown(
        """
        ### Teknologi
        Aplikasi dibangun dengan **Streamlit** (antarmuka) dan **SQLite** (basis data lokal).
        Tidak diperlukan proses login; aplikasi dijalankan secara lokal oleh petugas perpustakaan.
        """
    )


# ---------------------------------------------------------------------------
# Sidebar & navigasi
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        """
        <div class="brand">
            <div class="brand-icon">📚</div>
            <div>
                <div class="brand-title">Perpustakaan Polines</div>
                <div class="brand-sub">Sistem Sirkulasi</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    nav = st.radio("Navigasi", NAV_ITEMS, key="nav", label_visibility="collapsed")

    st.markdown("---")
    st.markdown('<div class="side-label">Aturan Perpustakaan</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="side-list">
            Masa pinjam <b>7 hari</b><br>
            Maksimal <b>2 buku</b><br>
            Denda <b>Rp1.000</b> / buku / hari<br>
            Peminjam harus <b>aktif</b>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown('<div class="side-label">Kelompok 7</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="side-group">
            Chandra Hernaldi <span>09</span><br>
            Jauzaa Lubnaa <span>15</span><br>
            Marahita Aldila S <span>18</span><br>
            Ranum Darwari <span>23</span><br>
            Ulung Galih <span>28</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown(
        '<div class="sidebar-foot">Streamlit + SQLite · Data tersimpan lokal pada<br>'
        '<b>perpustakaan.db</b></div>',
        unsafe_allow_html=True,
    )

if nav == "Ringkasan":
    halaman_ringkasan()
elif nav == "Koleksi Buku":
    halaman_buku()
elif nav == "Anggota":
    halaman_anggota()
elif nav == "Peminjaman":
    halaman_peminjaman()
elif nav == "Pengembalian":
    halaman_pengembalian()
elif nav == "Laporan & Denda":
    halaman_laporan()
else:
    halaman_tentang()

st.markdown(
    '<div class="app-footer">Sistem Peminjaman & Pengembalian Buku Perpustakaan · '
    'Kelompok 7 · Politeknik Negeri Semarang</div>',
    unsafe_allow_html=True,
)
