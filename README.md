# DotAI

Proyecto personal de coaching y analytics para Dota 2 basado en Game State Integration (GSI).

## Stack

- Python
- FastAPI
- PostgreSQL
- Streamlit

## Estado actual

- Captura de partidas mediante GSI
- Ingestión de MATCH
- Ingestión de SNAPSHOT
- Ingestión de ABILITY_EVENT
- ITEM_EVENT en desarrollo

## Arquitectura

GSI → FastAPI → JSONL → PostgreSQL → Analytics → Dashboard