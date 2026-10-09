"""
IEEE Journal & Article Downloader - Python Modern Port
Built by Hans x Gravi

A high-performance, memory-efficient IEEE scraper and PDF compiler.
Supports:
1. Full Journal / Conference Issue downloads (via TOC link) with automatic PDF merge.
2. Single Article downloads (via /document/arnumber link) with direct IEEE open-access
   and multi-mirror Sci-Hub resolution.
"""
# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "requests>=2.28.0",
#     "beautifulsoup4>=4.11.0",
#     "pypdf>=3.0.0",
#     "tqdm>=4.64.0",
# ]
# ///

import os


import sys
import re
import time
import json
import argparse
from urllib.parse import urlparse, parse_qs
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from pypdf import PdfWriter
from tqdm import tqdm

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

SCIHUB_MIRRORS = [
    "https://sci-hub.ru",
    "https://sci-hub.st",
    "https://sci-hub.se",
]


class IEEEDownloader:
    def __init__(self, session: requests.Session | None = None, delay: float = 1.5):
        self.session = session or requests.Session()
        self.session.headers.update({
            "User-Agent": DEFAULT_USER_AGENT,
            "Accept-Language": "en-US,en;q=0.9",
        })
        self.delay = delay
        self._session_warmed_up = False
        self._universal = None

    def get_universal_engine(self):
        """Lazy-loads the UniversalDownloader with full 5-tier cascade, DoH, and multi-mirror pool."""
        if self._universal is None:
            from universal_downloader import UniversalDownloader
            self._universal = UniversalDownloader(delay=self.delay)
        return self._universal

    @staticmethod
    def to_long_path_safe(path: Path) -> Path:
        """Converts path to extended-length format on Windows if needed to bypass MAX_PATH limit."""
        resolved = path.resolve()
        if os.name == "nt" and not str(resolved).startswith("\\\\?\\"):
            return Path(f"\\\\?\\{resolved}")
        return resolved

    def warm_up_session(self):
        """Initializes cookies by hitting IEEE home once."""
        if not self._session_warmed_up:
            try:
                self.session.get("https://ieeexplore.ieee.org/", timeout=10)
                self._session_warmed_up = True
            except Exception:
                pass

    def sanitize_filename(self, name: str, max_length: int = 80) -> str:
        """Sanitizes names for Windows/Linux file paths, keeping length bounded."""
        clean = re.sub(r'[\\/*?:"<>|]', "_", name).strip()
        return clean[:max_length].strip()

    def parse_journal_url(self, url: str) -> tuple[str, str]:
        """
        Extracts (punumber, isnumber) from IEEE issue URL.
        If punumber is missing, fetches it using the issue metadata endpoint.
        """
        parsed = urlparse(url)
        params = parse_qs(parsed.query)

        isnumber = params.get("isnumber", [None])[0]
        punumber = params.get("punumber", [None])[0]

        if not isnumber:
            match = re.search(r"issue/(\d+)", parsed.path)
            if match:
                isnumber = match.group(1)

        if not isnumber:
            raise ValueError(
                f"Could not identify 'isnumber' (Issue Number) from link: {url}\n"
                f"Tip: If you're trying to download a single article, use an IEEE /document/<arnumber> link."
            )

        if not punumber:
            print(f"[*] 'punumber' not in URL, querying IEEE metadata for issueid={isnumber}...")
            punumber = self.fetch_punumber_by_issue(isnumber)

        return punumber, isnumber

    def fetch_punumber_by_issue(self, isnumber: str) -> str:
        """Resolves punumber (Publication Number) from isnumber."""
        meta_url = f"https://ieeexplore.ieee.org/rest/publication/home/metadata?issueid={isnumber}"
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "Host": "ieeexplore.ieee.org",
            "Origin": "https://ieeexplore.ieee.org",
        }
        res = self.session.get(meta_url, headers=headers, timeout=15)
        res.raise_for_status()
        data = res.json()
        punumber = str(data.get("publicationNumber", ""))
        if not punumber:
            raise RuntimeError(f"Failed to resolve publicationNumber from {meta_url}")
        return punumber

    def get_table_of_contents(self, punumber: str, isnumber: str, original_url: str) -> dict:
        """Fetches the Table of Contents JSON records for the target issue."""
        toc_url = f"https://ieeexplore.ieee.org/rest/search/pub/{punumber}/issue/{isnumber}/toc"
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "Host": "ieeexplore.ieee.org",
            "Origin": "https://ieeexplore.ieee.org",
            "Referer": original_url,
        }
        payload = {
            "isnumber": str(isnumber),
            "punumber": str(punumber),
            "sortType": "vol-only-seq",
        }
        res = self.session.post(toc_url, json=payload, headers=headers, timeout=20)
        res.raise_for_status()
        return res.json()

    def fetch_document_metadata(self, arnumber: str) -> dict:
        """Fetches metadata for a single article document."""
        self.warm_up_session()
        doc_url = f"https://ieeexplore.ieee.org/document/{arnumber}"
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Referer": "https://ieeexplore.ieee.org/",
        }
        res = self.session.get(doc_url, headers=headers, timeout=15)
        if res.status_code != 200:
            raise RuntimeError(f"Failed to access document page {doc_url} (HTTP {res.status_code})")

        match = re.search(r'xplGlobal\.document\.metadata\s*=\s*(\{.*?\});\s*</script>', res.text, re.DOTALL)
        if not match:
            raise RuntimeError(f"Could not extract metadata from {doc_url}")

        return json.loads(match.group(1))

    def resolve_ieee_pdf_stream(self, pdf_link: str) -> str | None:
        """Resolves direct PDF URL from IEEE stamp page iframe."""
        stamp_url = f"https://ieeexplore.ieee.org{pdf_link}"
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Referer": "https://ieeexplore.ieee.org/",
        }
        try:
            res = self.session.get(stamp_url, headers=headers, timeout=15)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, "html.parser")
                iframe = soup.find("iframe")
                if iframe and iframe.get("src"):
                    return iframe.get("src")
        except Exception as e:
            print(f"[!] Error resolving IEEE stamp link {stamp_url}: {e}")
        return None

    def resolve_scihub_pdf_stream(self, doi: str) -> tuple[str | None, str | None]:
        """
        Attempts to resolve PDF stream URL across Sci-Hub mirrors with In-App DoH bypass.
        Returns (pdf_url, referer_used).
        """
        engine = self.get_universal_engine()
        src, _, referer = engine.resolve_scihub(doi)
        if src:
            return src, referer
        return None, None

    def stream_download(self, url: str, dest_path: Path, referer: str | None = None) -> bool:
        """
        Streams PDF content directly to disk in chunks to adhere to 8GB RAM constraints.
        Validates PDF header (%PDF). Supports Windows extended long paths.
        """
        headers = {}
        if referer:
            headers["Referer"] = referer

        safe_dest = self.to_long_path_safe(dest_path)
        safe_dest.parent.mkdir(parents=True, exist_ok=True)

        try:
            with self.session.get(url, headers=headers, stream=True, timeout=30) as r:
                if r.status_code != 200:
                    return False

                chunk_gen = r.iter_content(chunk_size=65536)
                first_chunk = next(chunk_gen, None)
                if not first_chunk or not first_chunk.startswith(b"%PDF"):
                    return False

                with open(safe_dest, "wb") as f:
                    f.write(first_chunk)
                    for chunk in chunk_gen:
                        if chunk:
                            f.write(chunk)
            return True
        except Exception as e:
            if safe_dest.exists():
                try:
                    safe_dest.unlink()
                except OSError:
                    pass
            return False

    def process_single_document(self, url: str, arnumber: str, output_base: str = "pdf_output") -> None:
        """Handles downloading a single IEEE article/paper."""
        print("=" * 65)
        print(" IEEE ARTICLE DOWNLOADER (Single Document Mode) ")
        print("=" * 65)
        print(f"[*] Document URL:   {url}")
        print(f"[*] Article Number: {arnumber}")
        print("[*] Fetching article metadata...")

        try:
            metadata = self.fetch_document_metadata(arnumber)
        except Exception as e:
            print(f"[!] Error fetching document metadata: {e}")
            return

        title = metadata.get("title") or f"Article_{arnumber}"
        doi = metadata.get("doi") or ""
        authors = [a.get("name") for a in metadata.get("authors", []) if a.get("name")]
        pub_title = metadata.get("publicationTitle") or "IEEE_Publication"
        pdf_url = metadata.get("pdfUrl") or f"/stamp/stamp.jsp?tp=&arnumber={arnumber}"
        is_oa = metadata.get("isOpenAccess", False) or metadata.get("ephemera", False)
        is_conf = metadata.get("isConference", False)
        is_journal = metadata.get("isJournal", False)
        issue_number = metadata.get("issueNumber") or metadata.get("issue")
        punumber = metadata.get("punumber")

        safe_pub_title = self.sanitize_filename(pub_title, max_length=60)
        safe_title = self.sanitize_filename(title, max_length=80)

        print(f"\n[*] Title:       {title}")
        if authors:
            print(f"[*] Authors:     {', '.join(authors[:5])}")
        print(f"[*] Publication: {pub_title}")
        print(f"[*] DOI:         {doi}")
        print(f"[*] Type:        {'Conference Paper' if is_conf else 'Journal Article' if is_journal else 'Publication'}")
        print(f"[*] Open Access: {'Yes (Freely Available)' if is_oa else 'No (Locked / Subscription Required)'}\n")

        dest_dir = Path(output_base) / "Single_Articles" / safe_pub_title
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_file = dest_dir / f"{safe_title}.pdf"

        safe_dest_check = self.to_long_path_safe(dest_file)
        if safe_dest_check.exists() and safe_dest_check.stat().st_size > 1024:
            print(f"[+] File already exists: {dest_file.resolve()}")
            print("=" * 65)
            return

        success = False
        # 1. Direct IEEE access if Open Access / Ephemera
        if is_oa and pdf_url:
            print("[*] Attempting direct IEEE Open-Access download...")
            stream_url = self.resolve_ieee_pdf_stream(pdf_url)
            if stream_url:
                success = self.stream_download(stream_url, dest_file, referer="https://ieeexplore.ieee.org/")

        # 2. Universal Waterfall Cascade fallback if locked
        if not success and doi:
            print(f"[*] Resolving locked paper via Universal Engine & Sci-Hub DoH (DOI: {doi})...")
            engine = self.get_universal_engine()
            oa_url, _ = engine.resolve_unpaywall(doi)
            if oa_url and engine.stream_download(oa_url, dest_file):
                success = True
            if not success:
                oa_url, _ = engine.resolve_openalex(doi)
                if oa_url and engine.stream_download(oa_url, dest_file):
                    success = True
            if not success:
                oa_url, _ = engine.resolve_semanticscholar(doi)
                if oa_url and engine.stream_download(oa_url, dest_file):
                    success = True
            if not success:
                scihub_src = engine.download_from_scihub_cascade(doi, dest_file)
                if scihub_src:
                    success = True

        if success:
            print(f"\n[OK] Document successfully downloaded!")
            print(f"     File: {dest_file.resolve()}")
            print(f"     Size: {dest_file.stat().st_size // 1024} KB")
        else:
            print(f"\n[-] Could not automatically download PDF.")
            if not is_oa:
                print(f"[!] Catatan Penting:")
                print(f"    Paper ini terkunci di balik paywall resmi IEEE (Bukan Open Access).")
                print(f"    Karena terbitan sangat baru (2024-2026), paper belum terarsip di mirror Sci-Hub.")
                print(f"    Silakan akses melalui akun/SSO kampus/institusi atau kontak author di ResearchGate:")
                print(f"    -> IEEE Link: https://ieeexplore.ieee.org/document/{arnumber}")
                print(f"    -> DOI Link:  https://doi.org/{doi}")

        if issue_number and punumber:
            print(f"\n[i] Info Issue:")
            print(f"    Paper ini merupakan bagian dari Issue ID: {issue_number}, Pub ID: {punumber}")
            print(f"    Untuk mengunduh seluruh isu jurnal/konferensi tersebut:")
            print(f"    python ieee_downloader.py \"https://ieeexplore.ieee.org/xpl/tocresult.jsp?isnumber={issue_number}&punumber={punumber}\"")

        print("=" * 65)

    def process_issue(self, url: str, output_base: str = "pdf_output", limit: int | None = None) -> None:
        """Main orchestrator for downloading issue articles and compiling the master PDF."""
        print("=" * 65)
        print(" IEEE JOURNAL DOWNLOADER (Hans x Gravi Python Engine) ")
        print("=" * 65)
        print(f"[*] Target URL: {url}")

        punumber, isnumber = self.parse_journal_url(url)
        print(f"[*] Publication Number: {punumber}")
        print(f"[*] Issue Number:       {isnumber}")

        print("[*] Fetching Table of Contents...")
        toc_data = self.get_table_of_contents(punumber, isnumber, url)
        records = toc_data.get("records", [])

        if not records:
            print("[!] No records found for this journal issue. Please verify the link.")
            return

        if limit and limit > 0:
            print(f"[*] Limiting download to first {limit} record(s) as requested.")
            records = records[:limit]

        sample_record = records[0]
        pub_title = sample_record.get("publicationTitle") or sample_record.get("displayPublicationTitle") or "IEEE_Publication"
        volume = sample_record.get("volume") or "UnknownVol"
        issue = sample_record.get("issue") or "UnknownIssue"

        safe_pub_title = self.sanitize_filename(pub_title)
        safe_issue_folder = self.sanitize_filename(f"Volume_{volume}_Issue_{issue}")

        issue_dir = Path(output_base) / safe_pub_title / safe_issue_folder
        separate_dir = issue_dir / "separate"
        separate_dir.mkdir(parents=True, exist_ok=True)

        error_log_path = issue_dir / "error_log.txt"
        with open(error_log_path, "w", encoding="utf-8") as f:
            f.write(f"IEEE Journal Downloader Error Log\nIssue: {safe_issue_folder}\nURL: {url}\n\n")

        print(f"[*] Publication: {pub_title}")
        print(f"[*] Volume:      {volume} | Issue: {issue}")
        print(f"[*] Total Items: {len(records)}")
        print(f"[*] Save Dir:    {issue_dir.resolve()}\n")

        downloaded_files: list[Path] = []
        failed_records: list[dict] = []

        for index, record in enumerate(records, start=1):
            title = record.get("articleTitle") or f"Article_{index}"
            doi = record.get("doi") or ""
            access_type_data = record.get("accessType", {})
            access_type = access_type_data.get("type", "locked") if isinstance(access_type_data, dict) else "locked"
            pdf_link = record.get("pdfLink", "")
            arnumber = record.get("articleNumber", "")

            safe_title = self.sanitize_filename(title)[:70]
            filename = f"{index:02d}_{safe_title}.pdf"
            dest_file = separate_dir / filename

            print(f"[{index}/{len(records)}] {title[:60]}... ({access_type})")

            # Check if file already exists from previous run
            if dest_file.exists() and dest_file.stat().st_size > 1024:
                print(f"    -> Already downloaded: {filename}")
                downloaded_files.append(dest_file)
                continue

            success = False
            # 1. Direct IEEE access for open-access or ephemera
            if access_type in ["ephemera", "open-access"] and pdf_link:
                stream_url = self.resolve_ieee_pdf_stream(pdf_link)
                if stream_url:
                    success = self.stream_download(stream_url, dest_file, referer="https://ieeexplore.ieee.org/")

            # 2. Universal Waterfall Cascade fallback for locked or failed direct access
            if not success and doi:
                print(f"    -> Resolving DOI ({doi}) via Universal Engine & Sci-Hub DoH...")
                engine = self.get_universal_engine()
                oa_url, _ = engine.resolve_unpaywall(doi)
                if oa_url and engine.stream_download(oa_url, dest_file):
                    success = True
                if not success:
                    oa_url, _ = engine.resolve_openalex(doi)
                    if oa_url and engine.stream_download(oa_url, dest_file):
                        success = True
                if not success:
                    oa_url, _ = engine.resolve_semanticscholar(doi)
                    if oa_url and engine.stream_download(oa_url, dest_file):
                        success = True
                if not success:
                    scihub_src = engine.download_from_scihub_cascade(doi, dest_file)
                    if scihub_src:
                        success = True

            if success:
                print(f"    [+] Saved: {filename} ({dest_file.stat().st_size // 1024} KB)")
                downloaded_files.append(dest_file)
            else:
                print(f"    [-] Failed to obtain PDF!")
                failed_records.append(record)
                with open(error_log_path, "a", encoding="utf-8") as f:
                    f.write(
                        f"Index: {index}\n"
                        f"Title: {title}\n"
                        f"DOI: {doi}\n"
                        f"AccessType: {access_type}\n"
                        f"IEEE Link: https://ieeexplore.ieee.org/document/{arnumber}\n"
                        f"{'-'*40}\n"
                    )

            # Politeness & anti-bot delay
            time.sleep(self.delay)

            # Adaptive cooldown every 10 articles
            if index % 10 == 0 and index < len(records):
                print("    [*] Pausing 8 seconds to maintain polite connection rate...")
                time.sleep(8)

        print("\n" + "=" * 65)
        print(f"[*] Download Summary: {len(downloaded_files)}/{len(records)} articles downloaded.")
        if failed_records:
            print(f"[!] {len(failed_records)} articles failed. Details logged in {error_log_path.name}")

        # PDF Compilation
        if downloaded_files:
            merged_pdf_name = f"{safe_issue_folder}.pdf"
            merged_pdf_path = issue_dir / merged_pdf_name
            print(f"[*] Merging {len(downloaded_files)} documents into master file...")
            print(f"    Destination: {merged_pdf_path.name}")

            writer = PdfWriter()
            try:
                for pdf_path in tqdm(downloaded_files, desc="Merging PDFs"):
                    writer.append(str(pdf_path))
                writer.write(str(merged_pdf_path))
                writer.close()
                print(f"\n[OK] Master merged PDF successfully created!")
                print(f"     File: {merged_pdf_path.resolve()}")
                print(f"     Size: {merged_pdf_path.stat().st_size // (1024 * 1024):.1f} MB")
            except Exception as e:
                print(f"[!] Error while merging PDFs: {e}")
        else:
            print("[!] No documents were successfully downloaded to merge.")
        print("=" * 65)


