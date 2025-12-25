"""Link preview generation utilities with oEmbed support"""
import requests
from bs4 import BeautifulSoup
from typing import Optional, Dict, List
from urllib.parse import urlparse, urljoin, quote
import json

# Increase timeout for slow sites
DEFAULT_TIMEOUT = 15

def is_embeddable_platform(url: str) -> bool:
    """Check if URL is from an embeddable platform"""
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    
    embeddable_domains = [
        'youtube.com', 'youtu.be', 'm.youtube.com',
        'twitter.com', 'x.com', 'mobile.twitter.com',
        'vimeo.com',
        'spotify.com', 'open.spotify.com',
        'soundcloud.com',
        'tiktok.com', 'vm.tiktok.com',
        'instagram.com', 'www.instagram.com',
        'reddit.com', 'www.reddit.com',
    ]
    
    return any(domain in domain_name for domain_name in embeddable_domains)

def is_twitter_url(url: str) -> bool:
    """Check if URL is a Twitter/X post"""
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    return 'twitter.com' in domain or 'x.com' in domain

def is_youtube_url(url: str) -> bool:
    """Check if URL is a YouTube video"""
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    return 'youtube.com' in domain or 'youtu.be' in domain

def is_reddit_url(url: str) -> bool:
    """Check if URL is a Reddit post"""
    parsed = urlparse(url)
    return 'reddit.com' in parsed.netloc.lower()

def is_instagram_url(url: str) -> bool:
    """Check if URL is an Instagram post"""
    parsed = urlparse(url)
    return 'instagram.com' in parsed.netloc.lower()

