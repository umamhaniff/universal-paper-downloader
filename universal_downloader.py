"""
Universal Academic Paper & DOI Downloader
Built by Hans x Gravi

A multi-source waterfall paper retriever that downloads academic research papers
from ANY publisher (Nature, Science, IEEE, Elsevier, Springer, Wiley, ACM, etc.)
by DOI or direct article URL.

Cascade Resolution Pipeline:
Tier 1: Legal Open Access via Unpaywall (Author Accepted Manuscripts, Repositories)
Tier 2: Global Scholarly Index via OpenAlex (OA Locations & Direct Publisher PDFs)
Tier 3: Semantic Scholar API (Open Access PDFs)
Tier 4: IEEE Xplore Open-Access Stamp Resolver (for IEEE articles)
Tier 5: Sci-Hub Multi-Mirror Fallback (.ru, .st, .se) for paywalled archives
"""

# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "requests>=2.28.0",
#     "beautifulsoup4>=4.11.0",
#     "pypdf>=3.0.0",
#     "pyperclip>=1.8.2",
#     "pillow>=9.0.0",
#     "tqdm>=4.64.0",
# ]
# ///

import os
import sys
import re
import time
import json
import argparse
import warnings
from pathlib import Path
from urllib.parse import urlparse, unquote
import urllib.request



warnings.filterwarnings("ignore")

import requests
from bs4 import BeautifulSoup
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

# Default pool of known Sci-Hub mirrors. Can be augmented via SCIHUB_MIRRORS env var.
DEFAULT_SCIHUB_MIRRORS = [
    "https://sci-hub.ren",
    "https://sci-hub.ru",
    "https://sci-hub.su",
    "https://sci-hub.st",
    "https://sci-hub.wf",
]

# Encrypted DoH endpoints (port 443 HTTPS) for bypass against ISP DNS tampering / poisoning
DOH_RESOLVER_ENDPOINTS = [
    ("https://1.1.1.1/dns-query", {"accept": "application/dns-json"}, "Cloudflare DoH"),
    ("https://8.8.8.8/resolve", {}, "Google DoH"),
]



