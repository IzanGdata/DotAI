CREATE TABLE match (
    match_id            TEXT PRIMARY KEY,
    file_name           TEXT,
    hero_name           TEXT,
    start_datetime      TIMESTAMP,
    duration_seconds    INTEGER,
    win_team            TEXT
);

CREATE TABLE snapshot (
    snapshot_id         SERIAL PRIMARY KEY,
    match_id            TEXT REFERENCES match(match_id),
    game_time           INTEGER,
    clock_time          INTEGER,
    daytime             BOOLEAN,
    nightstalker_night  BOOLEAN,
    radiant_score       INTEGER,
    dire_score          INTEGER,
    team_name           TEXT,
    gold                INTEGER,
    gold_reliable       INTEGER,
    gold_unreliable     INTEGER,
    kills               INTEGER,
    deaths              INTEGER,
    assists             INTEGER,
    last_hits           INTEGER,
    denies              INTEGER,
    gpm                 INTEGER,
    xpm                 INTEGER,
    health              INTEGER,
    max_health          INTEGER,
    health_percent      INTEGER,
    mana                INTEGER,
    max_mana            INTEGER,
    mana_percent        INTEGER,
    level               INTEGER,
    xp                  INTEGER,
    alive               BOOLEAN,
    respawn_seconds     INTEGER,
    xpos                INTEGER,
    ypos                INTEGER,
    buyback_cost        INTEGER,
    buyback_cooldown    INTEGER
);

CREATE TABLE item_event (
    event_id            SERIAL PRIMARY KEY,
    match_id            TEXT REFERENCES match(match_id),
    game_time           INTEGER,
    item_name           TEXT,
    event_type          TEXT
);

CREATE TABLE ability_event (
    event_id            SERIAL PRIMARY KEY,
    match_id            TEXT REFERENCES match(match_id),
    game_time           INTEGER,
    ability_name        TEXT,
    level_new           INTEGER
);