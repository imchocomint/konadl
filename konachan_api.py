# konachan_api.py
import requests
import os
import shutil

class KonachanAPI:
    # Changed the base URL to yande.re, a known mirror that is more lenient.
    BASE_URL = "https://yande.re/post.json"
    
    def __init__(self):
        # Create a requests session with a custom User-Agent to avoid 403 errors
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def search_images(self, tags, excluded_tags, limit=50):
        # The API uses spaces for inclusive tags and '-' for exclusive tags.
        query_tags = tags.split()
        if excluded_tags:
            query_tags.extend([f"-{tag.strip()}" for tag in excluded_tags.split(',')])

        params = {
            'tags': " ".join(query_tags),
            'limit': limit,
        }
        
        try:
            # Use the session object for the request
            response = self.session.get(self.BASE_URL, params=params)
            response.raise_for_status()  # This will raise an exception for 4xx or 5xx errors
            
            posts = response.json()
            
            # The API returns an empty list for no results, which is a valid JSON
            if not posts:
                return [], None
            
            images = [
                {
                    'id': post.get('id'),
                    'name': f"Post #{post.get('id')}",
                    'author': post.get('author'),
                    'tags': post.get('tags').split(),
                    # The API response has 'file_url' for the full image and 'preview_url' for the thumbnail
                    'download_url': post.get('file_url'),
                    'preview_url': post.get('preview_url'),
                    'file_extension': os.path.splitext(post.get('file_url'))[1] if post.get('file_url') else '.jpg',
                } 
                for post in posts if post.get('file_url')
            ]
            return images, None
        
        except requests.RequestException as e:
            return None, f"Network error: {e}"
        except ValueError as e:
            return None, f"Failed to parse response: {e}"
        except Exception as e:
            return None, f"An unexpected error occurred: {e}"

    def download_image(self, url, save_path):
        try:
            # Use the session object for the request
            response = self.session.get(url, stream=True)
            response.raise_for_status()
            with open(save_path, 'wb') as f:
                shutil.copyfileobj(response.raw, f)
            return True, "Download successful."
        except requests.RequestException as e:
            return False, f"Download failed: {e}"
        except Exception as e:
            return False, f"An unexpected error occurred: {e}"