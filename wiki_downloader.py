import argparse
import os
import time
import requests

BASE_URL = "https://pokemon.fandom.com"
API_ENDPOINT = f"{BASE_URL}/api.php"

def search(query):
    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "format": "json"
    }
    resp = requests.get(API_ENDPOINT, params=params)
    data = resp.json()
    for item in data.get("query", {}).get("search", []):
        print(f"- {item['title']}")

def category(cat):
    title = f"Category:{cat}" if not cat.startswith("Category:") else cat
    params = {
        "action": "query",
        "list": "categorymembers",
        "cmlimit": "max",
        "cmtitle": title,
        "format": "json"
    }
    resp = requests.get(API_ENDPOINT, params=params)
    data = resp.json()
    for item in data.get("query", {}).get("categorymembers", []):
        print(f"- {item['title']}")

def bulk(pages, out_dir, fmt="text"):
    os.makedirs(out_dir, exist_ok=True)
    for index, page in enumerate(pages):
        print(f"Downloading: {page}...")
        params = {
            "action": "query",
            "prop": "extracts",
            "titles": page,
            "format": "json"
        }
        if fmt == "text":
            params["explaintext"] = "1"
        else:
            params = {
                "action": "parse",
                "page": page,
                "prop": "text" if fmt=="html" else "wikitext",
                "format": "json"
            }
        
        try:
            # Bulbapedia and others often block default requests User-Agent
            headers = {"User-Agent": "RAG-Corpus-Builder/1.0 (contact@example.com)"}
            resp = requests.get(API_ENDPOINT, params=params, headers=headers, timeout=10)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            print(f"Error fetching {page}: {e}")
            continue
        
        content = ""
        if fmt == "text":
            pages_data = data.get("query", {}).get("pages", {})
            for page_id, page_info in pages_data.items():
                if "extract" in page_info:
                    content = page_info["extract"]
                    
            if not content:
                # Fallback for wikis (like Fandom) that disable TextExtracts API
                fallback_params = {
                    "action": "parse",
                    "page": page,
                    "prop": "text",
                    "format": "json"
                }
                try:
                    fb_resp = requests.get(API_ENDPOINT, params=fallback_params, headers=headers, timeout=10)
                    fb_data = fb_resp.json()
                    html_content = fb_data.get("parse", {}).get("text", {}).get("*", "")
                    if html_content:
                        import re
                        clean_text = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL)
                        clean_text = re.sub(r'<script[^>]*>.*?</script>', '', clean_text, flags=re.DOTALL)
                        clean_text = re.sub(r'<[^>]+>', ' ', clean_text)
                        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
                        content = clean_text
                except Exception as e:
                    pass
                    
        else:
            parse_data = data.get("parse", {})
            if fmt == "html":
                content = parse_data.get("text", {}).get("*", "")
            else:
                content = parse_data.get("wikitext", {}).get("*", "")
                
        if not content:
            print(f"Warning: No content found for '{page}'. It might be a redirect or misspelled.")
            continue
            
        filename = page.replace(" ", "_").replace("/", "_") + f".{fmt}"
        if fmt == "text": filename = filename.replace(".text", ".txt")
        if fmt == "wikitext": filename = filename.replace(".wikitext", ".wiki")
        
        filepath = os.path.join(out_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        
        # Respect servers
        time.sleep(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")
    
    # Search
    search_parser = subparsers.add_parser("search")
    search_parser.add_argument("query")
    
    # Category
    cat_parser = subparsers.add_parser("category")
    cat_parser.add_argument("category")
    
    # Bulk
    bulk_parser = subparsers.add_parser("bulk")
    bulk_parser.add_argument("pages", nargs="+")
    bulk_parser.add_argument("--dir", default="corpus", help="Output directory")
    bulk_parser.add_argument("--format", default="text", choices=["text", "html", "wikitext"])
    
    args = parser.parse_args()
    
    if args.command == "search":
        search(args.query)
    elif args.command == "category":
        category(args.category)
    elif args.command == "bulk":
        bulk(args.pages, args.dir, args.format)
    else:
        parser.print_help()
