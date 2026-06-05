import os
import json
from datetime import datetime
from fastapi import FastAPI, Request

app = FastAPI()
current_game_state = None
current_file = None
current_match_id = None

MATCHES_DIR = "raw_matches"

if not os.path.exists(MATCHES_DIR):
    os.makedirs(MATCHES_DIR)

@app.post("/")
async def receive_gsi(data:dict):
    global current_game_state
    global current_file
    global current_match_id

    # Obtener game state
    game_state = data.get("map", {}).get("game_state")

    if not game_state:
        return {"status": "no_game_state"}
    
    # Detectar inicio de partida
    if game_state == "DOTA_GAMERULES_STATE_GAME_IN_PROGRESS" and current_file is None:

        hero_name = data.get("hero",{}).get("name", "unknown_hero")
        hero_name = hero_name.replace("npc_dota_hero_","")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        current_match_id = f"{timestamp}_{hero_name}"

        file_path = os.path.join(MATCHES_DIR, f"{current_match_id}.jsonl")

        current_file = open(file_path, "a", encoding="utf-8")

        print(f"🟢 Nueva partida detectada: {current_match_id}")

    # Si la partida esta en progreso -> guardar snapshot
    if game_state == "DOTA_GAMERULES_STATE_GAME_IN_PROGRESS" and current_file:
        current_file.write(json.dumps(data) + "\n")
        current_file.flush()

    POST_GAME_BUFFER = 10  # snapshots extra a capturar después del POST_GAME
    post_game_counter = 0
    post_game_detected = False
    
    if game_state == "DOTA_GAMERULES_STATE_POST_GAME":
            if not post_game_detected:
                post_game_detected = True
                post_game_counter = 0
                print(f"⚠️ Post game detectado, capturando {POST_GAME_BUFFER} snapshots más...")

            post_game_counter += 1

            if post_game_counter >= POST_GAME_BUFFER:
                print(f"🔴 Partida finalizada: {current_match_id}")
                current_file.close()
                current_file = None
                current_match_id = None
                post_game_detected = False
                post_game_counter = 0
    
    return {"status": "ok"}