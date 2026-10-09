# Universal Paper Downloader Architecture

Built by **Hans x Gravi**

## Project Overview
Proyek ini berevolusi dari sekadar pengunduh jurnal IEEE menjadi **Universal Paper Downloader** dengan arsitektur *Waterfall Cascade Resolution*. Mampu mengunduh dokumen ilmiah dari penerbit mana pun (**Nature, Springer, Elsevier / ScienceDirect, IEEE, Wiley, ACM, Taylor & Francis, PubMed, dll.**) berdasarkan nomor DOI atau tautan URL, sekaligus mengunduh seluruh volume/edisi jurnal IEEE dan menggabungkannya ke dalam satu PDF master.

## Core Engines & Runtime
1. **Universal DOI & Paper Downloader:** [universal_downloader.py](file:///D:/_CampusLife/ProjectLikely/universal_paper_downloader/universal_downloader.py)
   - **Standar Eksekusi:** Didukung penuh oleh **Astral `uv`** via standar **PEP 723 (Inline Script Metadata)**.
   - **Input:** DOI apa saja (`10.xxxx/...`), tautan paper dari berbagai publisher, tautan issue IEEE, atau mode batch teks.
   - **Cascade Pipeline:**
     - **Tier 1:** Unpaywall API (Legal Open Access & Author Manuscripts)
     - **Tier 2:** OpenAlex Global Scholarly Index (OA URLs & Publisher Direct)
     - **Tier 3:** Semantic Scholar API (Open Access PDFs)
     - **Tier 4:** IEEE Open Access Stamp Resolver
     - **Tier 5:** Sci-Hub Multi-Mirror (`.ru`, `.su`, `.wf`, `.ren`, `.st`) dengan **In-App Encrypted DoH (1.1.1.1 / 8.8.8.8)** bypass untuk sensor ISP tanpa modifikasi OS.
   - **Anti-Censorship & Future-Proofing:** In-App DoH socket fallback otomatis saat ISP memblokir domain mirror, serta dukungan konfigurasi pool mirror dinamis via environment variable (`SCIHUB_MIRRORS`).
   - **Visual Output Pipeline:** Memiliki pembatas kotak visual terpisah (Metadata $\rightarrow$ Cascade Check $\rightarrow$ Disk Streaming Chunk $\rightarrow$ Hasil Akhir) serta menu tindakan interaktif pasca-unduh agar sesi tidak tertutup sepihak.
2. **IEEE Issue Engine:** [ieee_downloader.py](file:///D:/_CampusLife/ProjectLikely/universal_paper_downloader/ieee_downloader.py)
   - Spesialisasi mengunduh seluruh artikel pada edisi/isu jurnal IEEE (`isnumber` & `punumber`) dan menggabungkannya secara sequential ke dalam PDF master (`Volume_X_Issue_Y.pdf`).

## UI & Pemasangan
- **Interactive Batch TUI Launcher:** [`Universal_Downloader.bat`](file:///D:/_CampusLife/ProjectLikely/universal_paper_downloader/Universal_Downloader.bat)
  - Otomatis mendeteksi keberadaan `uv` (Astral Rust Runner) untuk eksekusi kilat (~200ms) dengan fallback ke `python`.
  - RAM overhead 0 MB (ideal untuk limit memori 8GB).
- **Shortcut Installer 1-Klik:** [`install_shortcut.bat`](file:///D:/_CampusLife/ProjectLikely/universal_paper_downloader/install_shortcut.bat)
  - Memasang pintasan berlogo resmi di Windows Start Menu.
- **Aset & Identitas Visual:** Folder [`assets/`](file:///D:/_CampusLife/ProjectLikely/universal_paper_downloader/assets/)
  - `logo.png`: High-res 512x512 PNG 3D Hardcover Academic Tome.
  - `app_icon.ico`: Multi-resolusi (256 s/d 16 px) untuk icon Windows.
  - `generate_icon.py`: Generator aset visual matematis berbasis Pillow.


## RAM & Performance Optimization (Strict 8GB RAM Constraint)
- Streaming via `requests.get(..., stream=True)` dengan chunk 64KB langsung ke disk tanpa penumpukan memori.
- Verifikasi magic bytes `%PDF` di header tiap file sebelum penyimpanan permanen.
- Penggabungan PDF dilakukan secara sequential menggunakan `pypdf.PdfWriter`.

## Root Directory Layout (Sanitized & Clean)
```text
universal-paper-downloader/
├── assets/                     <-- Logo PNG, icon ICO, & generator script
├── pdf_output/                 <-- Folder penyimpanan berkas PDF unduhan
├── legacy_rust/                <-- Arsip kode Rust 2021 (terisolasi rapi)
├── .gitignore                  <-- Rule pengabaian file sementara & cache
├── LICENSE                     <-- Lisensi resmi MIT (FongYoong & Hans x Gravi)
├── README.md                   <-- Panduan lengkap step-by-step & dokumentasi uv
├── gemini.md                   <-- Dokumentasi arsitektur & persisten memori
├── requirements.txt            <-- Daftar dependensi uv / pip
├── Universal_Downloader.bat    <-- UI Launcher Utama (Auto-detect uv)
├── install_shortcut.bat        <-- Pemasang shortcut Start Menu 1-klik
├── universal_downloader.py     <-- Mesin Universal (PEP 723 uv)
└── ieee_downloader.py          <-- Mesin IEEE Issue Merger
```

## Quick Usage Guide
```powershell
# --- CARA 1: INTERACTIVE BATCH UI LAUNCHER (SUPER ENTENG) ---
# Jalankan file batch UI atau klik shortcut berlogo di Windows Start Menu:
./Universal_Downloader.bat

# --- CARA 2: EKSEKUSI MODERN VIA UV (RECOMMENDED) ---
uv run universal_downloader.py
uv run universal_downloader.py "10.1038/s41586-020-2649-2"
uv run universal_downloader.py --file daftar_doi.txt

# --- CARA 3: CLI PYTHON STANDAR ---
python universal_downloader.py "10.1038/s41586-020-2649-2"
```

## Git & Repository Status
- **Origin (Personal GitHub):** `https://github.com/umamhaniff/universal-paper-downloader.git` (Tracking `master`)
- **Upstream (Read-Only Mirror):** `https://github.com/FongYoong/ieee_journal_downloader.git` (Sumber fondasi awal)
