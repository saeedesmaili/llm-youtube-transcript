# llm-youtube-transcript

[![PyPI](https://img.shields.io/pypi/v/llm-youtube-transcript.svg)](https://pypi.org/project/llm-youtube-transcript/)
[![Changelog](https://img.shields.io/github/v/release/saeedesmaili/llm-youtube-transcript?include_prereleases&label=changelog)](https://github.com/saeedesmaili/llm-youtube-transcript/releases)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/saeedesmaili/llm-youtube-transcript/blob/main/LICENSE)

LLM plugin for fetching YouTube video transcripts.

This plugin fetches the text transcript of a YouTube video using the [Supadata API](https://supadata.ai/documentation/youtube/get-transcript) and makes it available as an LLM fragment.

For background on LLM fragments:

- [Fragments - LLM Documentation](https://llm.datasette.io/en/stable/fragments.html)

## Installation

Install this plugin in the same environment as [LLM](https://llm.datasette.io/).

```bash
llm install llm-youtube-transcript
```

## Configuration

This plugin requires a Supadata API key to function. You get 100 requests per month with a free acount.

1.  Sign up at [Supadata.ai](https://supadata.ai/) and get your API key.
2.  Set the API key as an environment variable named `SUPADATA_API_KEY`:

    ```bash
    export SUPADATA_API_KEY=your_api_key_here
    ```

    You can add this line to your shell profile (e.g., `~/.bashrc`, `~/.zshrc`) to make it persistent across sessions.

## Usage

You can feed the transcript of a YouTube video into LLM using the `yt:` [fragment](https://llm.datasette.io/en/stable/fragments.html) prefix followed by either the full video URL or just the video ID.

Make sure you have set the `SUPADATA_API_KEY` environment variable first.

**Note:** If your YouTube URL contains special characters (like `?` or `&`), you **must** enclose the entire fragment identifier (e.g., `yt:https://...`) in single or double quotes on the command line. This prevents your shell from misinterpreting the URL or ID.

For example:

```bash
llm -f yt:https://youtu.be/dQw4w9WgXcQ 'Summarize this transcript'

# Fetch transcript using the full YouTube video URL (note the quotes)
llm -f 'yt:https://www.youtube.com/watch?v=dQw4w9WgXcQ' 'Summarize this transcript'

# Fetch transcript using just the video ID
llm -f yt:dQw4w9WgXcQ 'Summarize this transcript'
```

The plugin will call the Supadata API to retrieve the plain text transcript of the specified video. If the API key is missing or invalid, or if the transcript cannot be fetched, an error will be raised.

## TODO

- [ ] Use `youtube-transcript-api` library instead of Supadata.
- [x] Add support for `yt:VIDEO_ID`.

## Development

To set up this plugin locally, first checkout the code. Then create a new virtual environment:

```bash
cd llm-youtube-transcript
python -m venv venv
source venv/bin/activate
```

Now install the dependencies and test dependencies:

```bash
# Installs llm, httpx, and testing tools like pytest
pip install -e '.[test]'
```

To run the tests:

```bash
python -m pytest
```
