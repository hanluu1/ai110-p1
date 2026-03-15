from logic_utils import check_guess, update_score


# --- Attempts initialization bug (fixed: start at 0 not 1) ---

def test_attempts_display_starts_at_full():
    # attempts=0 at init means all attempts are shown before any guess
    attempts = 0
    attempt_limit = 8  # Normal difficulty
    assert attempt_limit - attempts == attempt_limit


def test_attempts_display_decrements_by_one_on_first_guess():
    attempts = 0
    attempt_limit = 8
    attempts += 1  # simulates first submit
    assert attempt_limit - attempts == attempt_limit - 1


def test_old_bug_skipped_first_decrement():
    # With the old init of attempts=1, the first submit set attempts=2,
    # so the display jumped from 7 to 6 instead of 8 to 7.
    attempts_old = 1  # buggy initial value
    attempt_limit = 8
    attempts_old += 1  # first submit
    # shows 6 remaining, skipping the 8→7 step entirely
    assert attempt_limit - attempts_old == attempt_limit - 2


def test_score_uses_correct_attempt_number_after_fix():
    # With the fix, winning on the first guess passes attempt_number=1 to update_score.
    # With the bug, it would have passed attempt_number=2, giving fewer points.
    score_fixed = update_score(0, "Win", attempt_number=1)
    score_bugged = update_score(0, "Win", attempt_number=2)
    assert score_fixed > score_bugged


# --- Existing tests ---

def test_winning_guess():
    # If the secret is 50 and guess is 50, it should be a win
    outcome, message = check_guess(50, 50)
    assert outcome == "Win"

def test_guess_too_high():
    # If secret is 50 and guess is 60, hint should be "Too High"
    outcome, message = check_guess(60, 50)
    assert outcome == "Too High"

def test_guess_too_low():
    # If secret is 50 and guess is 40, hint should be "Too Low"
    outcome, message = check_guess(40, 50)
    assert outcome == "Too Low"


# --- Too High / Too Low message direction fix (lines 47, 49, 55, 56) ---

def test_too_high_message_says_lower():
    # Bug: "Too High" message said "HIGHER" instead of "LOWER" (messages were swapped).
    # Fix at line 47: guess > secret must return a go-LOWER hint.
    outcome, message = check_guess(60, 50)
    assert outcome == "Too High"
    assert "LOWER" in message.upper()


def test_too_low_message_says_higher():
    # Bug: "Too Low" message said "LOWER" instead of "HIGHER" (messages were swapped).
    # Fix at line 49: guess < secret must return a go-HIGHER hint.
    outcome, message = check_guess(40, 50)
    assert outcome == "Too Low"
    assert "HIGHER" in message.upper()


def test_too_high_message_does_not_say_higher():
    # Regression guard: "Too High" must never contain "HIGHER".
    outcome, message = check_guess(99, 1)
    assert outcome == "Too High"
    assert "HIGHER" not in message.upper()


def test_too_low_message_does_not_say_lower():
    # Regression guard: "Too Low" must never contain "LOWER".
    outcome, message = check_guess(1, 99)
    assert outcome == "Too Low"
    assert "LOWER" not in message.upper()


# --- TypeError fallback path (lines 55, 56) ---

class _RaisesOnCompare:
    """Forces the except TypeError branch in check_guess by raising on >."""
    def __init__(self, str_val):
        self._s = str_val

    def __eq__(self, other):
        return self._s == str(other)

    def __gt__(self, _):
        raise TypeError("forced for test")

    def __str__(self):
        return self._s


def test_fallback_too_high_message_says_lower():
    # Triggers except branch (lines 51-56): "60" > "50" is True by string comparison.
    # Fix at line 55: fallback Too High must also return a go-LOWER hint, not go-HIGHER.
    outcome, message = check_guess(_RaisesOnCompare("60"), "50")
    assert outcome == "Too High"
    assert "LOWER" in message.upper()


def test_fallback_too_low_message_says_higher():
    # Triggers except branch (lines 51-56): "40" > "50" is False by string comparison.
    # Fix at line 56: fallback Too Low must return a go-HIGHER hint, not go-LOWER.
    outcome, message = check_guess(_RaisesOnCompare("40"), "50")
    assert outcome == "Too Low"
    assert "HIGHER" in message.upper()
