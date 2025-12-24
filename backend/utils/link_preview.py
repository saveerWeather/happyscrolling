"""Link preview generation utilities"""
import requests
from bs4 import BeautifulSoup
from typing import Optional, Dict
from urllib.parse import urlparse
import re

def fetch_link_preview(url: str, timeout: int = 5) -> Optional[Dict[str, Optional[str]]]:
    """
    Fetch Open Graph and meta tags from a URL
    Returns dict with title, description, image_url, site_name
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract Open Graph tags
        og_title = soup.find('meta', property='og:title')
        og_description = soup.find('meta', property='og:description')
        og_image = soup.find('meta', property='og:image')
        og_site_name = soup.find('meta', property='og:site_name')
        
        # Fallback to regular meta tags
        title = og_title.get('content') if og_title else None
        if not title:
            title_tag = soup.find('title')
            title = title_tag.string if title_tag else None
        
        description = og_description.get('content') if og_description else None
        if not description:
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            description = meta_desc.get('content') if meta_desc else None
        
        image_url = og_image.get('content') if og_image else None
        site_name = og_site_name.get('content') if og_site_name else None
        
        # If no site_name, extract from domain
        if not site_name:
            parsed = urlparse(url)
            site_name = parsed.netloc.replace('www.', '')
        
        # Clean up text
        if title:
            title = title.strip()[:500]  # Limit length
        if description:
            description = description.strip()[:1000]  # Limit length
        
        # Make image URL absolute if relative
        if image_url and not image_url.startswith('http'):
            parsed = urlparse(url)
            base_url = f"{parsed.scheme}://{parsed.netloc}"
            if image_url.startswith('/'):
                image_url = base_url + image_url
            else:
                image_url = base_url + '/' + image_url
        
        return {
            'title': title,
            'description': description,
            'image_url': image_url,
            'site_name': site_name
        }
        
    except Exception as e:
        print(f"⚠️ Error fetching preview for {url}: {e}")
        return None

