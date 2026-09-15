"""Server-Side Request Forgery (SSRF) Protection and Safe URL Fetching."""

import socket
import ipaddress
from urllib.parse import urlparse
from typing import Tuple, Optional
import httpx
from bs4 import BeautifulSoup

from .config import settings
from .exceptions import URLFetchError, ArticleExtractionError

# Metadata hostnames and blacklisted patterns
BLOCKED_HOSTNAMES = {
    "localhost", "127.0.0.1", "::1", "0.0.0.0",
    "instance-data", "metadata.google.internal",
    "metadata.local", "kubernetes.default.svc"
}


def validate_url_safety(url_str: str) -> Tuple[str, str]:
    """Validate that URL uses http/https and does not resolve to private/internal IP addresses.
    
    Returns (clean_url, resolved_ip) if safe, otherwise raises URLFetchError.
    """
    if not url_str or not isinstance(url_str, str):
        raise URLFetchError("A valid URL string must be provided.")

    try:
        parsed = urlparse(url_str.strip())
    except Exception as e:
        raise URLFetchError(f"Malformed URL: {str(e)}")

    # 1. Enforce scheme
    if parsed.scheme not in ("http", "https"):
        raise URLFetchError(f"Unsupported URL protocol '{parsed.scheme}'. Only HTTP and HTTPS are permitted.")

    hostname = parsed.hostname
    if not hostname:
        raise URLFetchError("URL must contain a valid hostname.")

    hostname_lower = hostname.lower()
    if hostname_lower in BLOCKED_HOSTNAMES or hostname_lower.endswith(".local") or hostname_lower.endswith(".internal"):
        raise URLFetchError(f"Access to private/internal host '{hostname}' is strictly blocked.")

    # Enforce standard web ports
    if parsed.port and parsed.port not in (80, 443, 8080, 8443):
        raise URLFetchError(f"Port {parsed.port} is not permitted for article fetching. Only standard web ports (80, 443, 8080, 8443) are allowed.")

    # 2. DNS Resolution and IP checking
    try:
        addr_info = socket.getaddrinfo(hostname, parsed.port or (443 if parsed.scheme == "https" else 80))
    except socket.gaierror:
        raise URLFetchError(f"Unable to resolve DNS for hostname '{hostname}'.")

    # Inspect all resolved IPs
    for family, _, _, _, sockaddr in addr_info:
        ip_str = sockaddr[0]
        try:
            ip_obj = ipaddress.ip_address(ip_str)
        except ValueError:
            raise URLFetchError(f"Invalid IP address resolved: {ip_str}")

        # Check loopback, private RFC1918, link-local, reserved, multicast
        if (
            ip_obj.is_loopback or
            ip_obj.is_private or
            ip_obj.is_link_local or
            ip_obj.is_reserved or
            ip_obj.is_multicast or
            ip_obj.is_unspecified
        ):
            raise URLFetchError(f"Access to private, link-local, or loopback network address ({ip_str}) is forbidden.")

        # Block AWS/GCP/Azure link-local metadata address 169.254.169.254 explicitly
        if str(ip_obj) == "169.254.169.254":
            raise URLFetchError("Access to cloud metadata service is strictly blocked.")

    return url_str.strip(), addr_info[0][4][0]


async def fetch_url_safely(url_str: str) -> Tuple[str, str, str]:
    """Fetch article HTML safely following redirects up to MAX_URL_REDIRECTS.
    
    Returns (final_url, content_type, html_text).
    """
    current_url = url_str
    headers = {
        "User-Agent": "TruthLens/1.0 (Research Credibility Analysis; +https://truthlens.local)",
        "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.8"
    }

    async with httpx.AsyncClient(follow_redirects=False, timeout=settings.URL_REQUEST_TIMEOUT_SECONDS) as client:
        for hop in range(settings.MAX_URL_REDIRECTS + 1):
            # Validate every hop against SSRF rules
            validate_url_safety(current_url)

            try:
                response = await client.get(current_url, headers=headers)
            except httpx.TimeoutException:
                raise URLFetchError("URL request timed out after 8 seconds.")
            except httpx.RequestError as e:
                raise URLFetchError(f"Network error while connecting to source: {str(e)}")

            # Handle redirects manually to re-verify safety
            if response.status_code in (301, 302, 303, 307, 308):
                redirect_url = response.headers.get("Location")
                if not redirect_url:
                    raise URLFetchError("Redirect received without valid Location header.")
                # Resolve relative redirects
                parsed_redirect = httpx.URL(current_url).join(redirect_url)
                current_url = str(parsed_redirect)
                continue

            if response.status_code != 200:
                raise URLFetchError(f"Source server returned HTTP error status {response.status_code}.")

            # Validate Content-Type
            content_type = response.headers.get("content-type", "").lower()
            if not any(t in content_type for t in ("text/html", "application/xhtml+xml")):
                raise URLFetchError(f"Unsupported content type '{content_type}'. TruthLens only parses HTML articles.")

            # Validate Content Length
            content_bytes = response.content
            if len(content_bytes) > settings.MAX_URL_CONTENT_BYTES:
                raise URLFetchError(f"Response size ({len(content_bytes)} bytes) exceeds 5MB limit.")

            return current_url, content_type, response.text

    raise URLFetchError(f"Exceeded maximum allowable redirect hops ({settings.MAX_URL_REDIRECTS}).")


def extract_article_from_html(html_text: str) -> Tuple[str, str]:
    """Extract clean title and body text from HTML with robust fallback heuristics.
    
    Returns (title, body_text).
    """
    if not html_text:
        raise ArticleExtractionError("Empty HTML response received.")

    soup = BeautifulSoup(html_text, "html.parser")

    # Remove script, style, nav, footer, ads, header tags
    for tag in soup(["script", "style", "nav", "footer", "aside", "header", "form", "noscript", "svg"]):
        tag.decompose()

    # 1. Extract title
    title = ""
    og_title = soup.find("meta", property="og:title")
    if og_title and og_title.get("content"):
        title = og_title["content"].strip()
    elif soup.title and soup.title.string:
        title = soup.title.string.strip()
    elif soup.find("h1"):
        title = soup.find("h1").get_text().strip()

    # 2. Extract article body
    article_tag = soup.find("article")
    paragraphs = []
    if article_tag:
        paragraphs = [p.get_text().strip() for p in article_tag.find_all("p") if len(p.get_text().strip()) > 30]
        
    if not paragraphs:
        # Fallback to main content container
        main_tag = soup.find("main") or soup.find("div", class_=lambda c: c and any(w in c.lower() for w in ("article", "story", "content", "post-body")))
        if main_tag:
            paragraphs = [p.get_text().strip() for p in main_tag.find_all("p") if len(p.get_text().strip()) > 30]

    if not paragraphs:
        # Generic body paragraph search
        paragraphs = [p.get_text().strip() for p in soup.find_all("p") if len(p.get_text().strip()) > 35]

    body_text = "\n\n".join(paragraphs).strip()

    if len(body_text) < 40:
        raise ArticleExtractionError(
            "Could not extract meaningful article text from the webpage. The page may be paywalled, JavaScript-rendered, or not a news article."
        )

    return title or "Extracted Web Article", body_text