class UniversalDownloader:
    def __init__(self, delay: float = 1.0):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": DEFAULT_USER_AGENT,
            "Accept-Language": "en-US,en;q=0.9",
        })
        self.delay = delay
        self.contact_email = "scholar.research@gmail.com"

    @staticmethod
    def to_long_path_safe(path: Path) -> Path:
        """Converts path to extended-length format on Windows if needed to bypass MAX_PATH limit."""
        resolved = path.resolve()
        if os.name == "nt" and not str(resolved).startswith("\\\\?\\"):
            return Path(f"\\\\?\\{resolved}")
        return resolved

    def sanitize_filename(self, name: str, max_length: int = 80) -> str:
        """Sanitizes names for Windows/Linux file paths, keeping length bounded."""
        clean = re.sub(r'[\\/*?:"<>|]', "_", name).strip()
        return clean[:max_length].strip()

    def extract_doi(self, text: str) -> str | None:
        """
        Extracts a clean DOI from arbitrary text or URLs.
        Examples:
        - 10.1038/s41586-020-2649-2
        - https://doi.org/10.1038/s41586-020-2649-2
        - https://link.springer.com/article/10.1007/s11263-020-01387-4
        - https://www.taylorfrancis.com/chapters/edit/10.1201/9781003642886-21/ensemble-machine-...
        """
        text = unquote(text.strip())

        # 1. Specialized publisher URL patterns with descriptive title slugs
        tf_match = re.search(r"/(?:chapters|books)/(?:edit|mono)/(10\.\d{4,9}/[^/?#]+)", text)
        if tf_match:
            return tf_match.group(1).rstrip(".,;")

        # 2. General DOI regex
        doi_regex = r"(10\.\d{4,9}/[-._;()/:A-Za-z0-9]+)"
        match = re.search(doi_regex, text)
        if match:
            candidate = match.group(1).rstrip(".,;")
            # If candidate was extracted from a URL and contains additional path slashes (slugs)
            parts = candidate.split("/")
            if len(parts) > 2:
                # If the 3rd part looks like an article title slug (contains multiple hyphens or long words)
                if "-" in parts[2] or len(parts[2]) > 15:
                    return f"{parts[0]}/{parts[1]}"
            return candidate
        return None

    def fetch_crossref_metadata(self, doi: str) -> dict:
        """Retrieves structured bibliographic metadata via Crossref API."""
        url = f"https://api.crossref.org/works/{doi}"
        headers = {
            "User-Agent": f"UniversalPaperDownloader/2.0 (mailto:{self.contact_email})"
        }
        try:
            res = self.session.get(url, headers=headers, timeout=10)
            if res.status_code == 200:
                data = res.json().get("message", {})
                title = data.get("title", ["Unknown Title"])[0] if data.get("title") else "Unknown Title"
                container = data.get("container-title", ["Unknown Publication"])[0] if data.get("container-title") else "Unknown Publication"
                publisher = data.get("publisher", "Unknown Publisher")

                authors = []
                for a in data.get("author", []):
                    name = f"{a.get('given', '')} {a.get('family', '')}".strip()
                    if name:
                        authors.append(name)

                year = None
                date_parts = data.get("created", {}).get("date-parts", [[None]])[0]
                if date_parts and date_parts[0]:
                    year = str(date_parts[0])

                return {
                    "doi": doi,
                    "title": title,
                    "container": container,
                    "publisher": publisher,
                    "authors": authors,
                    "year": year,
                }
        except Exception:
            pass
        return {
            "doi": doi,
            "title": f"Document_{doi.replace('/', '_')}",
            "container": "Academic Publication",
            "authors": [],
            "year": "Unknown",
        }

    def resolve_unpaywall(self, doi: str) -> tuple[str | None, str | None]:
        """Tier 1: Check Unpaywall for legitimate Open Access / repository PDF."""
        url = f"https://api.unpaywall.org/v2/{doi}?email={self.contact_email}"
        try:
            res = self.session.get(url, timeout=10)
            if res.status_code == 200:
                data = res.json()
                if data.get("is_oa"):
                    best = data.get("best_oa_location", {})
                    pdf_url = best.get("url_for_pdf") or best.get("url")
                    version = best.get("version", "open_access")
                    if pdf_url:
                        return pdf_url, f"Unpaywall ({version})"
        except Exception:
            pass
        return None, None

    def resolve_openalex(self, doi: str) -> tuple[str | None, str | None]:
        """Tier 2: Check OpenAlex for direct OA locations."""
        url = f"https://api.openalex.org/works/https://doi.org/{doi}"
        try:
            res = self.session.get(url, timeout=10)
            if res.status_code == 200:
                data = res.json()
                oa_info = data.get("open_access", {})
                if oa_info.get("is_oa"):
                    oa_url = oa_info.get("oa_url")
                    if oa_url and (".pdf" in oa_url.lower() or "download" in oa_url.lower()):
                        return oa_url, "OpenAlex (Open Access)"
                    primary = data.get("primary_location", {})
                    pdf_url = primary.get("pdf_url")
                    if pdf_url:
                        return pdf_url, "OpenAlex (Primary PDF)"
        except Exception:
            pass
        return None, None

    def resolve_semanticscholar(self, doi: str) -> tuple[str | None, str | None]:
        """Tier 3: Check Semantic Scholar for open access PDF."""
        url = f"https://api.semanticscholar.org/graph/v1/paper/{doi}?fields=openAccessPdf"
        try:
            res = self.session.get(url, timeout=10)
            if res.status_code == 200:
                data = res.json()
                oa_pdf = data.get("openAccessPdf")
                if oa_pdf and oa_pdf.get("url"):
                    cand = oa_pdf.get("url")
                    # Ignore pure DOI landing page URLs (usually bronze publisher paywalls)
                    if "doi.org/" not in cand.lower():
                        return cand, "Semantic Scholar OA"
        except Exception:
            pass
        return None, None

    def resolve_ieee_direct(self, url_or_arnumber: str) -> tuple[str | None, str | None]:
        """Tier 4: Check IEEE direct stamp resolver if it's an IEEE link."""
        match = re.search(r"document/(\d+)", url_or_arnumber) or re.search(r"arnumber=(\d+)", url_or_arnumber)
        if match:
            arnumber = match.group(1)
            stamp_url = f"https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber={arnumber}"
            headers = {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Referer": "https://ieeexplore.ieee.org/",
            }
            try:
                res = self.session.get(stamp_url, headers=headers, timeout=12)
                if res.status_code == 200:
                    soup = BeautifulSoup(res.text, "html.parser")
                    iframe = soup.find("iframe")
                    if iframe and iframe.get("src"):
                        src = iframe.get("src")
                        if "getpdf" in src.lower() or ".pdf" in src.lower():
                            if src.startswith("//"):
                                src = "https:" + src
                            elif src.startswith("/"):
                                src = "https://ieeexplore.ieee.org" + src
                            return src, "IEEE Open Access Stamp"
            except Exception:
                pass
        return None, None

    def resolve_doh(self, hostname: str) -> list[str]:
        """
        In-memory DoH (DNS-over-HTTPS) resolution.
        Bypasses ISP DNS hijacking / Internet Positif blocks for academic mirrors
        using Cloudflare (1.1.1.1) and Google (8.8.8.8) encrypted endpoints.
        Zero OS changes: Operates strictly in process memory and automatically disappears when closed.
        """
        for doh_url, headers, provider in DOH_RESOLVER_ENDPOINTS:
            try:
                full_url = f"{doh_url}?name={hostname}&type=A"
                req = urllib.request.Request(full_url, headers=headers)
                with urllib.request.urlopen(req, timeout=4) as response:
                    data = json.loads(response.read().decode("utf-8", errors="replace"))
                    answers = data.get("Answer", [])
                    ips = [a.get("data") for a in answers if a.get("type") == 1 and a.get("data")]
                    if ips:
                        return ips
            except Exception:
                continue
        return []

    def get_active_scihub_mirrors(self) -> list[str]:
        """
        Retrieves pool of Sci-Hub mirrors, combining user environment overrides (SCIHUB_MIRRORS)
        with the built-in healthy mirrors pool for long-term future-proofing.
        """
        env_custom = os.environ.get("SCIHUB_MIRRORS")
        mirrors = []
        if env_custom:
            for m in env_custom.split(","):
                m = m.strip()
                if m:
                    if not m.startswith("http"):
                        m = f"https://{m}"
                    mirrors.append(m.rstrip("/"))

        for m in DEFAULT_SCIHUB_MIRRORS:
            if m not in mirrors:
                mirrors.append(m)
        return mirrors

    def request_with_doh_fallback(self, url: str, headers: dict | None = None, timeout: int = 10) -> requests.Response | None:
        """
        Performs an HTTP GET request with automatic DoH fallback.
        If system DNS fails (e.g. ISP blocks or poisoning), resolves via DoH
        without ever modifying Windows host network configuration.
        """
        req_headers = dict(self.session.headers)
        if headers:
            req_headers.update(headers)

        # 1. Attempt standard request via session
        try:
            res = self.session.get(url, headers=req_headers, timeout=timeout)
            if res.status_code == 200:
                return res
        except (requests.exceptions.ConnectionError, requests.exceptions.SSLError, requests.exceptions.Timeout):
            pass
        except Exception:
            pass

        # 2. In-App DoH Fallback if standard request failed
        parsed = urlparse(url)
        hostname = parsed.hostname
        if not hostname:
            return None

        doh_ips = self.resolve_doh(hostname)
        if not doh_ips:
            return None

        # Try connecting with DoH-resolved IP addresses
        import socket
        orig_getaddrinfo = socket.getaddrinfo

        for ip in doh_ips:
            def custom_getaddrinfo(host, port, *args, **kwargs):
                if host == hostname:
                    return orig_getaddrinfo(ip, port, *args, **kwargs)
                return orig_getaddrinfo(host, port, *args, **kwargs)

            try:
                socket.getaddrinfo = custom_getaddrinfo
                res = self.session.get(url, headers=req_headers, timeout=timeout)
                if res.status_code == 200:
                    return res
            except Exception:
                continue
            finally:
                socket.getaddrinfo = orig_getaddrinfo

        return None

    def resolve_scihub(self, doi: str) -> tuple[str | None, str | None, str | None]:
        """
        Tier 5: Sci-Hub Multi-Mirror resolution with In-App DoH bypass & future-proof mirror pool.
        Returns (pdf_url, source_label, referer_to_use).
        """
        mirrors = self.get_active_scihub_mirrors()
        for mirror in mirrors:
            target_url = f"{mirror}/{doi}"
            try:
                res = self.request_with_doh_fallback(target_url, timeout=10)
                if not res or res.status_code != 200:
                    continue

                html = res.text
                if "робота" in html or "altcha" in html.lower():
                    continue

                soup = BeautifulSoup(html, "html.parser")

                # Pattern A: <meta name="citation_pdf_url" content="...">
                meta_pdf = soup.find("meta", attrs={"name": "citation_pdf_url"})
                if meta_pdf and meta_pdf.get("content"):
                    src = meta_pdf["content"]
                    if src.startswith("//"):
                        src = "https:" + src
                    elif src.startswith("/"):
                        src = mirror + src
                    return src, f"Sci-Hub ({mirror}) [DoH-Ready]", target_url

                # Pattern B: <embed> or <iframe> with src
                embed = soup.find(["embed", "iframe"], attrs={"src": True})
                if embed and embed.get("src"):
                    src = embed["src"].split("#")[0]  # Strip viewer params like #view=FitH
                    if src.startswith("//"):
                        src = "https:" + src
                    elif src.startswith("/"):
                        src = mirror + src
                    return src, f"Sci-Hub ({mirror}) [DoH-Ready]", target_url

                # Pattern C: location.href redirect in button or script
                btn = soup.find(lambda el: el.name in ["button", "a"] and el.get("onclick") and "location.href" in el.get("onclick"))
                if btn:
                    match = re.search(r"location\.href\s*=\s*['\"]([^'\"]+)['\"]", btn["onclick"])
                    if match:
                        src = match.group(1).split("#")[0]
                        if src.startswith("//"):
                            src = "https:" + src
                        elif src.startswith("/"):
                            src = mirror + src
                        return src, f"Sci-Hub ({mirror}) [DoH-Ready]", target_url

                # Pattern D: Direct regex search for /storage/... PDF paths
                storage_match = re.search(r"['\"](/storage/[^'\"]+\.pdf(?:#[^'\"]*)?)['\"]", html)
                if storage_match:
                    src = storage_match.group(1).split("#")[0]
                    if src.startswith("//"):
                        src = "https:" + src
                    elif src.startswith("/"):
                        src = mirror + src
                    return src, f"Sci-Hub ({mirror}) [DoH-Ready]", target_url

            except Exception:
                continue

        return None, None, None

    def download_from_scihub_cascade(self, doi: str, dest_file: Path) -> str | None:
        """
        Iterates through active Sci-Hub mirrors, extracting candidate PDF URLs and
        immediately streaming to disk with Referer headers to bypass hotlink protection.
        Skips mirrors returning captcha challenges or broken storage links.
        Returns the source label on success, or None.
        """
        mirrors = self.get_active_scihub_mirrors()
        for mirror in mirrors:
            target_url = f"{mirror}/{doi}"
            try:
                res = self.request_with_doh_fallback(target_url, timeout=10)
                if not res or res.status_code != 200:
                    continue

                html = res.text
                if "робота" in html or "altcha" in html.lower():
                    continue

                soup = BeautifulSoup(html, "html.parser")
                candidates = []

                meta_pdf = soup.find("meta", attrs={"name": "citation_pdf_url"})
                if meta_pdf and meta_pdf.get("content"):
                    candidates.append(meta_pdf["content"])

                embed = soup.find(["embed", "iframe"], attrs={"src": True})
                if embed and embed.get("src"):
                    candidates.append(embed["src"].split("#")[0])

                btn = soup.find(lambda el: el.name in ["button", "a"] and el.get("onclick") and "location.href" in el.get("onclick"))
                if btn:
                    m = re.search(r"location\.href\s*=\s*['\"]([^'\"]+)['\"]", btn["onclick"])
                    if m:
                        candidates.append(m.group(1).split("#")[0])

                for storage_match in re.findall(r"['\"](/storage/[^'\"]+\.pdf(?:#[^'\"]*)?)['\"]", html):
                    candidates.append(storage_match.split("#")[0])

                for raw_src in candidates:
                    src = raw_src.strip()
                    if src.startswith("//"):
                        src = "https:" + src
                    elif src.startswith("/"):
                        src = mirror + src

                    if self.stream_download(src, dest_file, referer=target_url):
                        return f"Sci-Hub ({mirror}) [DoH-Ready]"

            except Exception:
                continue

        return None


    def stream_download(self, url: str, dest_path: Path, referer: str | None = None) -> bool:
        """
        Streams PDF content directly to disk in 64KB chunks to adhere strictly
        to 8GB RAM constraints. Verifies %PDF header magic bytes. Supports Windows long paths.
        """
        headers = {}
        if referer:
            headers["Referer"] = referer

        safe_dest = self.to_long_path_safe(dest_path)
        safe_dest.parent.mkdir(parents=True, exist_ok=True)

        def _do_stream():
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

        # Try normal download
        try:
            if _do_stream():
                return True
        except (requests.exceptions.ConnectionError, requests.exceptions.SSLError, requests.exceptions.Timeout):
            pass
        except Exception:
            pass

        # If failed, attempt stream download with DoH IP resolution
        parsed = urlparse(url)
        hostname = parsed.hostname
        if hostname:
            doh_ips = self.resolve_doh(hostname)
            if doh_ips:
                import socket
                orig_getaddrinfo = socket.getaddrinfo
                for ip in doh_ips:
                    def custom_getaddrinfo(host, port, *args, **kwargs):
                        if host == hostname:
                            return orig_getaddrinfo(ip, port, *args, **kwargs)
                        return orig_getaddrinfo(host, port, *args, **kwargs)

                    try:
                        socket.getaddrinfo = custom_getaddrinfo
                        if _do_stream():
                            return True
                    except Exception:
                        continue
                    finally:
                        socket.getaddrinfo = orig_getaddrinfo

        if safe_dest.exists():
            try:
                safe_dest.unlink()
            except OSError:
                pass
        return False


    def download_paper(self, input_query: str, output_base: str = "pdf_output") -> bool:
        """
        Main entry point for downloading a paper by DOI or URL.
        Runs the complete multi-source waterfall cascade with structured visual dividers.
        """
        print("\n" + "═" * 72)
        print("          UNIVERSAL ACADEMIC PAPER DOWNLOADER (Hans x Gravi)          ")
        print("═" * 72)
        print(f" Input Target : {input_query.strip()}")

        # Check if it's an IEEE TOC Issue URL
        if "ieeexplore.ieee.org" in input_query and ("tocresult" in input_query or "isnumber=" in input_query):
            print("\n[*] Terdeteksi link IEEE Journal Issue (TOC). Beralih ke IEEE Issue Engine...")
            try:
                from ieee_downloader import IEEEDownloader
                downloader = IEEEDownloader(delay=self.delay)
                downloader.process_issue(input_query, output_base=output_base)
                return True
            except Exception as e:
                print(f"[!] Error pada IEEE Issue Engine: {e}")
                return False

        # Extract DOI or IEEE Document
        doi = self.extract_doi(input_query)
        ieee_arnumber = None
        if "ieeexplore.ieee.org/document/" in input_query:
            match = re.search(r"document/(\d+)", input_query)
            if match:
                ieee_arnumber = match.group(1)

        # -------------------------------------------------------------
        # SECTION 1: METADATA EXTRACTION
        # -------------------------------------------------------------
        metadata = {}
        if doi:
            metadata = self.fetch_crossref_metadata(doi)
        elif ieee_arnumber:
            try:
                from ieee_downloader import IEEEDownloader
                ieee = IEEEDownloader()
                ieee_meta = ieee.fetch_document_metadata(ieee_arnumber)
                doi = ieee_meta.get("doi")
                metadata = {
                    "doi": doi or f"ieee_{ieee_arnumber}",
                    "title": ieee_meta.get("title", f"Article_{ieee_arnumber}"),
                    "container": ieee_meta.get("publicationTitle", "IEEE Publication"),
                    "publisher": "IEEE",
                    "authors": [a.get("name") for a in ieee_meta.get("authors", []) if a.get("name")],
                    "year": ieee_meta.get("publicationYear"),
                }
            except Exception as e:
                pass

        if not doi and not ieee_arnumber:
            print("\n" + "─" * 72)
            print(" [✕] ERROR: DOI atau Link Dokumen Tidak Dikenali!")
            print("─" * 72)
            print(f" Input yang kamu masukkan: '{input_query}'")
            print(" Format yang didukung:")
            print("  • Nomor DOI  : 10.1038/s41586-020-2649-2")
            print("  • Link Paper : https://www.nature.com/articles/s41586-020-2649-2")
            print("  • Link IEEE  : https://ieeexplore.ieee.org/document/8802303")
            print("═" * 72)
            return False

        title = metadata.get("title", f"Document_{doi.replace('/', '_')}")
        container = metadata.get("container", "Academic Publication")
        authors = metadata.get("authors", [])
        year = metadata.get("year", "")

        print("\n" + "┌" + "─" * 70 + "┐")
        print("│ 📋 1. METADATA ARTIKEL ILMIAH" + " " * 41 + "│")
        print("├" + "─" * 70 + "┤")
        print(f"│ Judul     : {title[:56]:<56} │")
        if len(title) > 56:
            print(f"│             {title[56:112]:<56} │")
        if authors:
            author_str = ', '.join(authors[:3]) + (' et al.' if len(authors) > 3 else '')
            print(f"│ Penulis   : {author_str[:56]:<56} │")
        print(f"│ Publikasi : {container[:46]} ({year})".ljust(69) + "│")
        print(f"│ DOI       : {str(doi)[:56]:<56} │")
        print("└" + "─" * 70 + "┘")

        safe_container = self.sanitize_filename(container)[:60]
        safe_title = self.sanitize_filename(title)[:80]
        dest_dir = Path(output_base) / "Universal_Downloads" / safe_container
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_file = dest_dir / f"{safe_title}.pdf"

        # Check existing file
        if dest_file.exists() and dest_file.stat().st_size > 1024:
            print("\n" + "┌" + "─" * 70 + "┐")
            print("│ ⚡ FILE SUDAH PERNAH DIUNDUH SEBELUMNYA" + " " * 31 + "│")
            print("├" + "─" * 70 + "┤")
            print(f"│ Lokasi : {str(dest_file.resolve())[:58]:<58} │")
            print(f"│ Ukuran : {dest_file.stat().st_size // 1024} KB".ljust(69) + "│")
            print("└" + "─" * 70 + "┘")
            print("═" * 72)
            return True

        # -------------------------------------------------------------
        # SECTION 2: CASCADE RESOLUTION PIPELINE (TIER CHECKING & STREAM)
        # -------------------------------------------------------------
        print("\n" + "┌" + "─" * 70 + "┐")
        print("│ 🔍 2. WATERFALL CASCADE RESOLUTION (Pengecekan Multi-Sumber)       │")
        print("├" + "─" * 70 + "┤")

        success = False
        source_label = None

        # Tier 1: Unpaywall
        if doi:
            cand_url, cand_label = self.resolve_unpaywall(doi)
            if cand_url:
                print("│ [✓] Tier 1: Unpaywall (Legal Open Access) ──► DITEMUKAN!           │")
                print("│     • Mengunduh & memvalidasi integritas (%PDF)...                   │")
                if self.stream_download(cand_url, dest_file):
                    success = True
                    source_label = cand_label
                else:
                    print("│     • Link bukan berkas PDF valid. Melanjutkan cascade...            │")
            else:
                print("│ [-] Tier 1: Unpaywall (Legal Open Access) ──► Tidak ada file OA    │")

        # Tier 2: OpenAlex
        if not success and doi:
            cand_url, cand_label = self.resolve_openalex(doi)
            if cand_url:
                print("│ [✓] Tier 2: OpenAlex Global Index         ──► DITEMUKAN!           │")
                print("│     • Mengunduh & memvalidasi integritas (%PDF)...                   │")
                if self.stream_download(cand_url, dest_file):
                    success = True
                    source_label = cand_label
                else:
                    print("│     • Link bukan berkas PDF valid. Melanjutkan cascade...            │")
            else:
                print("│ [-] Tier 2: OpenAlex Global Index         ──► Tidak ada file OA    │")

        # Tier 3: Semantic Scholar
        if not success and doi:
            cand_url, cand_label = self.resolve_semanticscholar(doi)
            if cand_url:
                print("│ [✓] Tier 3: Semantic Scholar Open Access  ──► DITEMUKAN!           │")
                print("│     • Mengunduh & memvalidasi integritas (%PDF)...                   │")
                if self.stream_download(cand_url, dest_file):
                    success = True
                    source_label = cand_label
                else:
                    print("│     • Link bukan berkas PDF valid. Melanjutkan cascade...            │")
            else:
                print("│ [-] Tier 3: Semantic Scholar Open Access  ──► Tidak ada file OA    │")

        # Tier 4: IEEE Stamp
        if not success and ("ieeexplore" in input_query or ieee_arnumber):
            cand_url, cand_label = self.resolve_ieee_direct(input_query or ieee_arnumber)
            if cand_url:
                print("│ [✓] Tier 4: IEEE Open-Access Stamp        ──► DITEMUKAN!           │")
                print("│     • Mengunduh & memvalidasi integritas (%PDF)...                   │")
                if self.stream_download(cand_url, dest_file, referer="https://ieeexplore.ieee.org/"):
                    success = True
                    source_label = cand_label
                else:
                    print("│     • Paper berstatus terkunci. Melanjutkan cascade...               │")
            else:
                print("│ [-] Tier 4: IEEE Open-Access Stamp        ──► Paper Berstatus Terkunci │")

        # Tier 5: Sci-Hub Multi-Mirror
        if not success and doi:
            print("│ [*] Tier 5: Sci-Hub Multi-Mirror Archive  ──► Memeriksa Mirror Pool...│")
            scihub_label = self.download_from_scihub_cascade(doi, dest_file)
            if scihub_label:
                print("│ [✓] Tier 5: Sci-Hub Multi-Mirror Archive  ──► DITEMUKAN & VALID!   │")
                success = True
                source_label = scihub_label
            else:
                print("│ [-] Tier 5: Sci-Hub Multi-Mirror Archive  ──► Seluruh Mirror Gagal │")

        print("├" + "─" * 70 + "┤")
        if success:
            print(f"│ 🎯 Sumber Terpilih: {source_label[:49]:<49}│")
        else:
            print("│ ⚠️ Status: Seluruh 5 Tier tidak dapat mengunduh berkas PDF utuh    │")
        print("└" + "─" * 70 + "┘")

        # -------------------------------------------------------------
        # SECTION 3: DOWNLOAD EXECUTION SUMMARY
        # -------------------------------------------------------------
        print("\n" + "┌" + "─" * 70 + "┐")
        print("│ ⬇️ 3. PROSES PENGUNDUHAN BERKAS                                      │")
        print("├" + "─" * 70 + "┤")
        if success:
            print(f"│ • Menghubungi endpoint penyedia PDF... ──► OK!                      │")
            print(f"│ • Sumber Terpilih : {source_label[:48]:<48} │")
            print("│ • Mengalirkan data langsung ke disk (chunk 64KB, RAM-friendly)...   │")
            print("│ • Memverifikasi integritas format (%PDF magic bytes) ──► VALID!      │")
        else:
            print("│ • Status   : Berkas terkunci paywall atau belum terarsip di repositori.│")
            print("│ • Verifikasi: Seluruh 5 Tier selesai dicoba tanpa stream berkas valid.│")
        print("└" + "─" * 70 + "┘")

        # -------------------------------------------------------------
        # SECTION 4: FINAL OUTPUT BOX
        # -------------------------------------------------------------
        if success:
            print("\n" + "┌" + "─" * 70 + "┐")
            print("│ ✅ 4. HASIL AKHIR : BERHASIL DISIMPAN!                               │")
            print("├" + "─" * 70 + "┤")
            print(f"│ Judul   : {title[:58]:<58} │")
            print(f"│ Sumber  : {source_label[:58]:<58} │")
            print(f"│ Berkas  : {dest_file.name[:58]:<58} │")
            print(f"│ Folder  : {str(dest_file.parent.resolve())[:58]:<58} │")
            print(f"│ Ukuran  : {dest_file.stat().st_size // 1024} KB".ljust(69) + "│")
            print("└" + "─" * 70 + "┘")
            print("═" * 72)
            return True
        else:
            rg_search = f"https://www.researchgate.net/search/publication?q={title.replace(' ', '+')[:60]}"
            print("\n" + "┌" + "─" * 70 + "┐")
            print("│ ⚠️ 4. HASIL AKHIR : DOKUMEN TERKUNCI (PAYWALL RESMI)                 │")
            print("├" + "─" * 70 + "┤")
            print("│ Analisis Masalah:                                                    │")
            print("│ • Dokumen berbayar (Closed Access) dan belum diarsip di Sci-Hub.     │")
            print("│ • Terjadi pada prosiding/jurnal sangat baru terbitan 2024-2026.      │")
            print("│                                                                      │")
            print("│ Opsi Akses Mandiri (Gratis & Legal):                                 │")
            print("│ 1. Request Full-Text Langsung ke Penulis (ResearchGate):             │")
            print(f"│    {rg_search[:66]:<66}│")
            print("│ 2. Akses via Jaringan / VPN / Akun SSO Kampus Berlangganan           │")
            print(f"│ 3. Halaman Resmi DOI: https://doi.org/{str(doi)[:40]:<40}│")
            print("└" + "─" * 70 + "┘")
            print("═" * 72)
            return False


