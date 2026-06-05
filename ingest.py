import psycopg2
import json
import os

from config import DB_CONFIG
from datetime import datetime

IGNORED_ABILITIES = {
    "plus_high_five",
    "plus_guild_banner"
}

# Conexion a PostgreSQL
conn = psycopg2.connect(**DB_CONFIG)

cur = conn.cursor()
print("Conexion exitosa")

def ingest_file(filepath):
    filename = os.path.basename(filepath)
    
    # Leer todas las lineas del archivo
    snapshots = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                snapshots.append(json.loads(line))
    
    if not snapshots:
        print("Archivo vacio, saltando.")
        return
    
    print(f"Snapshots leidos: {len(snapshots)}")
    
    known_abilities = {}
    first_snapshot = True

    # Datos del primer snapshot
    first = snapshots[0]
    last = snapshots[-1]
    
    match_id        = first["map"]["matchid"]
    hero_name       = first["hero"]["name"].replace("npc_dota_hero_", "")
    start_datetime  = datetime.fromtimestamp(first["provider"]["timestamp"])
    duration_seconds = last["map"]["game_time"] - first["map"]["game_time"]
    win_team        = last["map"].get("win_team", None)
    if win_team == "none":
        win_team = None

    # Insertar MATCH
    cur.execute("""
        INSERT INTO match (match_id, file_name, hero_name, start_datetime, duration_seconds, win_team)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (match_id) DO NOTHING
    """, (match_id, filename, hero_name, start_datetime, duration_seconds, win_team))
    
    conn.commit()
    print(f"Match insertado: {match_id} | Hero: {hero_name} | Duracion: {duration_seconds}s")

#Insertar SNAPSHOTS
    for snap in snapshots:
        map_data = snap.get("map", {})
        player = snap.get("player", {})
        hero = snap.get("hero", {})

        game_time = map_data.get("game_time")
        clock_time = map_data.get("clock_time")
        daytime = map_data.get("daytime")
        nightstalker_night = map_data.get("nightstalker_night")

        radiant_score = map_data.get("radiant_score")
        dire_score = map_data.get("dire_score")

        team_name = player.get("team_name")

        gold = player.get("gold")
        gold_reliable = player.get("gold_reliable")
        gold_unreliable = player.get("gold_unreliable")

        kills = player.get("kills")
        deaths = player.get("deaths")
        assists = player.get("assists")

        last_hits = player.get("last_hits")
        denies = player.get("denies")

        gpm = player.get("gpm")
        xpm = player.get("xpm")

        health = hero.get("health")
        max_health = hero.get("max_health")
        health_percent = hero.get("health_percent")

        mana = hero.get("mana")
        max_mana = hero.get("max_mana")
        mana_percent = hero.get("mana_percent")

        level = hero.get("level")
        xp = hero.get("xp")

        alive = hero.get("alive")
        respawn_seconds = hero.get("respawn_seconds")

        xpos = hero.get("xpos")
        ypos = hero.get("ypos")

        buyback_cost = hero.get("buyback_cost")
        buyback_cooldown = hero.get("buyback_cooldown")
        cur.execute("""
        INSERT INTO snapshot (match_id, game_time, clock_time, daytime, nightstalker_night, radiant_score, dire_score, team_name, gold, gold_reliable, gold_unreliable, kills, deaths, assists, last_hits, denies, gpm, xpm, health, max_health, health_percent, mana, max_mana, mana_percent, level, xp, alive, respawn_seconds, xpos, ypos, buyback_cost, buyback_cooldown)
        VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT(match_id, game_time) DO NOTHING
        """, (match_id, game_time, clock_time, daytime, nightstalker_night, radiant_score, dire_score, team_name, gold, gold_reliable, gold_unreliable, kills, deaths, assists, last_hits, denies, gpm, xpm, health, max_health, health_percent, mana, max_mana, mana_percent, level, xp, alive, respawn_seconds, xpos, ypos, buyback_cost, buyback_cooldown))

        abilities = snap.get("abilities", {})
        current_abilities = {}
        for ability_key, ability_data in abilities.items():
            ability_name = ability_data.get("name")
            ability_level = ability_data.get("level", 0)

            if not ability_name:
                continue
            
            if ability_name in IGNORED_ABILITIES:
                continue

            current_abilities[ability_name] = ability_level
        
        # Primer snapshot = estado inicial
        if first_snapshot:

            for ability_name, current_level in current_abilities.items():
                known_abilities[ability_name] = current_level

            first_snapshot = False
            continue

        # Comparar contra máximos conocidos
        for ability_name, current_level in current_abilities.items():

            known_level = known_abilities.get(
                ability_name,
                0
            )

            if current_level > known_level:

                cur.execute("""
                INSERT INTO ability_event(match_id, game_time, ability_name, level_new)
                VALUES(%s, %s, %s, %s)
                ON CONFLICT(match_id, game_time, ability_name)
                DO NOTHING
                """,(match_id, game_time, ability_name, current_level))

                known_abilities[ability_name] = current_level

    conn.commit()
    print(f"Ingest completada: {match_id}")



# Procesar todos los archivos en raw_matches
RAW_MATCHES_DIR = "raw_matches"

for filename in os.listdir(RAW_MATCHES_DIR):
    if filename.endswith(".jsonl"):
        filepath = os.path.join(RAW_MATCHES_DIR, filename)
        print(f"\nProcesando: {filename}")
        ingest_file(filepath)

cur.close()
conn.close()