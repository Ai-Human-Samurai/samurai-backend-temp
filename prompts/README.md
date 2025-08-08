# 🧠 prompts/

This directory defines **how Samurai thinks, speaks, and reacts**  
— across languages, styles, and emotional contexts.

Samurai is not just a chatbot.  
It has a **code**, a **voice**, and a **presence**.

---

## 📂 Structure

Each file represents a **behavioral category**, split by language:

prompts/
├── styles/ # Speech tone presets
├── sos/ # Support in emotional crisis
├── intents/ # Key intent mappings for interpretation
├── generation/ # GPT prompt templates for dynamic phrase creation
├── reminders/ # Interaction logic for reminder flow
├── flood/ # Anti-flood logic and calm downs
├── system/ # Core behavioral definition (identity prompt)
├── semantic_filter/ # Ethical boundaries and phrase screening



Each subfolder contains:

- `ru.py` — Russian behavior profile  
- `en.py` — English behavior profile  
- (Optional) `fr.py`, `es.py`, etc. — any future languages

---

## 🧬 File Descriptions

### `system.py`
Defines Samurai's **core philosophy**.  
Used as the **system prompt** for GPT-based responses.  
Minimalist, focused, disciplined.

> "You are not a bot. You reflect. You protect. You speak with restraint."

---

### `styles.py`
Speech tone presets based on emotional framing.

- `friendly`: warm, human, supportive  
- `formal`: neutral, reserved, polite  
- `dry`: short, tactical, emotionless

Each includes:

- `wake_up`  
- `reminder`  
- `encouragement`  
- `snooze`

---

### `sos.py`
Short, humane phrases used in critical moments.  
No advice. No pity. Just presence.

Includes:

- `SOS_PHRASES`: ready-to-use lines  
- `SYSTEM_SOS_PROMPT`: GPT fallback generator  
- `SOS_INTENTS`: emotional context tags

---

### `intents.py`
Maps **user intention** to internal behavior categories.  
Used to drive logic and choose phrase style.

Examples:

- `wake_up_silent_1`  
- `encouragement_direct`  
- `reminder_done`

---

### `generation.py`
Contains **system prompts for GPT** to dynamically generate content, e.g.:

- Motivational lines  
- Wake-up calls  
- Reminder parsing instructions (`REMINDER_PARSE_SYSTEM`)  
- Examples (`REMINDER_PARSE_EXAMPLE`)

---

### `reminders.py`
Defines key stages of interaction with reminders:

- `reminder_confirm`  
- `reminder_done`  
- `reminder_repeat`  
- `reminder_expired`

All mapped as intent tags.

---

### `flood.py`
Handles **anti-flood responses** for repeated meaningless input.  
Used to gently push the user back to purpose.

Includes:

- `FLOOD_WARNINGS`: responses by stage  
- `FLOOD_WARNING_TITLES`: UI/meta tags

---

### `semantic_filter.py`
Ensures ethical communication.

Includes:

- `BAD_WORDS`: static word-level filter
- `SEMANTIC_FILTER_PROMPT`: GPT-based ethical judgment (TRUE/FALSE)

---

## 🌍 Multilingual Support

Adding a new language is seamless:

1. Create files like `en.py`, `fr.py`, `jp.py` in each subfolder  
2. Match the keys and structure of existing `ru.py` or `en.py`  
3. `load_prompts(lang)` will handle the rest

No backend rewrite required.

---

## 📡 Philosophy

This folder is not just config.  
It defines how Samurai **responds to intention** — not keywords.  
How it **behaves under stress**, how it **remains silent** when needed, and how it **adapts without losing integrity**.

> This is where the **soul of Samurai** lives.