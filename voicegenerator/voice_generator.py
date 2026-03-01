"""
=============================================================
  STEP 2: Telugu Voice Over Generator  ✅ AUTO-DISCOVER VERSION
  Channel: చిట్టి కథలు (Chitti Kathalu)
  Tool: Google Cloud TTS
=============================================================

THIS VERSION:
  ✅ First AUTO-DISCOVERS all Telugu voices available in your
     Google Cloud account — no more "voice not found" errors!
  ✅ Lists them all so you can pick the best
  ✅ Generates MP3 for any voice you choose

SAME API KEY — no new setup needed!

RUN:
  python voice_generator.py

MENU:
  D → Discover all available Telugu voices (run this first!)
  G → Generate voice MP3 for a story
=============================================================
"""

import os
import json
import glob
from datetime import datetime
from google.cloud import texttospeech

# ============================================================
# 🔑 YOUR GOOGLE CLOUD API KEY (same as before)
# ============================================================
GOOGLE_TTS_API_KEY = "AIzaSyDtvFLmL7Mhn2TqbTe3brO8VkbQJQiMpgg"   # ← Paste here

# Folders
# derive absolute paths so script works no matter where it's invoked from
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# original story generator outputs into ../story/generated_stories
STORIES_FOLDER  = os.path.join(SCRIPT_DIR, "..", "story", "generated_stories")   # Input  — from Step 1
VOICES_FOLDER   = os.path.join(SCRIPT_DIR, "generated_voices")    # Output — MP3 files

# ============================================================
# 🎙️ VOICE AUDIO SETTINGS
# ============================================================
# Note: Chirp3-HD does NOT support speaking_rate or pitch
# WaveNet/Standard DO support these controls

KIDS_WAVENET_SETTINGS = {
    "speaking_rate": 0.82,   # Slightly slower — easy for kids
    "pitch": 3.5,            # Higher pitch = warmer/younger feel
    "volume_gain_db": 1.5
}

NORMAL_WAVENET_SETTINGS = {
    "speaking_rate": 0.85,
    "pitch": 1.0,
    "volume_gain_db": 1.0
}


# ============================================================
# 🔍 AUTO-DISCOVER AVAILABLE VOICES
# ============================================================
def discover_telugu_voices(api_key):
    """Fetch all available te-IN voices from Google Cloud"""
    client = texttospeech.TextToSpeechClient(
        client_options={"api_key": api_key}
    )

    print("\n🔍 Fetching all available Telugu (te-IN) voices from Google Cloud...")

    try:
        response = client.list_voices(language_code="te-IN")
        voices = sorted(response.voices, key=lambda v: v.name)

        if not voices:
            print("❌ No Telugu voices found! Check if TTS API is enabled.")
            return []

        print(f"\n✅ Found {len(voices)} Telugu voices:\n")
        print(f"  {'#':<4} {'Voice Name':<35} {'Gender':<10} {'Type':<12}")
        print("  " + "-"*65)

        voice_list = []
        for i, voice in enumerate(voices, 1):
            name   = voice.name
            gender = texttospeech.SsmlVoiceGender(voice.ssml_gender).name
            # Detect voice type from name
            if "Chirp3-HD" in name or "Chirp-HD" in name:
                vtype = "Chirp3-HD ⭐"
            elif "Wavenet" in name or "WaveNet" in name:
                vtype = "WaveNet 👍"
            elif "Neural2" in name:
                vtype = "Neural2 ✅"
            elif "Standard" in name:
                vtype = "Standard"
            else:
                vtype = "Other"

            print(f"  {i:<4} {name:<35} {gender:<10} {vtype}")
            voice_list.append({
                "index": i,
                "name": name,
                "gender": gender,
                "type": vtype,
                "language_code": "te-IN"
            })

        print("\n  💡 TIP: Chirp3-HD ⭐ = most natural, WaveNet 👍 = good quality")
        return voice_list

    except Exception as e:
        print(f"❌ Error fetching voices: {str(e)}")
        if "403" in str(e) or "permission" in str(e).lower():
            print("   Make sure Text-to-Speech API is enabled:")
            print("   → https://console.cloud.google.com → APIs → Text-to-Speech → Enable")
        return []


