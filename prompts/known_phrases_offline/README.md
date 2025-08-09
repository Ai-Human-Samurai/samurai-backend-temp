# 📦 prompts/known_phrases_offline — Offline Fallback Phrases for Samurai

## Purpose
This module contains **fallback phrases** that Samurai can use when GPT or the backend server is completely unavailable.  
It allows the assistant to maintain **basic introduction, minimal interaction, and a sense of presence** even when there is no internet connection.

## How It Works
1. On system startup or when a response is requested:
   - If **online** → use standard prompts (`load_prompts(lang)`).
   - If **offline** → use this package (`known_phrases_offline/`).
2. Responses are chosen randomly:
   ```python
   random.choice(PROMPT["known_phrases_offline"][key])