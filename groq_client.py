import os
import time
import random
import threading

from dotenv import load_dotenv
from groq import Groq

from groq_rate_limiter import reserve_tokens


# ============================================================
# LOAD API KEY
# ============================================================

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError(
        "GROQ_API_KEY was not found in .env"
    )


# ============================================================
# GROQ CLIENT
# ============================================================

client = Groq(api_key=api_key)

MODEL_NAME = "groq/compound-mini"

# Keep generated responses bounded so the multi-agent pipeline does not
# consume the entire organization TPM allowance on a single request.
MAX_COMPLETION_TOKENS = 1024


# ============================================================
# RATE LIMIT CONFIGURATION
# ============================================================

MAX_RETRIES = 5

# Additional spacing between successful requests.
# Token reservation remains the primary protection.
MIN_REQUEST_INTERVAL = 15.0

_request_lock = threading.Lock()
_last_request_time = 0.0


# ============================================================
# TOKEN ESTIMATION
# ============================================================

def estimate_tokens(text):
    """
    Conservative approximation of input tokens.

    A rough 4-characters-per-token estimate is used, with a
    minimum reservation so very short requests are not treated
    as free.
    """

    if not isinstance(text, str):
        raise ValueError("Prompt must be a string.")

    estimated = max(
        100,
        (len(text) + 3) // 4
    )

    return estimated


# ============================================================
# SAFE GROQ REQUEST
# ============================================================

def generate_json(prompt):
    """
    Send a JSON-mode request to Groq.

    The request first reserves estimated input tokens through
    groq_rate_limiter.py, then applies additional pacing and
    429 retry/backoff handling.
    """

    global _last_request_time

    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError(
            "Prompt must be a non-empty string."
        )

    estimated_tokens = estimate_tokens(prompt)

    # Reserve input tokens before making the API request.
    # This prevents the application from intentionally sending
    # requests beyond the local safe TPM budget.
    reserve_tokens(estimated_tokens)

    for attempt in range(MAX_RETRIES):

        with _request_lock:

            now = time.monotonic()
            elapsed = now - _last_request_time

            if elapsed < MIN_REQUEST_INTERVAL:

                wait_time = (
                    MIN_REQUEST_INTERVAL - elapsed
                )

                time.sleep(wait_time)

            try:

                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    response_format={
                        "type": "json_object"
                    },
                    max_completion_tokens=MAX_COMPLETION_TOKENS
                )

                _last_request_time = time.monotonic()

                return response.choices[0].message.content

            except Exception as e:

                error_text = str(e)

                # A 413 is a request-size problem, not a
                # transient rate-limit problem. Do not retry it.
                if "413" in error_text:
                    raise

                # Retry only rate-limit failures.
                if "429" not in error_text:
                    raise

                server_delay = None

                marker = "Please try again in "

                if marker in error_text:

                    try:

                        remainder = (
                            error_text
                            .split(marker, 1)[1]
                        )

                        delay_text = (
                            remainder
                            .split("s", 1)[0]
                            .strip()
                        )

                        server_delay = float(
                            delay_text
                        )

                    except (
                        ValueError,
                        IndexError
                    ):

                        server_delay = None

                if server_delay is None:

                    server_delay = min(
                        15 * (2 ** attempt),
                        120
                    )

                server_delay += random.uniform(
                    1.0,
                    3.0
                )

                print(
                    f"[RATE LIMIT] Groq returned 429. "
                    f"Waiting {server_delay:.1f}s "
                    f"before retry "
                    f"{attempt + 1}/{MAX_RETRIES}..."
                )

                time.sleep(server_delay)

    raise RuntimeError(
        f"Groq request failed after "
        f"{MAX_RETRIES} rate-limit retries."
    )
