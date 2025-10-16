import requests
from datetime import datetime

# Tokens típicos devueltos por Chess.com en el campo "result" del jugador
WIN_TOKENS = {"win"}
LOSS_TOKENS = {"checkmated", "resigned", "timeout", "lose", "abandoned", "mate", "flagged"}

# Si quieres contar empates, añade aquí los tokens y devuelve "Empate"
DRAW_TOKENS = {"agreed", "repetition", "stalemate", "insufficient", "timevsinsufficient"}

def map_result_for_player(game_json: dict, username: str) -> str | None:
    """
    Devuelve "Ganada", "Perdida" o None (empate/otros) para el 'username' dado.
    """
    u = username.lower()
    white = game_json.get("white", {})
    black = game_json.get("black", {})
    # ¿jugaste con blancas o negras?
    if white.get("username", "").lower() == u:
        my_res = (white.get("result") or "").lower()
        
    
    elif black.get("username", "").lower() == u:
        my_res = (black.get("result") or "").lower()
           
    else:
        return None  # partida de otra persona (no debería pasar)

    if my_res in WIN_TOKENS:
        return "Ganada"
    if my_res in LOSS_TOKENS:
        return "Perdida"
    
    # Si quieres guardar empates, desconecta
    # if my_res in DRAW_TOKENS:
    #     return "Empate"
    return None # ignorar empates/otros por ahora
