import random
from openai import OpenAIError
from core.credentials import openai_client
from prompts import load_prompts
from modules.behavior.known_phrases import ALL_KNOWN_PHRASES


def generate_dynamic_phrase(category: str, lang: str = "ru") -> str:
    """
    Generates a fresh Samurai-style phrase for a given category and language.
    """
    prompts = load_prompts(lang)
    examples = ALL_KNOWN_PHRASES.get(category, [])
    system_prompt = prompts["generation"].get("GENERATOR_SYSTEM", "")
    fallback_phrase = prompts["generation"].get("GENERATOR_FALLBACK", "...")

    if not examples:
        return fallback_phrase

    examples_text = "\n".join(f"- {item['text']}" for item in examples)
    prefix = prompts["generation"].get("GENERATOR_EXAMPLES_PREFIX", "")
    user_req = prompts["generation"].get("GENERATOR_USER_REQUEST", "")

    user_prompt = f"{prefix}\n{examples_text}\n\n{user_req}".strip()

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            temperature=0.7,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]
        )
        return response.choices[0].message.content.strip() if response.choices else fallback_phrase
    except OpenAIError:
        return random.choice(examples)["text"]