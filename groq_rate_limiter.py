import time
import random
import threading


# ============================================================
# GROQ RATE LIMIT CONFIGURATION
# ============================================================

# Observed organization limit from Groq:
# 12,000 tokens per minute.
#
# We intentionally target a much lower ceiling to provide
# a safety margin for the contest/demo environment.

SAFE_TPM_LIMIT = 7000

# Convert TPM into tokens-per-second.
SAFE_TOKENS_PER_SECOND = SAFE_TPM_LIMIT / 60

# Shared state across all agent calls in this Python process.
_lock = threading.Lock()

_window_start = time.monotonic()
_tokens_reserved = 0


# ============================================================
# TOKEN RESERVATION
# ============================================================

def reserve_tokens(estimated_tokens):
    """
    Reserve an estimated number of tokens before making
    a Groq request.

    Requests are delayed when the estimated usage would
    exceed the safe per-minute budget.
    """

    global _window_start
    global _tokens_reserved

    if not isinstance(estimated_tokens, int):
        raise ValueError(
            "estimated_tokens must be an integer."
        )

    if estimated_tokens <= 0:
        raise ValueError(
            "estimated_tokens must be greater than zero."
        )

    with _lock:

        while True:

            now = time.monotonic()

            elapsed = now - _window_start

            # Start a fresh minute window.
            if elapsed >= 60:

                _window_start = now
                _tokens_reserved = 0
                elapsed = 0

            projected_usage = (
                _tokens_reserved
                + estimated_tokens
            )

            if projected_usage <= SAFE_TPM_LIMIT:

                _tokens_reserved += estimated_tokens

                print(
                    f"[RATE LIMIT] Reserved "
                    f"{estimated_tokens} tokens "
                    f"({ _tokens_reserved }/"
                    f"{SAFE_TPM_LIMIT} TPM)"
                )

                return

            # Remaining time in the current window.
            wait_time = 60 - elapsed

            print(
                f"[RATE LIMIT] Token budget reached. "
                f"Waiting {wait_time:.1f}s..."
            )

            time.sleep(wait_time)

            _window_start = time.monotonic()
            _tokens_reserved = 0


# ============================================================
# 429 RETRY DELAY
# ============================================================

def retry_delay(attempt, server_delay=None):
    """
    Calculate a safe delay after a 429 response.

    If Groq supplies a retry delay, prefer it.

    Otherwise use exponential backoff with jitter.
    """

    if server_delay is not None:

        try:

            delay = float(server_delay)

            if delay > 0:
                return delay

        except (TypeError, ValueError):
            pass

    # Exponential backoff:
    #
    # attempt 0 → ~2s
    # attempt 1 → ~4s
    # attempt 2 → ~8s
    # attempt 3 → ~16s
    #
    # Maximum 30 seconds.

    base_delay = min(
        2 ** (attempt + 1),
        30
    )

    jitter = random.uniform(
        0.5,
        1.5
    )

    return base_delay + jitter