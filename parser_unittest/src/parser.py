
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional


class ForumParser:

    DEFAULT_HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    }

    def __init__(self, headers: Optional[Dict[str, str]] = None, timeout: int = 10):
        self.headers = headers or self.DEFAULT_HEADERS
        self.timeout = timeout

    # ---------- core ----------
    def parse_html(self, html: str) -> List[Dict[str, Any]]:
        """Парсит HTML-строку. Вынесен отдельно, чтобы тесты не зависели от сети."""
        soup = BeautifulSoup(html, "lxml")
        posts = soup.select("div.post")

        result: List[Dict[str, Any]] = []
        for post in posts:
            post_id = post.get("data-post-id")
            if post_id is None:
                continue

            author_el = post.select_one("div.author")
            content_el = post.select_one("div.content")
            if not author_el or not content_el:
                continue

            result.append({
                "id": int(post_id),
                "name": author_el.get_text(strip=True),
                # decode_contents() — внутренности тега, без самого <div class="content">
                "message": content_el.decode_contents(),
            })
        return result

    @staticmethod
    def convert_reddit_payload(payload: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        def convert(raw: Dict[str, Any]) -> Dict[str, Any]:
            d = raw["data"]
            text = d.get("selftext") or d.get("body") or d.get("title") or ""
            return {
                "id": int(d["id"], 36),
                "name": d.get("author") or "[deleted]",
                "message": text[:8000],
            }

        result = [convert(payload[0]["data"]["children"][0])]  # сам пост
        for item in payload[1]["data"]["children"]:  # комментарии
            if item.get("kind") == "t1":
                result.append(convert(item))
        return result

    def parse_reddit_post(self, url: str) -> List[Dict[str, Any]]:
        if ".json" not in url:
            url = url.rstrip("/") + ".json"

        headers = {"User-Agent": "python:ptpm-lab:v1.0 (by /u/ВАШ_ЛОГИН)"}

        response = requests.get(url, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        return self.convert_reddit_payload(response.json())

    def parse_page(self, url: str) -> List[Dict[str, Any]]:
        """Скачивает страницу и парсит её."""
        response = requests.get(url, headers=self.headers, timeout=self.timeout)
        response.raise_for_status()
        return self.parse_html(response.text)

    # ---------- persistence ----------
    def save_to_db(self, parsed_data: List[Dict[str, Any]], repository) -> int:

        saved = 0
        for item in parsed_data:
            try:
                repository.add(item["id"], item["name"], item["message"])
                saved += 1
            except (ValueError, TypeError, KeyError):
                continue
        return saved