<p align="center">
  <img src="assets/logo.png" alt="Universal Paper Downloader Logo" width="160" height="160" />
</p>

<h1 align="center">Universal Paper Downloader</h1>

<p align="center">
  <em>The Scholarly Nexus — Cross-Publisher Academic Paper Downloader</em><br />
  <strong>Built by Hans x Gravi</strong>
</p>

<p align="center">
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python 3.8+" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT" /></a>
  <a href="https://github.com/FongYoong/ieee_journal_downloader"><img src="https://img.shields.io/badge/Derived%20From-FongYoong%2Fieee--journal--downloader-lightgrey.svg" alt="Original Upstream" /></a>
  <a href="#architecture"><img src="https://img.shields.io/badge/Resolver-5--Tier%20Waterfall-brightgreen.svg" alt="Architecture" /></a>
  <a href="#performance--memory"><img src="https://img.shields.io/badge/Memory-Strict%208GB%20Optimized-success.svg" alt="RAM Optimized" /></a>
</p>

> 📌 **Open-Source Attribution:** Berakar dan dikembangkan lebih lanjut dari proyek fondasi [FongYoong/ieee_journal_downloader](https://github.com/FongYoong/ieee_journal_downloader) oleh Fong Chien Yoong, kemudian direarsitektur dan diperluas menjadi pengunduh jurnal universal multi-penerbit oleh **Hans x Gravi**.

**Universal Paper Downloader** adalah aplikasi pengunduh artikel ilmiah dan jurnal akademik serbaguna berbasis terminal (*CLI*) dan satu-klik (*One-Click Launcher*). Mampu mengunduh dokumen ilmiah dari berbagai penerbit internasional ternama (**Nature, Springer, Elsevier / ScienceDirect, Wiley, IEEE, ACM, Taylor & Francis, PubMed, dll.**) secara instan berdasarkan DOI, tautan URL paper, maupun daftar batch.

Aplikasi ini juga mempertahankan kapabilitas khusus untuk mengunduh seluruh artikel pada suatu edisi jurnal IEEE dan menggabungkannya (*sequential merge*) menjadi satu buku PDF utuh.

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

## 🚀 Panduan Penggunaan

Aplikasi ini menyediakan 2 cara penggunaan fleksibel:

### 🌟 Cara 1: Interactive Batch UI Launcher (Rekomendasi - Super Enteng)
Cukup klik ganda berkas **`Universal_Downloader.bat`** atau klik shortcut berlogo **"Universal Paper Downloader"** di **Windows Start Menu**.

Tampilan antarmuka TUI langsung menyajikan menu navigasi lengkap tanpa beban RAM (0 MB overhead):
* **[1]** Unduh Paper Satuan (Otomatis deteksi clipboard / input DOI atau URL).
* **[2]** Unduh 1 Edisi Penuh Jurnal IEEE (Otomatis merge menjadi 1 master PDF).
* **[3]** Unduh Batch (Daftar DOI massal dari berkas `.txt`).
* **[4]** Buka folder penyimpanan hasil unduhan PDF di File Explorer.
* **[5]** Selesai & Keluar.

### 💻 Cara 2: Mode CLI Baris Perintah (Developer / Terminal)
Jalankan langsung melalui PowerShell atau Command Prompt:

#### A. Mode Interaktif Python
```powershell
python universal_downloader.py
```

#### B. Mengunduh via DOI Tunggal
```powershell
# Contoh Nature
python universal_downloader.py "10.1038/s41586-020-2649-2"

# Contoh Elsevier / ScienceDirect
python universal_downloader.py "10.1016/j.cell.2020.08.024"
```

#### C. Mengunduh via URL Halaman Paper
```powershell
python universal_downloader.py "https://www.nature.com/articles/s41586-020-2649-2"
```

#### D. Mengunduh Banyak Paper Sekaligus (Batch Mode)
Buat berkas teks (misal `daftar_paper.txt`) berisi satu DOI/URL per baris, lalu jalankan:
```powershell
python universal_downloader.py --file daftar_paper.txt
```

#### E. Mengunduh 1 Edisi Jurnal IEEE Penuh (Merged PDF)
```powershell
python universal_downloader.py "https://ieeexplore.ieee.org/xpl/tocresult.jsp?isnumber=9340528&punumber=8475037"
```

---

## 📂 Struktur Direktori Output

Semua hasil unduhan disimpan secara terstruktur di folder `pdf_output/`:

```
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

## 🛠 Instalasi Dependensi

Pastikan Python 3.8+ telah terpasang, lalu instal paket yang dibutuhkan:

```powershell
pip install requests beautifulsoup4 pypdf pyperclip fake-useragent
```

---

## 🤝 Kolaborasi & Kredit

* **Arsitektur & Pengembangan Lanjutan:** **Hans x Gravi**
* **Inspirasi & Upstream Engine Awal:** Menggunakan fondasi mesin IEEE issue downloader dari [FongYoong/ieee_journal_downloader](https://github.com/FongYoong/ieee_journal_downloader).