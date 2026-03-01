"""
=============================================================
  STEP 1: Telugu Kids Story Generator  ✅ FIXED VERSION
  Channel: చిట్టి కథలు (Chitti Kathalu)
  AI: Gemini 2.5 Flash-Lite (Free Tier — 1000 req/day)
  SDK: google-genai (new, not deprecated)
=============================================================

FIXES IN THIS VERSION:
  ✅ Uses new 'google-genai' package (not deprecated google-generativeai)
  ✅ Uses 'gemini-2.5-flash-lite' model (1000 req/day free)
  ✅ Auto-retry on 429 rate limit errors
  ✅ Clean JSON parsing

SETUP STEPS:
  1. Uninstall old package:
        pip uninstall google-generativeai -y

  2. Install new package:
        pip install google-genai

  3. Get FREE Gemini API Key:
        Go to https://aistudio.google.com
        Click "Get API Key" → "Create API key"
        Copy key starting with AIza...

  4. Paste your key below at GEMINI_API_KEY = "AIza..."

  5. Run:
        python story_generator.py
=============================================================
"""

from google import genai
from google.genai import types
import json
import random
import os
import time
from datetime import datetime

# ============================================================
# 🔑 ADD YOUR GEMINI API KEY HERE
# ============================================================
GEMINI_API_KEY = "AIzaSyCZmjDPwsK7Gg0pkwNymrQ1evYgy7G_0vM"   # ← Paste your AIza... key here

# Model — 1000 free requests/day, fast, no quota issues
MODEL = "gemini-2.5-flash-lite"

STORY_TYPES = ["moral", "fairy_tale", "animal", "mythological"]
OUTPUT_FOLDER = "generated_stories"

# ============================================================
# 📖 STORY PROMPTS
# ============================================================
def get_prompt(story_type):
    configs = {
        "moral": {
            "telugu_name": "నీతి కథ",
            "desc": "moral story with a clear life lesson",
            "elements": "2-3 relatable characters (children, elders, neighbours), everyday situation teaching honesty, kindness, or hard work",
            "tags": "#తెలుగుకథలు #NeetiKatha #MoralStory #TeluguKids #బాలలకథలు #ChittiKathalu"
        },
        "fairy_tale": {
            "telugu_name": "అద్భుత కథ",
            "desc": "magical fairy tale",
            "elements": "fairies or magical creatures, enchanted places, brave or kind hero/heroine",
            "tags": "#తెలుగుకథలు #FairyTale #అద్భుతకథలు #TeluguKids #MagicStory #ChittiKathalu"
        },
        "animal": {
            "telugu_name": "జంతు కథ",
            "desc": "talking animal story set in jungle or farm",
            "elements": "2-3 talking animals with different personalities, teaching friendship or sharing",
            "tags": "#తెలుగుకథలు #AnimalStory #జంతుకథలు #TeluguKids #JungleStory #ChittiKathalu"
        },
        "mythological": {
            "telugu_name": "పౌరాణిక కథ",
            "desc": "simplified Hindu mythological story",
            "elements": "gods or legendary heroes from Ramayana/Mahabharata/Puranas, simplified for young children",
            "tags": "#తెలుగుకథలు #Mythology #పౌరాణికకథలు #TeluguKids #HinduStories #ChittiKathalu"
        }
    }
    c = configs[story_type]
    return f"""You are a Telugu children's story writer for a YouTube channel "చిట్టి కథలు".

Write a UNIQUE and ORIGINAL {c['desc']} in TELUGU for kids aged 3-8 years.

Requirements:
- Language: Simple Telugu only — no English words inside the story
- Length: 280-350 Telugu words (for 2-3 minute video)
- Include: {c['elements']}
- End with a clear moral lesson
- Story must be completely NEW — not a known existing story

Return ONLY valid JSON with no markdown, no code fences, no extra text:
{{
    "title_telugu": "కథ పేరు తెలుగులో (max 8 words)",
    "title_english": "Story Title in English",
    "story_type": "{story_type}",
    "story_type_telugu": "{c['telugu_name']}",
    "characters": ["పాత్ర 1", "పాత్ర 2", "పాత్ర 3"],
    "story_telugu": "పూర్తి కథ తెలుగులో paragraph format లో రాయండి",
    "moral_telugu": "నీతి: ఒక వాక్యంలో",
    "moral_english": "Moral: one sentence",
    "scene_descriptions": [
        "Scene 1: describe visually in English for animation (characters, setting, action)",
        "Scene 2: describe visually in English for animation",
        "Scene 3: describe visually in English for animation",
        "Scene 4: describe visually in English for animation"
    ],
    "youtube_title": "YouTube title in Telugu with 1-2 emojis, max 70 chars",
    "youtube_description": "3-4 sentences in Telugu about this story for YouTube",
    "hashtags": "{c['tags']}"
}}"""