def get_input() -> str:
    """Prompt user for DOI or URL with clipboard fallback."""
    clipboard_text = ""
    try:
        import pyperclip
        clipboard_text = pyperclip.paste().strip()
    except Exception:
        pass

    if clipboard_text and ("10." in clipboard_text or "http" in clipboard_text):
        print(f"\n[*] Terdeteksi link/DOI di Clipboard:")
        print(f"    {clipboard_text}")
        choice = input("Gunakan link/DOI dari clipboard ini? (Y/n) [Default: Y] > ").strip().lower()
        if choice in ["", "y", "yes"]:
            return clipboard_text

    print("\nMasukkan nomor DOI atau Link Paper (Nature, IEEE, Springer, Elsevier, dll):")
    print("Contoh:")
    print("  • DOI        : 10.1038/s41586-020-2649-2")
    print("  • URL Nature : https://www.nature.com/articles/s41586-020-2649-2")
    print("  • URL IEEE   : https://ieeexplore.ieee.org/document/8802303")
    print("  • Issue IEEE : https://ieeexplore.ieee.org/xpl/tocresult.jsp?isnumber=8802299&punumber=8014")
    query = input("\nQuery / DOI > ").strip()
    return query


def ask_next_action(output_base: str) -> str:
    """Prompt user for the next action after an operation."""
    print("\n" + "┌" + "─" * 70 + "┐")
    print("│ 📌 PILIHAN TINDAKAN SELANJUTNYA                                      │")
    print("├" + "─" * 70 + "┤")
    print("│ [1] / [Enter] : Cari & unduh paper / DOI lain                        │")
    print("│ [2]           : Buka folder hasil unduhan di File Explorer (PDF)     │")
    print("│ [3] / [q]     : Tutup program & selesai                              │")
    print("└" + "─" * 70 + "┘")
    return input("Pilihan kamu (1/2/3) [Default: 1] > ").strip().lower()