# ============================================================
# 🎙️ VOICE GENERATOR
# ============================================================
class TeluguVoiceGenerator:

    def __init__(self, api_key):
        self.client = texttospeech.TextToSpeechClient(
            client_options={"api_key": api_key}
        )
        os.makedirs(VOICES_FOLDER, exist_ok=True)
        print("✅ Google Cloud TTS client ready!")

    def build_narration(self, story_data):
        title = story_data.get("title_telugu", "")
        story = story_data.get("story_telugu", "")
        moral = story_data.get("moral_telugu", "")
        return f"""చిట్టి కథలు కి స్వాగతం.

నేటి కథ పేరు... {title}.

{story}

{moral}

ఈ కథ మీకు నచ్చిందా? లైక్ చేయండి, చానెల్ సబ్స్క్రైబ్ చేయండి. మళ్ళీ మంచి కథతో కలుద్దాం!""".strip()

    def generate_voice(self, text, voice_info, kids_tuned=False):
        """Generate MP3 for a specific voice"""
        name   = voice_info["name"]
        gender = voice_info["gender"]
        vtype  = voice_info["type"]

        print(f"\n  🎙️  Generating: {name}  [{vtype}]")
        print(f"  📝 Characters : {len(text)}")

        try:
            synthesis_input = texttospeech.SynthesisInput(text=text)

            # Map gender string back to enum
            gender_enum = (
                texttospeech.SsmlVoiceGender.FEMALE
                if gender == "FEMALE"
                else texttospeech.SsmlVoiceGender.MALE
            )

            voice_params = texttospeech.VoiceSelectionParams(
                language_code="te-IN",
                name=name,
                ssml_gender=gender_enum
            )

            # Chirp3-HD does NOT support speaking_rate/pitch
            is_chirp = "Chirp" in name
            if is_chirp:
                audio_config = texttospeech.AudioConfig(
                    audio_encoding=texttospeech.AudioEncoding.MP3,
                    sample_rate_hertz=24000
                )
            else:
                # WaveNet/Standard support full audio controls
                settings = KIDS_WAVENET_SETTINGS if kids_tuned else NORMAL_WAVENET_SETTINGS
                audio_config = texttospeech.AudioConfig(
                    audio_encoding=texttospeech.AudioEncoding.MP3,
                    speaking_rate=settings["speaking_rate"],
                    pitch=settings["pitch"],
                    volume_gain_db=settings["volume_gain_db"],
                    sample_rate_hertz=24000
                )

            response = self.client.synthesize_speech(
                input=synthesis_input,
                voice=voice_params,
                audio_config=audio_config
            )

            # Save file
            safe_name = name.replace("/", "_").replace(" ", "_")
            kids_tag  = "_kids" if kids_tuned else ""
            filename  = f"{VOICES_FOLDER}/{safe_name}{kids_tag}.mp3"

            with open(filename, "wb") as f:
                f.write(response.audio_content)

            size_kb = len(response.audio_content) / 1024
            print(f"  ✅ Saved: {filename}  ({size_kb:.1f} KB)")
            return filename

        except Exception as e:
            err = str(e)
            if "not found" in err.lower() or "400" in err:
                print(f"  ⚠️  Voice '{name}' not available — skipping")
            else:
                print(f"  ❌ Error: {err}")
            return None


# ============================================================
# 📂 HELPERS
# ============================================================
def get_story_files():
    files = glob.glob(f"{STORIES_FOLDER}/*.json")
    files.sort(reverse=True)
    return files

def load_story(fp):
    with open(fp, "r", encoding="utf-8") as f:
        return json.load(f)


