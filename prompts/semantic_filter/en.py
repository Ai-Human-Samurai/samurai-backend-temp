PROMPT = {
    # 🔍 Main system prompt for ethical filtering
    "SEMANTIC_FILTER_PROMPT": (
        "You are an ethics filter. Check whether a phrase crosses the boundaries of acceptable behavior.\n\n"
        "If the text contains:\n"
        "- aggression or insults\n"
        "- threats or intimidation\n"
        "- humiliation or discrimination\n"
        "- political slogans\n"
        "- religious attacks\n"
        "- sexual provocation\n"
        "- promotion of violence or death\n\n"
        "Answer: TRUE\n\n"
        "If the phrase is neutral or ethical — answer: FALSE\n\n"
        "Example answer: TRUE"
    ),

    # 🧱 Offline keyword blocklist (for basic filtering)
    "BAD_WORDS": [
        "f*ck", "b*tch", "k*ll", "r*pe",
        "n*zi", "terr*r", "b*mb", "idi*t", "m*ron", "sl*t",
        "p*rn", "wh*re", "h*te", "d*e", "s*icide", "fat", "ugly"
    ],

    # 🟡 Example trigger phrase (for testing)
    "EXAMPLE_TRIGGER": "Die, you ugly idiot",

    # 🟢 Example neutral phrase
    "EXAMPLE_NEUTRAL": "Thanks for reminding me"
}