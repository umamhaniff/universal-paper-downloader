<p align="center">
  <img src="assets/logo.png" alt="Universal Paper Downloader Logo" width="160" height="160" />
</p>

<h1 align="center">Universal Paper Downloader</h1>

<p align="center">
  <em>The Scholarly Nexus — High-Performance Cross-Publisher Academic Paper Downloader</em><br />
  <strong>Built by Hans x Gravi</strong>
</p>

<p align="center">
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python 3.8+" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT" /></a>
  <a href="https://github.com/FongYoong/ieee_journal_downloader"><img src="https://img.shields.io/badge/Derived%20From-FongYoong%2Fieee--journal--downloader-lightgrey.svg" alt="Original Upstream" /></a>
  <a href="#-arsitektur-resolusi-5-tier-waterfall"><img src="https://img.shields.io/badge/Resolver-5--Tier%20Waterfall-brightgreen.svg" alt="Architecture" /></a>
  <a href="#-optimasi-memori--ram-strict-8gb"><img src="https://img.shields.io/badge/Memory-Strict%208GB%20Optimized-success.svg" alt="RAM Optimized" /></a>
</p>

> 📌 **Open-Source Attribution:** Berakar dan dikembangkan lebih lanjut dari proyek fondasi [FongYoong/ieee_journal_downloader](https://github.com/FongYoong/ieee_journal_downloader) oleh Fong Chien Yoong, kemudian direarsitektur dan diperluas menjadi pengunduh jurnal universal multi-penerbit oleh **Hans x Gravi**.

**Universal Paper Downloader** adalah aplikasi pengunduh artikel ilmiah dan jurnal akademik serbaguna berbasis antarmuka grafis terminal ringan (*Interactive Batch TUI*) serta baris perintah (*CLI*). Mampu mengunduh dokumen ilmiah dari berbagai penerbit internasional ternama (**Nature, Springer, Elsevier / ScienceDirect, Wiley, IEEE, ACM, Taylor & Francis, PubMed, dll.**) secara instan berdasarkan DOI, tautan URL paper, maupun daftar batch.

Aplikasi ini juga mempertahankan kapabilitas khusus untuk mengunduh seluruh artikel pada suatu edisi jurnal IEEE dan menggabungkannya (*sequential merge*) menjadi satu buku PDF master.

---

## ⚡ Fitur Utama

* **🌍 Universal Cross-Publisher Support:** Bekerja untuk hampir seluruh penerbit ilmiah dunia via DOI atau URL paper.
* **🌊 5-Tier Waterfall Cascade Resolution:**
  1. **Tier 1 — Unpaywall API:** Mengakses preprint legal dan author accepted manuscripts.
  2. **Tier 2 — OpenAlex Global Index:** Repositori pustaka akademik dunia dengan direct OA link.
  3. **Tier 3 — Semantic Scholar API:** Pencarian Open Access direct PDF endpoints.
  4. **Tier 4 — IEEE OA Stamp Resolver:** Penanganan khusus berkas Open Access dari IEEE Xplore.
  5. **Tier 5 — Sci-Hub Multi-Mirror:** Otomatis mem-bypass paywall jurnal berbayar melalui cermin mirror aktif (`.ru`, `.st`, `.se`).
* **📋 Multi-Input Fleksibel:**
  * Mode Interaktif: Cukup jalankan program dan tekan Enter untuk membaca link/DOI dari clipboard.
  * Argumen Baris Perintah: Oper DOI atau URL langsung di terminal.
  * Batch Processing: Dukungan argumen `--file daftar_doi.txt` untuk mengunduh puluhan paper sekaligus secara berurutan.
* **📚 IEEE Issue Master Merger:** Mengunduh 1 issue/edisi IEEE lengkap dan menyatukannya menjadi satu master PDF.
* **💾 Memory & RAM Efficient (Strict 8GB Optimization):**
  * Unduhan berbasis chunk streaming (64KB) langsung ke disk tanpa menimbun di RAM.
  * Validasi magic bytes `%PDF` pada header berkas sebelum disimpan.
  * Penggabungan PDF bertahap tanpa memory footprint berlebih.

---

## 🛠 Panduan Instalasi (Step-by-Step)

### 1. Prasyarat Sistem
Pastikan perangkat Anda sudah terpasang:
* **Python 3.8 atau lebih baru** ([Unduh Python](https://www.python.org/downloads/)). *Pastikan centang "Add python.exe to PATH" saat instalasi.*
* **Git** (Opsional, untuk clone repositori).

### 2. Unduh / Clone Repositori
Buka terminal (PowerShell atau Command Prompt), lalu jalankan:
```powershell
git clone https://github.com/umamhaniff/universal-paper-downloader.git
cd universal-paper-downloader
```

### 3. Instal Dependensi Python
Instal seluruh paket pustaka yang dibutuhkan hanya dengan satu perintah:
```powershell
pip install -r requirements.txt
```

### 4. Pasang Shortcut Windows Start Menu (Opsional / 1-Klik)
Untuk memasang pintasan aplikasi berlogo resmi 3D Hardcover Tome di Windows Start Menu:
* Klik ganda berkas **`install_shortcut.bat`**, atau
* Jalankan di terminal:
  ```powershell
  ./install_shortcut.bat
  ```
Setelah ini, Anda cukup menekan tombol **Windows** di keyboard lalu ketik **"Universal Paper Downloader"** untuk membuka aplikasi kapan saja!

---

## 🚀 Panduan Penggunaan

Aplikasi ini menyediakan **2 cara penggunaan** sesuai kenyamanan Anda:

### 🌟 Cara 1: Interactive Batch UI Launcher (Rekomendasi - Super Enteng)
Cukup klik ganda berkas **`Universal_Downloader.bat`** atau klik shortcut di **Windows Start Menu**.

Tampilan antarmuka TUI langsung menyajikan menu navigasi lengkap tanpa beban RAM (0 MB overhead):
```text
======================================================================
             UNIVERSAL PAPER DOWNLOADER (Hans x Gravi)                
======================================================================
  Engine: 5-Tier Waterfall | Cross-Publisher | Strict 8GB RAM Optimized
======================================================================

  [1] Unduh Paper Satuan (DOI / URL Nature, ScienceDirect, IEEE, dll)
  [2] Unduh 1 Edisi Jurnal Penuh IEEE (Auto-Merge Master PDF)
  [3] Unduh Batch (Banyak DOI sekaligus dari file teks)
  [4] Buka Folder Penyimpanan PDF (File Explorer)
  [5] Keluar

======================================================================
Pilih menu (1-5) [Default: 1] > 
```

* **Pilih [1]:** Cukup paste nomor DOI atau link URL artikel. Program juga secara otomatis mendeteksi jika Anda baru saja menyalin DOI ke clipboard!
* **Pilih [2]:** Masukkan link edisi IEEE (misal halaman Table of Contents issue IEEE) untuk mengunduh seluruh volume dan menggabungkannya ke 1 PDF.
* **Pilih [3]:** Masukkan path file teks (misal `daftar_doi.txt`) untuk mengunduh puluhan paper secara otomatis.
* **Pilih [4]:** Membuka folder output PDF langsung di Windows File Explorer.
* **Pilih [5]:** Menutup program secara aman.

---

### 💻 Cara 2: Mode CLI Baris Perintah (Developer / Terminal)
Bagi pengguna terminal, Anda dapat memanggil mesin Python secara langsung dengan parameter baris perintah:

#### A. Mode Interaktif CLI
```powershell
python universal_downloader.py
```

#### B. Mengunduh via DOI Tunggal
```powershell
# Contoh Artikel Nature
python universal_downloader.py "10.1038/s41586-020-2649-2"

# Contoh Artikel Elsevier / ScienceDirect
python universal_downloader.py "10.1016/j.cell.2020.08.024"

# Contoh Artikel IEEE
python universal_downloader.py "10.1109/TPAMI.2020.3012548"
```

#### C. Mengunduh via URL Halaman Paper
Salin URL langsung dari bilah alamat browser:
```powershell
python universal_downloader.py "https://www.nature.com/articles/s41586-020-2649-2"
```

#### D. Mengunduh Batch dari Berkas Teks
Buat berkas teks (misal `daftar_paper.txt`) berisi satu DOI/URL per baris, lalu jalankan:
```powershell
python universal_downloader.py --file daftar_paper.txt
```

#### E. Mengunduh 1 Edisi Jurnal IEEE Penuh (Merged Master PDF)
```powershell
python universal_downloader.py "https://ieeexplore.ieee.org/xpl/tocresult.jsp?isnumber=9340528&punumber=8475037"
```

---

## 📂 Struktur Direktori Output

Semua hasil unduhan disimpan secara terstruktur dan rapi di dalam direktori `pdf_output/`:

```text
pdf_output/
├── Universal_Downloads/
│   └── {Publisher_or_Journal_Name}/
│       └── {Safe_Article_Title}.pdf
├── Single_Articles/
│   └── {Publication_Title}/
│       └── {Safe_Title}.pdf
└── {Publication_Title}/
    └── Volume_{Vol}_Issue_{Issue}/
        ├── Volume_{Vol}_Issue_{Issue}.pdf   <-- Master Merged PDF
        ├── error_log.txt                    <-- Log kegagalan (jika ada)
        └── separate/
            ├── 01_{Safe_Title}.pdf
            └── 02_{Safe_Title}.pdf
```

---

## 🌊 Arsitektur Resolusi 5-Tier Waterfall

```text
Target DOI / URL
       │
       ▼
[Tier 1: Unpaywall API] ──────────► [Ditemukan?] ──► [Download PDF OA]
       │ (Tidak)
       ▼
[Tier 2: OpenAlex Global Index] ──► [Ditemukan?] ──► [Download Direct OA]
       │ (Tidak)
       ▼
[Tier 3: Semantic Scholar API] ───► [Ditemukan?] ──► [Download PDF OA]
       │ (Tidak)
       ▼
[Tier 4: IEEE Stamp Resolver] ────► [Ditemukan?] ──► [Download IEEE OA]
       │ (Tidak)
       ▼
[Tier 5: Sci-Hub Multi-Mirror] ───► [Ditemukan?] ──► [Download Paywall Bypass]
       │ (Tidak)
       ▼
[Hasil: Panduan Legal Request via ResearchGate / SSO Kampus]
```

---

## 💾 Optimasi Memori & RAM (Strict 8GB)
* **Streaming Chunks:** Pengunduhan file tidak pernah memuat seluruh berkas PDF ke dalam RAM sekaligus, melainkan dialirkan per chunk 64KB langsung ke disk (`requests.get(..., stream=True)`).
* **Verifikasi Magic Bytes:** Header berkas divalidasi memastikan berawalan byte `%PDF` sebelum disimpan permanen.
* **Sequential Merger:** Penggabungan issue PDF multi-artikel menggunakan alur sekuensial hemat memori.

---

## 🤝 Kolaborasi & Kredit

* **Arsitektur & Pengembangan Lanjutan:** **Hans x Gravi**
* **Inspirasi & Upstream Engine Awal:** Menggunakan fondasi mesin IEEE issue downloader dari [FongYoong/ieee_journal_downloader](https://github.com/FongYoong/ieee_journal_downloader) oleh Fong Chien Yoong.
* **Lisensi:** [MIT License](LICENSE)