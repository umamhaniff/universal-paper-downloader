# Universal Paper Downloader Architecture

Built by **Hans x Gravi**

## Project Overview
Proyek ini berevolusi dari sekadar pengunduh jurnal IEEE menjadi **Universal Paper Downloader** dengan arsitektur *Waterfall Cascade Resolution*. Mampu mengunduh dokumen ilmiah dari penerbit mana pun (Nature, Springer, Elsevier, IEEE, Wiley, ACM, dll.) berdasarkan nomor DOI atau tautan URL, sekaligus mengunduh seluruh volume/edisi jurnal IEEE dan menggabungkannya ke dalam satu PDF master.

## Core Engines
1. **Universal DOI & Paper Downloader:** [universal_downloader.py](file:///D:/_CampusLife/ProjectLikely/ieee_journal_downloader/universal_downloader.py)
   - **Input:** DOI apa saja (`10.xxxx/...`), tautan paper dari berbagai publisher, atau tautan issue IEEE.
   - **Cascade Pipeline:**
     - **Tier 1:** Unpaywall API (Legal Open Access & Author Manuscripts)
     - **Tier 2:** OpenAlex Global Scholarly Index (OA URLs & Publisher Direct)
     - **Tier 3:** Semantic Scholar API (Open Access PDFs)
     - **Tier 4:** IEEE Open Access Stamp Resolver
     - **Tier 5:** Sci-Hub Multi-Mirror (`.ru`, `.st`, `.se`) untuk paper terkunci paywall
   - **Fitur Batch:** Mendukung argumen `--file dois.txt` untuk mengunduh daftar paper sekaligus.
2. **IEEE Issue Engine:** [ieee_downloader.py](file:///D:/_CampusLife/ProjectLikely/ieee_journal_downloader/ieee_downloader.py)
   - Spesialisasi mengunduh seluruh artikel pada edisi/isu jurnal IEEE (`isnumber` & `punumber`) dan menggabungkannya secara sequential ke dalam PDF master (`Volume_X_Issue_Y.pdf`).

## RAM & Performance Optimization (Strict 8GB RAM Constraint)
- Streaming via `requests.get(..., stream=True)` dengan chunk 64KB langsung ke disk.
- Verifikasi magic bytes `%PDF` di header tiap file.
- Penggabungan PDF dilakukan secara sequential menggunakan `pypdf.PdfWriter` tanpa *memory footprint* berlebih.

## Output Directory Structure
```
pdf_output/
├── Universal_Downloads/
│   └── {Journal_or_Publisher_Name}/
│       └── {Safe_Article_Title}.pdf
├── Single_Articles/
│   └── {Publication_Title}/
│       └── {Safe_Title}.pdf
└── {Publication_Title}/
    └── Volume_{Vol}_Issue_{Issue}/
        ├── Volume_{Vol}_Issue_{Issue}.pdf  <-- Master Merged PDF
        ├── error_log.txt                   <-- Failed items (if any)
        └── separate/
            ├── 01_{Safe_Title}.pdf
            └── 02_{Safe_Title}.pdf
```

## Quick Usage Guide
```powershell
# --- UNIVERSAL DOWNLOADER (SEMUA JURNAL & PUBLISHER) ---
# 1. Mode Interaktif (bisa paste clipboard):
python universal_downloader.py

# 2. Unduh via DOI (Nature, Elsevier, Springer, IEEE, dll):
python universal_downloader.py "10.1038/s41586-020-2649-2"

# 3. Unduh via URL paper:
python universal_downloader.py "https://www.nature.com/articles/s41586-020-2649-2"

# 4. Unduh banyak DOI sekaligus dari file teks:
python universal_downloader.py --file daftar_doi.txt

# --- ONE-CLICK LAUNCHER & START MENU ---
# Klik shortcut "Universal Paper Downloader" di Windows Start Menu
# Atau jalankan batch file:
./run_downloader.bat
```

## Git & Repository Status
- **Origin (Personal):** Siap diarahkan ke akun GitHub pribadi Hans saat hendak di-push.
- **Upstream (Read-Only Mirror):** `https://github.com/FongYoong/ieee_journal_downloader.git` (khusus memantau update dari pembuat asli tanpa merusak kode lokal).
