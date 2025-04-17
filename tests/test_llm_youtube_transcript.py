import llm
import pytest
from llm_youtube_transcript import load_youtube_transcript

TEST_VIDEO_ID = "dQw4w9WgXcQ"
TEST_VIDEO_URL = f"https://www.youtube.com/watch?v={TEST_VIDEO_ID}"
TEST_TRANSCRIPT_CONTENT = "[Music] we're no strangers to love you know the rules and so do I I full commitments while I'm thinking of you wouldn't get this from any other guy I just want to tell you how I'm feeling got to make you understand Never Going To Give You Up never going to let you down never going to run around and desert you never going to make you cry never going to say goodbye never going to tell a lie and hurt you we've known each other for so long your heart's been aching but your to sh to say it inside we both know what's been going on we know the game and we're going to playing and if you ask me how I'm feeling don't tell me you're too my you see Never Going To Give You Up never going to let you down never to run around and desert you never going to make you cry never going to say goodbye never going to tell a lie and hurt you never going to give you up never going to let you down never going to run around and desert you never going to make you cry never going to sing goodbye going to tell a lie and hurt you give you give you going to give going to give you going to give going to give you we've known each other for so long your heart's been aching but you're too sh to say inside we both know what's been going on we the game and we're going to play it I just want to tell you how I'm feeling got to make you understand Never Going To Give You Up never going to let you down never going to run around and desert you never going to make you cry never going to say goodbye never going to tell you my and Hurt You Never Going To Give You Up never going to let you down never going to run around and desert you never going to make you C never going to say goodbye never going to tell and Hur You Never Going To Give You Up never going to let you down never going to run around and desert you never going to make you going to [Music] goodbye"  # noqa: E501

VIDEO_TITLE = "Rick Astley - Never Gonna Give You Up (Official Music Video)"
EXAMPLE_API_RESPONSE = {
    "content": TEST_TRANSCRIPT_CONTENT,
    "metadata": {
        "title": VIDEO_TITLE,
        "duration": 212,
        "channel_name": "Rick Astley",
    },
    "source": TEST_VIDEO_URL,
}


@pytest.fixture
def mock_env(monkeypatch):
    """Fixture to mock the SUPADATA_API_KEY environment variable."""
    monkeypatch.setenv("SUPADATA_API_KEY", "test-api-key")


def test_load_youtube_transcript_with_video_id(httpx_mock, mock_env):
    """Test loading transcript using just the video ID."""
    httpx_mock.add_response(json=EXAMPLE_API_RESPONSE)

    fragment = load_youtube_transcript(TEST_VIDEO_ID)

    assert isinstance(fragment, llm.Fragment)
    assert fragment.source == TEST_VIDEO_URL
    assert str(fragment) == TEST_TRANSCRIPT_CONTENT


@pytest.mark.httpx
def test_load_youtube_transcript_with_full_url(httpx_mock, mock_env):
    """Test loading transcript using the full video URL."""
    httpx_mock.add_response(json=EXAMPLE_API_RESPONSE)

    fragment = load_youtube_transcript(TEST_VIDEO_URL)

    assert isinstance(fragment, llm.Fragment)
    assert fragment.source == TEST_VIDEO_URL
    assert str(fragment) == TEST_TRANSCRIPT_CONTENT


def test_load_youtube_transcript_invalid_id():
    """Test loading transcript with an invalid video ID format."""
    invalid_id = "invalid-id-too-long"
    expected_error = f"Invalid YouTube video ID format: '{invalid_id}'"
    with pytest.raises(ValueError, match=expected_error):
        load_youtube_transcript(invalid_id)


def test_load_youtube_transcript_missing_api_key(monkeypatch):
    """Test loading transcript when API key is missing."""
    monkeypatch.delenv("SUPADATA_API_KEY", raising=False)
    expected_error = "SUPADATA_API_KEY environment variable not set."
    with pytest.raises(ValueError, match=expected_error):
        load_youtube_transcript(TEST_VIDEO_ID)


def test_load_youtube_transcript_api_error(httpx_mock, mock_env):
    """Test handling of API errors from Supadata."""
    error_response = {"detail": "Authentication credentials were not provided."}
    httpx_mock.add_response(json=error_response, status_code=401)

    with pytest.raises(ValueError) as excinfo:
        load_youtube_transcript(TEST_VIDEO_ID)

    expected_error_msg = f"Error fetching transcript for '{TEST_VIDEO_URL}'"
    assert expected_error_msg in str(excinfo.value)
    assert "HTTPStatusError" in str(excinfo.value)
    assert "401 Unauthorized" in str(excinfo.value)
    assert f"API Response: {error_response}" in str(excinfo.value)


@pytest.mark.httpx
def test_load_youtube_transcript_api_non_json_error(httpx_mock, mock_env):
    """Test handling of non-JSON API error responses."""
    error_text = "<html><body>Gateway Timeout</body></html>"
    httpx_mock.add_response(
        text=error_text, status_code=504, headers={"content-type": "text/html"}
    )

    with pytest.raises(ValueError) as excinfo:
        load_youtube_transcript(TEST_VIDEO_ID)

    expected_error_msg = f"Error fetching transcript for '{TEST_VIDEO_URL}'"
    assert expected_error_msg in str(excinfo.value)
    assert "HTTPStatusError" in str(excinfo.value)
    assert "504 Gateway Timeout" in str(excinfo.value)
    assert f"API Response: {error_text}" in str(excinfo.value)


@pytest.mark.httpx
def test_load_youtube_transcript_api_unexpected_content_type(httpx_mock, mock_env):
    """Test handling of unexpected content type in successful response."""
    httpx_mock.add_response(
        text="This is not JSON",
        status_code=200,
        headers={"content-type": "text/plain"},
    )

    with pytest.raises(ValueError) as excinfo:
        load_youtube_transcript(TEST_VIDEO_ID)

    assert "Unexpected content type: text/plain" in str(excinfo.value)
    assert "Expected JSON" in str(excinfo.value)
    assert "Response text: This is not JSON" in str(excinfo.value)


@pytest.mark.httpx
def test_load_youtube_transcript_api_missing_content_key(httpx_mock, mock_env):
    """Test handling when 'content' key is missing in API response."""
    incomplete_response = {
        "metadata": {},
        "source": TEST_VIDEO_URL,
    }  # Missing 'content'
    httpx_mock.add_response(json=incomplete_response)

    with pytest.raises(ValueError) as excinfo:
        load_youtube_transcript(TEST_VIDEO_ID)

    expected_error_msg = "Could not find 'content' in Supadata API response"
    assert expected_error_msg in str(excinfo.value)
    assert f"Response JSON: {incomplete_response}" in str(excinfo.value)
