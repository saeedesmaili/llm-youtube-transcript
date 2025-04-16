import llm
import httpx
import os

REQUEST_TIMEOUT = 60
SUPADATA_API_URL = "https://api.supadata.ai/v1/youtube/transcript"
USER_AGENT = "llm-youtube-transcript-plugin/0.1"


@llm.hookimpl
def register_fragment_loaders(register):
    """Register the 'yt' fragment loader."""
    register("yt", load_youtube_transcript)


def load_youtube_transcript(url_string: str) -> llm.Fragment:
    """
    Load a transcript from a YouTube video URL using the Supadata API.

    Takes the part after 'yt:' as input.
    Example input: 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
    """
    api_key = os.environ.get("SUPADATA_API_KEY")
    if not api_key:
        raise ValueError(
            "SUPADATA_API_KEY environment variable not set. "
            "Get a key from https://supadata.ai/"
        )

    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
        "x-api-key": api_key,
    }

    params = {
        "url": url_string,
        "text": "true",  # Request plain text transcript
    }

    try:
        response = httpx.get(
            SUPADATA_API_URL,
            params=params,
            headers=headers,
            timeout=REQUEST_TIMEOUT,
            follow_redirects=True,
        )
        response.raise_for_status()

        # Check content type before parsing JSON
        content_type = response.headers.get("content-type", "")
        if "application/json" not in content_type:
            error_msg = (
                f"Unexpected content type: {content_type}. Expected JSON. "
                f"Response text: {response.text}"
            )
            raise ValueError(error_msg)

        data = response.json()

        content = data.get("content")
        if content is None:
            error_msg = (
                "Could not find 'content' in Supadata API response: "
                f"Response JSON: {data}"
            )
            raise ValueError(error_msg)

    except Exception as exc:
        error_msg = (
            f"Error fetching transcript for '{url_string}'. "
            f"Error: {exc.__class__.__name__}: {exc}"
        )
        if isinstance(exc, httpx.HTTPStatusError):
            try:
                response_details = exc.response.json()
            except Exception:
                response_details = exc.response.text
            error_msg += f" API Response: {response_details}"

        raise ValueError(error_msg) from exc

    return llm.Fragment(content, source=url_string)
