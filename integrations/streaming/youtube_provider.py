import urllib.parse


class YouTubeProvider:
    """Minimal provider: returns a YouTube search URL for a query."""

    NAME = "youtube"

    @staticmethod
    def search_play_url(query: str) -> str:
        q = urllib.parse.quote_plus(query)
        return f"https://www.youtube.com/results?search_query={q}"