def interactive_menu(downloader: UniversalDownloader, output_base: str, initial_query: str | None = None):
    """Interactive loop providing continuous workflow and explicit exit controls."""
    current_query = initial_query

    while True:
        if not current_query:
            current_query = get_input()

        if current_query:
            downloader.download_paper(current_query, output_base=output_base)
            current_query = None  # Reset query after download finishes

        # Menu loop
        while True:
            choice = ask_next_action(output_base)
            if choice in ["3", "q", "exit", "quit", "keluar"]:
                print("\n[✓] Terima kasih! Program ditutup. Sampai jumpa, Hans!\n")
                return
            elif choice == "2":
                out_path = Path(output_base).resolve()
                out_path.mkdir(parents=True, exist_ok=True)
                print(f"\n[*] Membuka folder di File Explorer: {out_path}")
                try:
                    os.startfile(str(out_path))
                except Exception as e:
                    print(f"[!] Gagal membuka folder: {e}")
                continue
            else:
                # Option 1 or Enter: loop back to get a new query!
                break


def main():
    parser = argparse.ArgumentParser(description="Universal Academic Paper & DOI Downloader (Hans x Gravi Engine)")
    parser.add_argument("query", nargs="?", help="DOI or paper URL to download")
    parser.add_argument("--output", "-o", default="pdf_output", help="Base output directory (default: pdf_output)")
    parser.add_argument("--file", "-f", help="Text file containing list of DOIs to batch download (one per line)")
    parser.add_argument("--delay", "-d", type=float, default=1.0, help="Delay between requests in seconds (default: 1.0)")

    args = parser.parse_args()
    downloader = UniversalDownloader(delay=args.delay)

    if args.file:
        batch_path = Path(args.file)
        if not batch_path.exists():
            print(f"[!] File batch tidak ditemukan: {args.file}")
            sys.exit(1)
        with open(batch_path, "r", encoding="utf-8") as f:
            lines = [l.strip() for l in f if l.strip() and not l.startswith("#")]
        print(f"[*] Memulai batch download untuk {len(lines)} artikel...")
        for i, q in enumerate(lines, start=1):
            print(f"\n--- Batch Item [{i}/{len(lines)}] ---")
            downloader.download_paper(q, output_base=args.output)
            time.sleep(args.delay)
        # Offer menu after batch finishes too!
        interactive_menu(downloader, output_base=args.output)
    elif args.query:
        interactive_menu(downloader, output_base=args.output, initial_query=args.query)
    else:
        interactive_menu(downloader, output_base=args.output)


if __name__ == "__main__":
    main()
