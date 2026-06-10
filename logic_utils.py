"""Game logic utilities for the Glitchy Guesser Streamlit application.

This module provides helper functions to handle difficulty scaling, user input
parsing, game boundary validations, guessing metrics, and dynamic scoring rules.
"""


def get_range_for_difficulty(difficulty: str) -> tuple[int, int]:
    """Determine the inclusive numeric guessing range based on game difficulty.

    Args:
        difficulty: A string representation of the game mode. Expected values
            are "Easy", "Normal", or "Hard".

    Returns:
        A tuple of two integers representing the lower and upper bounds of
        the guessing range, inclusive. Defaults to (1, 100) if an unknown
        difficulty is provided.
    """
    if difficulty == "Easy":
        return 1, 20
    if difficulty == "Normal":
        return 1, 50
    if difficulty == "Hard":
        return 1, 100
    return 1, 100


def parse_guess(raw: str, low: int, high: int) -> tuple[bool, int | None, str | None]:
    """Strictly parse and validate a raw string input into a valid game guess.

    This function strips whitespace, enforces a strict whole-number requirement 
    (rejecting decimals entirely to prevent silent rounding), and verifies that 
    the resulting integer lies within the designated game boundaries.

    Args:
        raw: The unprocessed text input captured from the user interface.
        low: The inclusive minimum valid value permitted for the current game.
        high: The inclusive maximum valid value permitted for the current game.

    Returns:
        A tuple containing three elements:
            - ok (bool): True if the input was successfully converted and fits 
              within the range bounds; False otherwise.
            - guess_int (int | None): The parsed integer value if successful; 
              None if parsing or validation failed.
            - error_message (str | None): A user-friendly error message if 
              validation failed; None if the input is perfectly valid.
    """
    if raw is "" or not raw.strip():
        return False, None, "Please enter a guess."

    clean_raw = raw.strip()

    if "." in clean_raw:
        return (
            False,
            None,
            f"Decimals are not allowed. Please enter a whole number between {low} and {high}."
        )

    try:
        value = int(clean_raw)
    except ValueError:
        return False, None, "That is not a valid number. Please enter digits only."

    if value < low or value > high:
        return False, None, f"Out of bounds! Your guess must be between {low} and {high}."

    return True, value, None


def check_guess(guess: int, secret: int) -> tuple[str, str]:
    """Compare a processed guess against the secret number to evaluate game state.

    Args:
        guess: The validated integer guessed by the player.
        secret: The active target integer the player is attempting to guess.

    Returns:
        A tuple containing two elements:
            - outcome (str): A keyword tracking game state progression. Possible
              values include "Win", "Too High", or "Too Low".
            - message (str): A user-friendly feedback text string displaying 
              hints and accompanying emojis.
    """
    try:
        secret_value = int(secret)
    except (TypeError, ValueError):
        secret_value = secret

    if guess == secret_value:
        return "Win", "🎉 Correct!"
    if guess > secret_value:
        return "Too High", "📉 Go LOWER!"
    return "Too Low", "📈 Go HIGHER!"


def update_score(
    current_score: int,
    outcome: str,
    attempt_number: int,
    current_diff: int | None = None,
    prev_diff: int | None = None
) -> int:
    """Calculate and update the player's cumulative score using trend metrics.

    Scoring is calculated dynamically based on the following rules:
        - A "Win" awards a scaling completion bonus based on remaining attempts,
          guaranteeing a baseline floor of 10 points.
        - The first guess of a round maintains the score baseline.
        - Subsequent incorrect guesses award +5 points if the player moved closer
          to the secret number ("warmer"), or penalize -5 points if they moved
          further away or stagnated ("colder").

    Args:
        current_score: The player's existing score baseline before this submission.
        outcome: The evaluative status from the last check ("Win", "Too High", etc).
        attempt_number: Total count of valid attempts made by the player so far.
        current_diff: The absolute mathematical distance between the current guess
            and the secret target. Optional.
        prev_diff: The absolute mathematical distance between the previous valid
            guess and the secret target. Optional.

    Returns:
        The updated total score integer reflecting bonuses or penalizations.
    """
    if outcome == "Win":
        points = 100 - 10 * (attempt_number + 1)
        return current_score + max(points, 10)

    # If there is no previous guess context, score doesn't drift
    if current_diff is None or prev_diff is None:
        return current_score

    # Evaluate the directional movement of the hot/cold trend line
    if current_diff < prev_diff:
        return current_score + 5
    else:
        return current_score - 5