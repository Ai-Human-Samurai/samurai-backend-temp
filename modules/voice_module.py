import openai
from core.logger import logger
from core.credentials import OPENAI_API_KEY
from modules.voice_cache import save_mp3_file
from modules.behavior_engine import get_phrase
from modules.emotion_detector import should_block_emotion, log_emotional_appeal
from modules.flood_guard import guard, check_meaning
from modules.behavior.style_map import resolve_style
from prompts import load_prompts

openai.api_key = OPENAI_API_KEY


def is_toxic(text: str, lang: str = "ru") -> bool:
    prompts = load_prompts(lang)
    bad_words = prompts["semantic_filter"]["BAD_WORDS"]
    return any(word in text.lower() for word in bad_words)


def check_semantic_toxicity(text: str, lang: str = "ru") -> bool:
    try:
        prompts = load_prompts(lang)
        system_prompt = prompts["semantic_filter"]["SEMANTIC_FILTER_PROMPT"]

        completion = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            temperature=0,
            max_tokens=5
        )
        result = completion.choices[0].message.content.strip().upper()
        return result == "TRUE"
    except Exception as e:
        logger.error(f"[GPT-Filter] Semantic check failed: {e}")
        return False


def is_text_blocked(text: str, lang: str = "ru") -> bool:
    return is_toxic(text, lang=lang) or check_semantic_toxicity(text, lang=lang)


def style_to_voice(normalized_style: str) -> str:
    mapping = {
        "friendly": "onyx",
        "formal": "onyx",
        "dry": "onyx",
    }
    return mapping.get(normalized_style.lower().strip(), "nova")


def synthesize_voice(text: str, voice: str = "nova") -> bytes | None:
    try:
        logger.info(f"[TTS] Synthesizing voice={voice}, text={text[:30]}...")
        response = openai.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text
        )
        return response.read()
    except Exception as e:
        logger.error(f"[TTS] synthesis failed (voice={voice}, text={text[:30]}): {e}")
        return None


def save_blocked_voice(lang: str = "ru") -> str | None:
    prompts = load_prompts(lang)
    text = prompts["system"]["BLOCKED_MESSAGE"]
    voice = style_to_voice("dry")

    audio_bytes = synthesize_voice(text=text, voice=voice)
    if not audio_bytes:
        return None

    return save_mp3_file(audio_bytes, text=text, lang=lang)


def save_custom_response(text: str, lang: str = "ru") -> str | None:
    voice = style_to_voice("dry")
    audio_bytes = synthesize_voice(text=text, voice=voice)
    if not audio_bytes:
        return None

    return save_mp3_file(audio_bytes, text=text, lang=lang)


def generate_and_save_voice(user_id: int, style: str, intent: str, db, lang: str = "ru") -> str | None:
    logger.info(f"[VoiceGen] Intent start: user_id={user_id}, intent={intent}, style={style}, lang={lang}")
    style = resolve_style(style, lang)
    phrase_data = get_phrase(style=style, intent=intent, lang=lang, user_id=user_id)
    text = phrase_data["text"]

    if is_text_blocked(text, lang=lang):
        logger.warning(f"[BlockedIntentText] {text}")
        return save_blocked_voice(lang)



    log_emotional_appeal(db, user_id, detail=f"intent={intent}")

    flood_reply = guard.update(user_id, is_meaningful=check_meaning(text), lang=lang)
    if flood_reply:
        return save_custom_response(flood_reply, lang)

    voice_name = "onyx"
    audio_bytes = synthesize_voice(text=text, voice=voice_name)
    if not audio_bytes:
        return None

    return save_mp3_file(audio_bytes, text=text, lang=lang)


def generate_custom_voice(user_id: int, text: str, style: str = "friendly", db=None, lang: str = "ru") -> str | None:
    logger.info(f"[VoiceGen] Custom start: user_id={user_id}, style={style}, lang=lang, text={text}")
    style = resolve_style(style, lang)

    if is_text_blocked(text, lang=lang):
        logger.warning(f"[BlockedCustomText] {text}")
        return save_blocked_voice(lang)


    log_emotional_appeal(db, user_id, detail="custom")

    flood_reply = guard.update(user_id, is_meaningful=check_meaning(text), lang=lang)
    if flood_reply:
        return save_custom_response(flood_reply, lang)

    voice_name = style_to_voice(style)
    audio_bytes = synthesize_voice(text=text, voice=voice_name)
    if not audio_bytes:
        return None

    return save_mp3_file(audio_bytes, text=text, lang=lang)