# ============================================================
# 🚀 MAIN
# ============================================================
def main():
    print("\n" + "="*65)
    print("  🎙️  చిట్టి కథలు — Telugu Voice Generator")
    print("  Auto-Discover + Generate Natural Telugu Voices")
    print("="*65)

    if GOOGLE_TTS_API_KEY == "YOUR_GOOGLE_CLOUD_API_KEY_HERE":
        print("\n❌  Paste your Google Cloud API key first!")
        return

    print("\n  What do you want to do?")
    print("  D → Discover all available Telugu voices (run this first!)")
    print("  G → Generate voice MP3 for a story")
    print("  B → Both — discover voices then generate")

    action = input("\nEnter choice (D/G/B): ").strip().upper()

    # ── DISCOVER VOICES ───────────────────────────────────────
    voice_list = []
    if action in ["D", "B"]:
        voice_list = discover_telugu_voices(GOOGLE_TTS_API_KEY)
        if not voice_list:
            return
        if action == "D":
            print("\n  ✅ Voice discovery complete!")
            print("  Run again and choose G to generate MP3s.")
            return

    # ── GENERATE MP3 ──────────────────────────────────────────
    if action in ["G", "B"]:

        # If we didn't discover yet, do it now silently
        if not voice_list:
            voice_list = discover_telugu_voices(GOOGLE_TTS_API_KEY)
            if not voice_list:
                return

        # Pick story
        story_files = get_story_files()
        if not story_files:
            print(f"\n❌  No stories in '{STORIES_FOLDER}/' — run story_generator.py first!")
            return

        print(f"\n\n📚 Stories available:\n")
        for i, f in enumerate(story_files[:5], 1):
            s = load_story(f)
            print(f"  {i}. {s.get('title_telugu')}  [{s.get('story_type')}]")
        print("  L → Latest story")

        sc = input("\nPick story (1-5 or L): ").strip().upper()
        idx = 0 if sc == "L" else max(0, int(sc)-1) if sc.isdigit() else 0
        idx = min(idx, len(story_files)-1)
        story = load_story(story_files[idx])
        print(f"\n✅ Story: {story.get('title_telugu')}")

        # Pick voices to generate
        print(f"\n  Which voices to generate?")
        print(f"  A   → ALL {len(voice_list)} voices (best for comparing)")
        print(f"  C   → Chirp3-HD voices only (most natural)")
        print(f"  W   → WaveNet voices only")
        print(f"  Or enter numbers separated by comma  e.g: 1,3,5")

        vc = input("\nEnter choice: ").strip().upper()

        if vc == "A":
            selected = voice_list
        elif vc == "C":
            selected = [v for v in voice_list if "Chirp" in v["type"]]
        elif vc == "W":
            selected = [v for v in voice_list if "WaveNet" in v["type"]]
        else:
            # Specific numbers
            try:
                indices = [int(x.strip())-1 for x in vc.split(",")]
                selected = [voice_list[i] for i in indices if 0 <= i < len(voice_list)]
            except Exception:
                selected = [voice_list[0]]  # Default to first voice

        gen = TeluguVoiceGenerator(GOOGLE_TTS_API_KEY)
        narration = gen.build_narration(story)
        print(f"\n📝 Narration: {len(narration)} characters")

        # Ask kids-tune for WaveNet voices
        has_wavenet = any("WaveNet" in v["type"] for v in selected)
        kids_tune = False
        if has_wavenet:
            kt = input("\n  Apply kids-tuning to WaveNet voices? (higher pitch + slower) Y/N: ").strip().upper()
            kids_tune = kt == "Y"

        print(f"\n🎙️  Generating {len(selected)} voice(s)...\n")
        print("-"*65)

        results = {}
        for v in selected:
            is_kids = kids_tune and "WaveNet" in v["type"]
            path = gen.generate_voice(narration, v, kids_tuned=is_kids)
            if path:
                results[v["name"]] = path

        # Summary
        print("\n" + "="*65)
        print(f"  ✅ {len(results)} MP3 file(s) generated!")
        print("="*65)
        print(f"\n  📁 Location: {VOICES_FOLDER}/")
        print(f"\n  💡 Next steps:")
        print(f"     1. Open File Explorer → {VOICES_FOLDER}/")
        print(f"     2. Play each MP3 and pick your favorite")
        print(f"     3. Tell me which voice name you like best!")
        print(f"     4. That voice will be locked in for all future videos")
        print(f"\n  🎬 Once decided → Step 3: AI Video Generation!")


if __name__ == "__main__":
    main()
