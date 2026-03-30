import httpx


async def fetch_image(url: str) -> tuple[bytes, str]:
    """Fetch an image from a URL and return (content, content_type)."""
    async with httpx.AsyncClient(
        follow_redirects=True,
        timeout=10.0,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        },
    ) as client:
        response = await client.get(url)
        response.raise_for_status()
        content_type = response.headers.get("content-type", "image/jpeg")
        return response.content, content_type
