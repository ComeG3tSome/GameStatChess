import requests
from datetime import datetime

# Typical tokens returned by Chess.com in the player's "result" field.
WIN_TOKENS = {"win"}
LOSS_TOKENS = {"checkmated", "resigned", "timeout", "lose", "abandoned", "mate", "flagged"}

# If you want to count ties, add the tokens here and return "Tie".
DRAW_TOKENS = {"agreed", "repetition", "stalemate", "insufficient", "timevsinsufficient"}

def map_result_for_player(game_json: dict, username: str) -> str | None:
    """
    Return "Win", "Loss", or None (draw/other) for the given 'username'
    """
    u = username.lower()
    white = game_json.get("white", {})
    black = game_json.get("black", {})
    # Did you play with white or black?
    if white.get("username", "").lower() == u:
        my_res = (white.get("result") or "").lower()
        
    
    elif black.get("username", "").lower() == u:
        my_res = (black.get("result") or "").lower()
           
    else:
        return None  # another person's game (this shouldn't happen)

    if my_res in WIN_TOKENS:
        return "Win"
    if my_res in LOSS_TOKENS:
        return "Loss"
    
    # If you want to save draws, uncomment
    # if my_res in DRAW_TOKENS:
    #     return "Draw"
    return None # ignore draws/others for now