def fetch_oembed(url: str, timeout: int = DEFAULT_TIMEOUT) -> Optional[Dict]:
    """
    Fetch oEmbed data for embeddable platforms
    Returns dict with title, author_name, thumbnail_url, html, etc.
    """
    try:
        # Twitter/X oEmbed
        if is_twitter_url(url):
            oembed_url = f"https://publish.twitter.com/oembed?url={quote(url)}"
            response = requests.get(oembed_url, timeout=timeout)
            if response.status_code == 200:
                data = response.json()
                # Parse the HTML to extract tweet text
                embed_html = data.get('html', '')
                tweet_text = ''
                if embed_html:
                    # Extract text from blockquote <p> tag in embed HTML
                    soup = BeautifulSoup(embed_html, 'html.parser')
                    p_tag = soup.find('p')
                    if p_tag:
                        tweet_text = p_tag.get_text()

                return {
                    'title': tweet_text[:100] if tweet_text else data.get('author_name', ''),
                    'description': None,
                    'text_content': tweet_text or data.get('author_name', ''),
                    'author': data.get('author_name', '').replace('@', ''),
                    'image_url': None,
                    'embed_html': embed_html,
                    'embeddable': False,  # Don't use embed, show native
                    'platform': 'twitter',
                    'site_name': 'X'
                }
        
        # YouTube oEmbed (via noembed.com)
        elif is_youtube_url(url):
            oembed_url = f"https://noembed.com/embed?url={quote(url)}"
            response = requests.get(oembed_url, timeout=timeout)
            if response.status_code == 200:
                data = response.json()
                return {
                    'title': data.get('title', ''),
                    'description': None,
                    'author': data.get('author_name', ''),
                    'image_url': data.get('thumbnail_url', ''),
                    'embed_html': data.get('html', ''),
                    'embeddable': True,
                    'platform': 'youtube',
                    'site_name': 'YouTube'
                }
        
        # Vimeo oEmbed
        elif 'vimeo.com' in url:
            # Extract video ID
            parsed = urlparse(url)
            video_id = None
            path_parts = [p for p in parsed.path.split('/') if p]
            if path_parts:
                video_id = path_parts[-1]
            
            if video_id:
                oembed_url = f"https://vimeo.com/api/oembed.json?url={quote(url)}"
                response = requests.get(oembed_url, timeout=timeout)
                if response.status_code == 200:
                    data = response.json()
                    return {
                        'title': data.get('title', ''),
                        'description': data.get('description', ''),
                        'author': data.get('author_name', ''),
                        'image_url': data.get('thumbnail_url', ''),
                        'embed_html': data.get('html', ''),
                        'embeddable': True,
                        'platform': 'vimeo',
                        'site_name': 'Vimeo'
                    }
        
        # Spotify oEmbed
        elif 'spotify.com' in url:
            oembed_url = f"https://embed.spotify.com/oembed?url={quote(url)}"
            response = requests.get(oembed_url, timeout=timeout)
            if response.status_code == 200:
                data = response.json()
                return {
                    'title': data.get('title', ''),
                    'description': None,
                    'author': data.get('author_name', ''),
                    'image_url': data.get('thumbnail_url', ''),
                    'embed_html': data.get('html', ''),
                    'embeddable': True,
                    'platform': 'spotify',
                    'site_name': 'Spotify'
                }
        
        # SoundCloud oEmbed
        elif 'soundcloud.com' in url:
            oembed_url = f"https://soundcloud.com/oembed?url={quote(url)}&format=json"
            response = requests.get(oembed_url, timeout=timeout)
            if response.status_code == 200:
                data = response.json()
                return {
                    'title': data.get('title', ''),
                    'description': None,
                    'author': data.get('author_name', ''),
                    'image_url': None,  # SoundCloud oEmbed doesn't always provide images
                    'embed_html': data.get('html', ''),
                    'embeddable': True,
                    'platform': 'soundcloud',
                    'site_name': 'SoundCloud'
                }
        
        # TikTok oEmbed
        elif 'tiktok.com' in url:
            oembed_url = f"https://www.tiktok.com/oembed?url={quote(url)}"
            response = requests.get(oembed_url, timeout=timeout)
            if response.status_code == 200:
                data = response.json()
                return {
                    'title': data.get('title', ''),
                    'description': None,
                    'author': data.get('author_name', ''),
                    'image_url': data.get('thumbnail_url', ''),
                    'embed_html': data.get('html', ''),
                    'embeddable': True,
                    'platform': 'tiktok',
                    'site_name': 'TikTok'
                }

        # Instagram oEmbed
        elif 'instagram.com' in url:
            oembed_url = f"https://graph.facebook.com/v8.0/instagram_oembed?url={quote(url)}"
            try:
                response = requests.get(oembed_url, timeout=timeout)
                if response.status_code == 200:
                    data = response.json()
                    return {
                        'title': data.get('title', 'Instagram Post'),
                        'description': None,
                        'author': data.get('author_name', ''),
                        'image_url': data.get('thumbnail_url', ''),
                        'embed_html': None,  # Don't embed, show as link
                        'embeddable': False,
                        'platform': 'instagram',
                        'site_name': 'Instagram'
                    }
            except:
                # Instagram posts often require login, return basic info
                return {
                    'title': 'Instagram Post',
                    'description': 'View on Instagram (login required)',
                    'author': None,
                    'image_url': None,
                    'embed_html': None,
                    'embeddable': False,
                    'platform': 'instagram',
                    'site_name': 'Instagram'
                }

        # Reddit oEmbed (via noembed.com)
        elif is_reddit_url(url):
            oembed_url = f"https://noembed.com/embed?url={quote(url)}"
            response = requests.get(oembed_url, timeout=timeout)
            if response.status_code == 200:
                data = response.json()
                # Reddit oEmbed might not always work, so we'll also try HTML scraping
                if data.get('html'):
                    return {
                        'title': data.get('title', ''),
                        'description': data.get('description', ''),
                        'author': data.get('author_name', ''),
                        'image_url': data.get('thumbnail_url', ''),
                        'embed_html': data.get('html', ''),
                        'embeddable': True,
                        'platform': 'reddit',
                        'site_name': 'Reddit'
                    }
        
        # Generic oEmbed (try noembed.com for other platforms)
        oembed_url = f"https://noembed.com/embed?url={quote(url)}"
        response = requests.get(oembed_url, timeout=timeout)
        if response.status_code == 200:
            data = response.json()
            if data.get('html') and 'error' not in data:
                return {
                    'title': data.get('title', ''),
                    'description': data.get('description', ''),
                    'author': data.get('author_name', ''),
                    'image_url': data.get('thumbnail_url', ''),
                    'embed_html': data.get('html', ''),
                    'embeddable': True,
                    'platform': 'other',
                    'site_name': data.get('provider_name', '')
                }
    
    except requests.exceptions.Timeout:
        print(f"⚠️ oEmbed timeout for {url}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"⚠️ oEmbed request error for {url}: {e}")
        return None
    except Exception as e:
        print(f"⚠️ oEmbed error for {url}: {e}")
        return None
    
    return None

def extract_twitter_content_from_html(soup: BeautifulSoup, url: str) -> Dict[str, Optional[str]]:
    """Extract content from Twitter/X post HTML (fallback when oEmbed fails)"""
    result = {}
    
    # Try Twitter Card tags first
    twitter_title = soup.find('meta', attrs={'name': 'twitter:title'})
    twitter_description = soup.find('meta', attrs={'name': 'twitter:description'})
    twitter_image = soup.find('meta', attrs={'name': 'twitter:image'})
    twitter_creator = soup.find('meta', attrs={'name': 'twitter:creator'})
    
    # Fallback to Open Graph
    og_title = soup.find('meta', property='og:title')
    og_description = soup.find('meta', property='og:description')
    og_image = soup.find('meta', property='og:image')
    
    # Get title (tweet text is often in og:title or twitter:title)
    title = None
    if twitter_title:
        title = twitter_title.get('content')
    if not title and og_title:
        title = og_title.get('content')
    
    # Get description
    description = None
    if twitter_description:
        description = twitter_description.get('content')
    if not description and og_description:
        description = og_description.get('content')
    
    # Combine title and description for full tweet text
    text_content = title or description or ""
    if title and description and title != description:
        text_content = f"{title}\n\n{description}" if description else title
    
    # Get image
    image_url = None
    if twitter_image:
        image_url = twitter_image.get('content')
    if not image_url and og_image:
        image_url = og_image.get('content')
    
    # Get author info
    author = None
    if twitter_creator:
        author = twitter_creator.get('content', '').replace('@', '')
    
    # Make image URL absolute
    if image_url:
        image_url = make_absolute_url(image_url, url)
    
    result['title'] = text_content[:500] if text_content else None
    result['description'] = None
    result['text_content'] = text_content[:2000] if text_content else None
    result['image_url'] = image_url
    result['site_name'] = 'Twitter' if 'twitter.com' in url else 'X'
    result['author'] = author
    result['platform'] = 'twitter'
    result['embeddable'] = False  # No embed HTML from scraping
    result['embed_html'] = None
    
    return result

def extract_reddit_content(soup: BeautifulSoup, url: str) -> Dict[str, Optional[str]]:
    """Extract content from Reddit post"""
    result = {}
    
    # Reddit uses Open Graph tags
    og_title = soup.find('meta', property='og:title')
    og_description = soup.find('meta', property='og:description')
    og_image = soup.find('meta', property='og:image')
    og_site_name = soup.find('meta', property='og:site_name')
    
    title = og_title.get('content') if og_title else None
    description = og_description.get('content') if og_description else None
    image_url = og_image.get('content') if og_image else None
    site_name = og_site_name.get('content') if og_site_name else 'Reddit'
    
    # Try to extract subreddit from URL
    subreddit = None
    parsed = urlparse(url)
    path_parts = [p for p in parsed.path.split('/') if p]
    if 'r' in path_parts:
        idx = path_parts.index('r')
        if idx + 1 < len(path_parts):
            subreddit = f"r/{path_parts[idx + 1]}"
    
    if image_url:
        image_url = make_absolute_url(image_url, url)
    
    result['title'] = title[:500] if title else None
    result['description'] = description[:1000] if description else None
    result['image_url'] = image_url
    result['site_name'] = site_name
    result['subreddit'] = subreddit
    result['platform'] = 'reddit'
    result['embeddable'] = False
    result['embed_html'] = None
    
    return result

def extract_article_content(soup: BeautifulSoup, url: str) -> Dict[str, Optional[str]]:
    """Extract content from article/blog post with aggressive fallbacks"""
    result = {}
    images = []

    # Extract Open Graph tags
    og_title = soup.find('meta', property='og:title')
    og_description = soup.find('meta', property='og:description')
    og_image = soup.find('meta', property='og:image')
    og_site_name = soup.find('meta', property='og:site_name')

    # Try Twitter Card tags as fallback
    twitter_title = soup.find('meta', attrs={'name': 'twitter:title'})
    twitter_description = soup.find('meta', attrs={'name': 'twitter:description'})
    twitter_image = soup.find('meta', attrs={'name': 'twitter:image'})

    # Extract title with multiple fallbacks
    title = None
    if og_title:
        title = og_title.get('content')
    if not title and twitter_title:
        title = twitter_title.get('content')
    if not title:
        title_tag = soup.find('title')
        title = title_tag.string if title_tag else None
    if not title:
        # Last resort: try h1
        h1 = soup.find('h1')
        title = h1.get_text() if h1 else None

    # Extract description with fallbacks
    description = None
    if og_description:
        description = og_description.get('content')
    if not description and twitter_description:
        description = twitter_description.get('content')
    if not description:
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        description = meta_desc.get('content') if meta_desc else None
    if not description:
        # Try to find first paragraph
        p_tag = soup.find('p')
        if p_tag:
            description = p_tag.get_text()

    # Extract images with fallbacks
    if og_image:
        img_url = og_image.get('content')
        if img_url:
            images.append(make_absolute_url(img_url, url))

    if twitter_image and not images:
        img_url = twitter_image.get('content')
        if img_url:
            images.append(make_absolute_url(img_url, url))

    # Try to find all og:image tags
    og_images = soup.find_all('meta', property='og:image')
    for img in og_images:
        img_url = img.get('content')
        if img_url:
            full_url = make_absolute_url(img_url, url)
            if full_url not in images:
                images.append(full_url)

    # Try to extract article:published_time, article:author, etc.
    article_author = soup.find('meta', property='article:author')
    article_published = soup.find('meta', property='article:published_time')

    # Get primary image
    image_url = images[0] if images else None

    # Extract site name with fallbacks
    site_name = None
    if og_site_name:
        site_name = og_site_name.get('content')
    if not site_name:
        # Try application-name meta tag
        app_name = soup.find('meta', attrs={'name': 'application-name'})
        site_name = app_name.get('content') if app_name else None
    if not site_name:
        # Fallback to hostname
        parsed = urlparse(url)
        site_name = parsed.netloc.replace('www.', '').title()

    # Clean up text
    if title:
        title = title.strip()[:500]
    if description:
        description = description.strip()[:1000]

    result['title'] = title
    result['description'] = description
    result['image_url'] = image_url
    result['images'] = images[:5] if images else None
    result['site_name'] = site_name
    result['author'] = article_author.get('content') if article_author else None
    result['published_time'] = article_published.get('content') if article_published else None
    result['platform'] = 'article'
    result['embeddable'] = False
    result['embed_html'] = None

    return result

def make_absolute_url(url: str, base_url: str) -> str:
    """Convert relative URL to absolute"""
    if url.startswith('http'):
        return url
    
    parsed = urlparse(base_url)
    base = f"{parsed.scheme}://{parsed.netloc}"
    
    if url.startswith('/'):
        return base + url
    else:
        return urljoin(base_url, url)

def fetch_link_preview(url: str, timeout: int = DEFAULT_TIMEOUT) -> Optional[Dict[str, Optional[str]]]:
    """
    Fetch link preview with oEmbed support for embeddable platforms
    Returns dict with title, description, image_url, embed_html, embeddable, etc.
    """
    # Step 1: Try oEmbed for embeddable platforms
    if is_embeddable_platform(url):
        oembed_data = fetch_oembed(url, timeout)
        if oembed_data:
            # For Twitter, try to get better image from HTML if oEmbed didn't provide one
            if is_twitter_url(url) and not oembed_data.get('image_url'):
                try:
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    }
                    response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        og_image = soup.find('meta', property='og:image')
                        twitter_image = soup.find('meta', attrs={'name': 'twitter:image'})
                        if og_image:
                            oembed_data['image_url'] = make_absolute_url(og_image.get('content'), url)
                        elif twitter_image:
                            oembed_data['image_url'] = make_absolute_url(twitter_image.get('content'), url)
                except:
                    pass  # If HTML fetch fails, just use oEmbed data without image
            
            return oembed_data
    
    # Step 2: For non-embeddable or if oEmbed failed, scrape HTML
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
        response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        response.raise_for_status()
        
        # Check content type
        content_type = response.headers.get('content-type', '').lower()
        if 'text/html' not in content_type:
            # Not HTML, return basic info
            parsed = urlparse(url)
            return {
                'title': None,
                'description': None,
                'image_url': None,
                'site_name': parsed.netloc.replace('www.', ''),
                'platform': 'other',
                'embeddable': False,
                'embed_html': None
            }
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Route to platform-specific extractors
        if is_twitter_url(url):
            return extract_twitter_content_from_html(soup, url)
        elif is_reddit_url(url):
            return extract_reddit_content(soup, url)
        elif is_instagram_url(url):
            # Instagram requires login, return basic info
            return {
                'title': 'Instagram Post',
                'description': 'View on Instagram (login may be required)',
                'image_url': None,
                'site_name': 'Instagram',
                'author': None,
                'platform': 'instagram',
                'embeddable': False,
                'embed_html': None
            }
        else:
            return extract_article_content(soup, url)
        
    except requests.exceptions.Timeout:
        print(f"⚠️ Timeout fetching preview for {url} (timeout={timeout}s)")
        return None
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Request error fetching preview for {url}: {e}")
        return None
    except Exception as e:
        print(f"⚠️ Error fetching preview for {url}: {e}")
        return None