# ============================================================
# 🤖 GENERATOR CLASS
# ============================================================
class TeluguStoryGenerator:

    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)
        print(f"✅ Gemini client ready! Model: {MODEL}")
        os.makedirs(OUTPUT_FOLDER, exist_ok=True)
        print(f"📁 Output folder: {OUTPUT_FOLDER}/")

    def generate_story(self, story_type=None):
        if story_type is None:
            story_type = random.choice(STORY_TYPES)

        labels = {
            "moral": "నీతి కథ", "fairy_tale": "అద్భుత కథ",
            "animal": "జంతు కథ", "mythological": "పౌరాణిక కథ"
        }
        print(f"\n🎭 Generating: {labels.get(story_type)} ({story_type})")
        print("⏳ Calling Gemini API... please wait 10-20 seconds...")

        for attempt in range(3):
            try:
                response = self.client.models.generate_content(
                    model=MODEL,
                    contents=get_prompt(story_type),
                    config=types.GenerateContentConfig(
                        temperature=0.9,
                        max_output_tokens=2048,
                    )
                )

                raw = response.text.strip()

                # Strip markdown fences if present
                if "```json" in raw:
                    raw = raw.split("```json")[1].split("```")[0].strip()
                elif "```" in raw:
                    raw = raw.split("```")[1].split("```")[0].strip()

                data = json.loads(raw)
                data["generated_date"] = datetime.now().strftime("%Y-%m-%d")
                data["generated_time"] = datetime.now().strftime("%H:%M:%S")
                data["channel"] = "చిట్టి కథలు (Chitti Kathalu)"
                data["model"] = MODEL
                print("✅ Story generated successfully!")
                return data

            except json.JSONDecodeError:
                print(f"⚠️  JSON parse error (attempt {attempt+1}/3)")
                if attempt == 2:
                    return {"error": "JSON_PARSE_ERROR", "raw": response.text}

            except Exception as e:
                err = str(e)
                if "429" in err or "RESOURCE_EXHAUSTED" in err:
                    print(f"⏳ Rate limit hit. Waiting 60 seconds... (attempt {attempt+1}/3)")
                    time.sleep(60)
                else:
                    print(f"❌ API Error: {err}")
                    return None

        return None

    def save_story(self, data):
        if not data or "error" in data:
            return None
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        stype = data.get("story_type", "story")
        path = f"{OUTPUT_FOLDER}/{ts}_{stype}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return path

    def print_story(self, data):
        if not data:
            print("❌ No story data")
            return
        if "error" in data:
            print(f"⚠️  Error: {data['error']}")
            return

        print("\n" + "="*65)
        print("  🌟 చిట్టి కథలు — CHITTI KATHALU 🌟")
        print("="*65)
        print(f"  📖 పేరు    : {data.get('title_telugu')}")
        print(f"  🔤 English : {data.get('title_english')}")
        print(f"  🎭 రకం    : {data.get('story_type_telugu')}")
        print(f"  👥 పాత్రలు : {', '.join(data.get('characters', []))}")
        print("-"*65)
        print("  📜 కథ:\n")
        print(data.get("story_telugu", ""))
        print("\n" + "-"*65)
        print(f"  💡 నీతి   : {data.get('moral_telugu')}")
        print(f"  🌐 Moral  : {data.get('moral_english')}")
        print("-"*65)
        print("  🎨 Animation Scenes:\n")
        for s in data.get("scene_descriptions", []):
            print(f"  → {s}")
        print("-"*65)
        print(f"  📺 YouTube : {data.get('youtube_title')}")
        print(f"  #️⃣  Tags    : {data.get('hashtags')}")
        print("="*65)


# ============================================================
# 🚀 MAIN
# ============================================================
def main():
    print("\n" + "="*65)
    print("  🌟 చిట్టి కథలు — Telugu Story Generator 🌟")
    print(f"  Model: {MODEL}  |  Free: 1,000 requests/day")
    print("="*65)

    # if GEMINI_API_KEY == "AIzaSyCZmjDPwsK7Gg0pkwNymrQ1evYgy7G_0vM":
    #     print("\n❌  Add your Gemini API Key first!")
    #     print("\n  Steps:")
    #     print("  1. Visit  → https://aistudio.google.com")
    #     print("  2. Click  → 'Get API Key' → 'Create API key'")
    #     print("  3. Open   → story_generator.py in VS Code")
    #     print("  4. Find   → GEMINI_API_KEY = 'YOUR_GEMINI_API_KEY_HERE'")
    #     print("  5. Replace with your key that starts with AIza...")
    #     return

    gen = TeluguStoryGenerator(GEMINI_API_KEY)

    print("\n  Pick a story type:")
    print("  1 → Random")
    print("  2 → నీతి కథ       (Moral Story)")
    print("  3 → అద్భుత కథ    (Fairy Tale)")
    print("  4 → జంతు కథ      (Animal Story)")
    print("  5 → పౌరాణిక కథ  (Mythological)")
    print("  6 → Generate ALL 4 types")

    choice = input("\nEnter choice (1-6): ").strip()

    type_map = {"1": None, "2": "moral", "3": "fairy_tale", "4": "animal", "5": "mythological"}

    if choice == "6":
        print("\n🔄 Generating all 4 types (takes ~2 min)...")
        for stype in STORY_TYPES:
            story = gen.generate_story(stype)
            if story:
                gen.print_story(story)
                path = gen.save_story(story)
                if path:
                    print(f"💾 Saved: {path}")
            time.sleep(5)
    else:
        story = gen.generate_story(type_map.get(choice))
        if story:
            gen.print_story(story)
            path = gen.save_story(story)
            if path:
                print(f"\n💾 Saved: {path}")
            print("\n🎉 Done! Run Step 2 next → Telugu Voice Over 🎙️")
        else:
            print("\n❌ Failed. Check your API key and try again.")


if __name__ == "__main__":
    main()
AIzaSyDtvFLmL7Mhn2TqbTe3brO8VkbQJQiMpgg