def get_input_url() -> str:
    """Prompt user for IEEE journal URL, checking clipboard if available."""
    clipboard_text = ""
    try:
        import pyperclip
        clipboard_text = pyperclip.paste().strip()
    except Exception:
        pass

    if clipboard_text and "ieeexplore.ieee.org" in clipboard_text:
        print(f"[*] Detected IEEE link in clipboard:\n    {clipboard_text}")
        choice = input("Use this link? (Y/n): ").strip().lower()
        if choice in ["", "y", "yes"]:
            return clipboard_text

    print("\nPlease enter the IEEE Journal / Issue link or Document link:")
    print("Issue link example:    https://ieeexplore.ieee.org/xpl/tocresult.jsp?isnumber=8802299&punumber=8014")
    print("Document link example: https://ieeexplore.ieee.org/document/11087310")
    url = input("Link > ").strip()
    return url


def main():
    parser = argparse.ArgumentParser(description="IEEE Journal & Document Downloader (Hans x Gravi Modern Port)")
    parser.add_argument("url", nargs="?", help="IEEE issue URL or document URL")
    parser.add_argument("--output", "-o", default="pdf_output", help="Base output directory (default: pdf_output)")
    parser.add_argument("--delay", "-d", type=float, default=1.5, help="Delay between requests in seconds (default: 1.5)")
    parser.add_argument("--limit", "-l", type=int, default=None, help="Limit number of articles to download (for testing/partial runs)")

    args = parser.parse_args()
    target_url = args.url or get_input_url()

    if not target_url:
        print("[!] No URL provided. Exiting.")
        sys.exit(1)

    downloader = IEEEDownloader(delay=args.delay)

    # Check if URL is a single document link (/document/<arnumber>)
    doc_match = re.search(r"document/(\d+)", target_url)
    if doc_match and "tocresult" not in target_url and "isnumber=" not in target_url:
        arnumber = doc_match.group(1)
        downloader.process_single_document(target_url, arnumber, output_base=args.output)
    else:
        downloader.process_issue(target_url, output_base=args.output, limit=args.limit)


if __name__ == "__main__":
    main()
