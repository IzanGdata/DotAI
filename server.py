import os
import json
from datetime import datetime
from fastapi import FastAPI, Request

app = FastAPI()
current_game_state = None
current_file = None
current_match_id = None
POST_GAME_BUFFER = 1
post_game_counter = 0
post_game_detected = False

MATCHES_DIR = "raw_matches"

if not os.path.exists(MATCHES_DIR):
    os.makedirs(MATCHES_DIR)

@app.post("/")
async def receive_gsi(data:dict):
    global current_game_state
    global current_file
    global current_match_id
    global post_game_counter
    global post_game_detected

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

    # Si hay partida activa -> guardar snapshot
    if current_file:
         current_file.write(json.dumps(data) + "\n")
         current_file.flush()
    
    if game_state == "DOTA_GAMERULES_STATE_POST_GAME":
            if not post_game_detected:
                post_game_detected = True
                post_game_counter = 0
                print(f"⚠️ Post game detectado, capturando {POST_GAME_BUFFER} snapshots más...")

            post_game_counter += 1

            if post_game_counter >= POST_GAME_BUFFER:
                print(f"🔴 Partida finalizada: {current_match_id}")
                print("Archivo cerrado correctamente")
                current_file.close()
                current_file = None
                current_match_id = None
                post_game_detected = False
                post_game_counter = 0
    
    return {"status": "ok"}