import llm
import httpx
import os
import re

REQUEST_TIMEOUT = 60
SUPADATA_API_URL = "https://api.supadata.ai/v1/youtube/transcript"
USER_AGENT = "llm-youtube-transcript-plugin/0.1"


@llm.hookimpl
def register_fragment_loaders(register):
    """Register the 'yt' fragment loader."""
    register("yt", load_youtube_transcript)


def load_youtube_transcript(input_string: str) -> llm.Fragment:
    """
    Load a transcript from a YouTube video URL or video ID using
    the Supadata API.

    Takes the part after 'yt:' as input.
    Example inputs:
    - 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
    - 'dQw4w9WgXcQ'
    """
    youtube_id_regex = r"^[a-zA-Z0-9_-]{11}$"
    is_http = input_string.startswith("http://")
    is_https = input_string.startswith("https://")
    is_full_url = is_http or is_https

    if is_full_url:
        url_string = input_string
    else:
        if not re.match(youtube_id_regex, input_string):
            raise ValueError(
                f"Invalid YouTube video ID format: '{input_string}'. "
                "Expected 11 characters (letters, numbers, -, _)."
            )
        video_id = input_string
        base_url = "https://www.youtube.com/watch?v="
        url_string = f"{base_url}{video_id}"

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
