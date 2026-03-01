"""
=============================================================
  STEP 3: AI Video Creator
  Channel: చిట్టి కథలు (Chitti Kathalu)
  Images : Pollinations AI (FREE — no API key, no limits!)
  Video  : FFmpeg (merge images + voice → MP4)
  Style  : 2D Cartoon — colorful kids animation style
=============================================================

WHAT THIS SCRIPT DOES:
  1. Reads story JSON from generated_stories/
  2. Reads voice MP3 from generated_voices/
  3. Generates 4 cartoon scene images using Pollinations AI
  4. Adds Telugu title text overlay on each scene
  5. Applies Ken Burns zoom effect for animation feel
  6. Merges all scenes + voice → final MP4 video
  7. Adds intro title card + outro subscribe card

SETUP:
  1. Install packages:
        pip install pollinations requests pillow

  2. Install FFmpeg:
        Windows → https://ffmpeg.org/download.html
                → Download, extract, add to PATH
        OR run:  winget install ffmpeg

  3. Run:
        python video_creator.py

OUTPUT:
  generated_videos/
    └── 20260228_143805_moral_final.mp4  ← Upload to YouTube!
=============================================================
"""

import os
import json
import glob
import time
import subprocess
import textwrap
import requests
from pathlib import Path
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import urllib.parse

# ============================================================
# ⚙️ CONFIGURATION
# ============================================================
# derive absolute folders so script works regardless of cwd
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR   = os.path.normpath(os.path.join(SCRIPT_DIR, ".."))

# Input story JSONs are produced by story_generator in sibling 'story' folder
STORIES_FOLDER = os.path.join(BASE_DIR, "story", "generated_stories")
# Voice MP3s are created by voice_generator in sibling 'voicegenerator' folder
VOICES_FOLDER  = os.path.join(BASE_DIR, "voicegenerator", "generated_voices")
# Images & videos are local to this script
IMAGES_FOLDER  = os.path.join(SCRIPT_DIR, "generated_images")
VIDEOS_FOLDER  = os.path.join(SCRIPT_DIR, "generated_videos")

# Video settings — YouTube standard
VIDEO_WIDTH    = 1920
VIDEO_HEIGHT   = 1080
FPS            = 24

# How long each scene shows (seconds)
# Voice duration is auto-detected; scenes are evenly split
INTRO_DURATION   = 3    # Title card at start
OUTRO_DURATION   = 5    # Subscribe card at end
MIN_SCENE_SECS   = 5    # Minimum seconds per scene

# Pollinations AI image settings
IMAGE_WIDTH    = 1920
IMAGE_HEIGHT   = 1080
IMAGE_MODEL    = "flux"   # Best quality free model

# Colors for text overlays
COLOR_TITLE_BG   = (0, 0, 0, 160)       # Semi-transparent black
COLOR_TITLE_TEXT = (255, 255, 80)        # Bright yellow
COLOR_MORAL_BG   = (20, 80, 20, 200)    # Dark green
COLOR_MORAL_TEXT = (255, 255, 255)       # White
COLOR_INTRO_BG   = (15, 15, 60)         # Deep blue
COLOR_OUTRO_BG   = (20, 60, 20)         # Deep green


# ============================================================
# 🎨 CARTOON PROMPT BUILDER
# ============================================================
def build_cartoon_prompt(scene_description, story_type):
    """Build a kid-friendly cartoon image prompt from scene description"""

    style = (
        "2D cartoon animation style, colorful and vibrant, "
        "Indian children's storybook illustration, "
        "cute characters, soft pastel colors mixed with bright colors, "
        "warm lighting, friendly and cheerful atmosphere, "
        "suitable for kids aged 3-8, "
        "high quality digital art, "
        "no text, no watermarks, no logos"
    )

    type_context = {
        "moral":        "Indian village setting, traditional Indian clothing, warm earthy tones",
        "fairy_tale":   "magical fantasy setting, sparkles, glowing lights, enchanted forest",
        "animal":       "colorful jungle or farm, cute cartoon animals, bright green trees",
        "mythological": "ancient Indian temple setting, divine glow, traditional Indian art style"
    }

    context = type_context.get(story_type, "Indian setting, colorful background")

    return f"{scene_description}, {context}, {style}"


# ============================================================
# 🖼️ POLLINATIONS IMAGE GENERATOR
# ============================================================
class PollinationsImageGenerator:

    def __init__(self):
        self.base_url = "https://image.pollinations.ai/prompt"
        os.makedirs(IMAGES_FOLDER, exist_ok=True)
        print("✅ Pollinations AI ready! (Free — no API key needed)")

    def generate_image(self, prompt, filename, scene_num):
        """Generate a cartoon image using Pollinations AI"""
        print(f"\n  🎨 Scene {scene_num}: Generating cartoon image...")
        print(f"  📝 Prompt: {prompt[:80]}...")

        # Encode prompt for URL
        encoded = urllib.parse.quote(prompt)
        url = (
            f"{self.base_url}/{encoded}"
            f"?width={IMAGE_WIDTH}"
            f"&height={IMAGE_HEIGHT}"
            f"&model={IMAGE_MODEL}"
            f"&nologo=true"
            f"&safe=true"
            f"&seed={scene_num * 1000}"   # Different seed per scene
        )

        for attempt in range(3):
            try:
                response = requests.get(url, timeout=60)
                if response.status_code == 200:
                    filepath = f"{IMAGES_FOLDER}/{filename}"
                    with open(filepath, "wb") as f:
                        f.write(response.content)
                    size_kb = len(response.content) / 1024
                    print(f"  ✅ Saved: {filepath}  ({size_kb:.1f} KB)")
                    return filepath
                else:
                    print(f"  ⚠️  HTTP {response.status_code} — retrying ({attempt+1}/3)")
                    time.sleep(5)
            except requests.Timeout:
                print(f"  ⚠️  Timeout — retrying ({attempt+1}/3)...")
                time.sleep(10)
            except Exception as e:
                print(f"  ❌ Error: {e}")
                time.sleep(5)

        print(f"  ❌ Failed after 3 attempts — using placeholder")
        return self._create_placeholder(filename, scene_num)

    def _create_placeholder(self, filename, scene_num):
        """Create a colored placeholder if image generation fails"""
        colors = [(255, 200, 100), (100, 200, 255), (200, 255, 100), (255, 100, 200)]
        img = Image.new("RGB", (IMAGE_WIDTH, IMAGE_HEIGHT), colors[scene_num % 4])
        draw = ImageDraw.Draw(img)
        draw.text((IMAGE_WIDTH//2, IMAGE_HEIGHT//2),
                  f"Scene {scene_num}", fill=(0,0,0), anchor="mm")
        filepath = f"{IMAGES_FOLDER}/{filename}"
        img.save(filepath)
        return filepath


# ============================================================
# 🖼️ TEXT OVERLAY HELPER
# ============================================================
class TextOverlay:

    @staticmethod
    def add_story_title(image_path, title_telugu, scene_num, total_scenes):
        """Add Telugu title and scene number overlay to image"""
        img = Image.open(image_path).convert("RGBA")
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        w, h = img.size

        # Bottom bar for title
        bar_h = 100
        draw.rectangle([(0, h - bar_h), (w, h)], fill=COLOR_TITLE_BG)

        # Try to load font — fallback to default if not available
        try:
            font_title = ImageFont.truetype("arial.ttf", 42)
            font_small = ImageFont.truetype("arial.ttf", 28)
        except Exception:
            font_title = ImageFont.load_default()
            font_small = font_title

        # Story title
        draw.text((w // 2, h - 55), title_telugu,
                  font=font_title, fill=COLOR_TITLE_TEXT, anchor="mm")

        # Scene counter
        draw.text((w - 30, h - 80), f"{scene_num}/{total_scenes}",
                  font=font_small, fill=(200, 200, 200), anchor="rm")

        # Merge
        result = Image.alpha_composite(img, overlay).convert("RGB")
        out_path = image_path.replace(".jpg", "_overlay.jpg").replace(".png", "_overlay.png")
        result.save(out_path, quality=95)
        return out_path

    @staticmethod
    def create_intro_card(title_telugu, title_english, story_type_telugu, output_path):
        """Create title intro card"""
        img = Image.new("RGB", (VIDEO_WIDTH, VIDEO_HEIGHT), COLOR_INTRO_BG)
        draw = ImageDraw.Draw(img)

        try:
            font_big    = ImageFont.truetype("arial.ttf", 72)
            font_medium = ImageFont.truetype("arial.ttf", 48)
            font_small  = ImageFont.truetype("arial.ttf", 36)
        except Exception:
            font_big = font_medium = font_small = ImageFont.load_default()

        # Channel name
        draw.text((VIDEO_WIDTH//2, 180), "చిట్టి కథలు 🌟",
                  font=font_big, fill=(255, 220, 50), anchor="mm")

        # Story type
        draw.text((VIDEO_WIDTH//2, 320), story_type_telugu,
                  font=font_medium, fill=(180, 220, 255), anchor="mm")

        # Telugu title
        draw.text((VIDEO_WIDTH//2, 500), title_telugu,
                  font=font_big, fill=(255, 255, 255), anchor="mm")

        # English title
        draw.text((VIDEO_WIDTH//2, 640), title_english,
                  font=font_small, fill=(180, 180, 180), anchor="mm")

        # Decorative line
        draw.line([(300, 420), (VIDEO_WIDTH-300, 420)], fill=(255, 220, 50), width=3)

        img.save(output_path, quality=95)
        return output_path

    @staticmethod
    def create_moral_card(moral_telugu, moral_english, output_path):
        """Create moral/lesson card"""
        img = Image.new("RGB", (VIDEO_WIDTH, VIDEO_HEIGHT), (20, 50, 20))
        draw = ImageDraw.Draw(img)

        try:
            font_big    = ImageFont.truetype("arial.ttf", 60)
            font_medium = ImageFont.truetype("arial.ttf", 44)
            font_small  = ImageFont.truetype("arial.ttf", 32)
        except Exception:
            font_big = font_medium = font_small = ImageFont.load_default()

        draw.text((VIDEO_WIDTH//2, 200), "💡 నేటి నీతి",
                  font=font_big, fill=(255, 220, 50), anchor="mm")
        draw.line([(300, 270), (VIDEO_WIDTH-300, 270)], fill=(255, 220, 50), width=3)
        draw.text((VIDEO_WIDTH//2, 420), moral_telugu,
                  font=font_medium, fill=(255, 255, 255), anchor="mm")
        draw.text((VIDEO_WIDTH//2, 560), moral_english,
                  font=font_small, fill=(180, 220, 180), anchor="mm")

        img.save(output_path, quality=95)
        return output_path

    @staticmethod
    def create_outro_card(output_path):
        """Create subscribe outro card"""
        img = Image.new("RGB", (VIDEO_WIDTH, VIDEO_HEIGHT), (20, 20, 80))
        draw = ImageDraw.Draw(img)

        try:
            font_big    = ImageFont.truetype("arial.ttf", 72)
            font_medium = ImageFont.truetype("arial.ttf", 48)
        except Exception:
            font_big = font_medium = ImageFont.load_default()

        draw.text((VIDEO_WIDTH//2, 300), "చిట్టి కథలు 🌟",
                  font=font_big, fill=(255, 220, 50), anchor="mm")
        draw.text((VIDEO_WIDTH//2, 450), "👍 Like చేయండి",
                  font=font_medium, fill=(255, 255, 255), anchor="mm")
        draw.text((VIDEO_WIDTH//2, 560), "🔔 Subscribe చేయండి",
                  font=font_medium, fill=(100, 255, 100), anchor="mm")
        draw.text((VIDEO_WIDTH//2, 680), "మళ్ళీ మంచి కథతో కలుద్దాం! 🙏",
                  font=font_medium, fill=(255, 200, 100), anchor="mm")

        img.save(output_path, quality=95)
        return output_path


# ============================================================
# 🎬 VIDEO ASSEMBLER (FFmpeg)
# ============================================================
class VideoAssembler:

    def __init__(self):
        self._check_ffmpeg()

    def _find_ffmpeg(self):
        """Auto-discover ffmpeg executable on Windows — handles portable installs"""
        import shutil

        # 1. Already in PATH?
        if shutil.which("ffmpeg"):
            return "ffmpeg", "ffprobe"

        # 2. Common portable install locations on Windows
        search_roots = [
            os.environ.get("USERPROFILE", "C:\\Users"),
            "C:\\Program Files",
            "C:\\Program Files (x86)",
            "C:\\tools",
            "C:\\ffmpeg",
            os.environ.get("LOCALAPPDATA", ""),
            # winget portable default location
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "WinGet", "Packages"),
        ]

        for root in search_roots:
            if not root or not os.path.exists(root):
                continue
            # Walk up to 5 levels deep
            for dirpath, dirnames, filenames in os.walk(root):
                # Limit depth to avoid scanning entire drive
                depth = dirpath.replace(root, "").count(os.sep)
                if depth > 5:
                    dirnames.clear()
                    continue
                if "ffmpeg.exe" in filenames:
                    ffmpeg_path  = os.path.join(dirpath, "ffmpeg.exe")
                    ffprobe_path = os.path.join(dirpath, "ffprobe.exe")
                    if not os.path.exists(ffprobe_path):
                        ffprobe_path = ffmpeg_path.replace("ffmpeg.exe", "ffprobe.exe")
                    return ffmpeg_path, ffprobe_path

        return None, None

    def _check_ffmpeg(self):
        self.ffmpeg_path, self.ffprobe_path = self._find_ffmpeg()

        if self.ffmpeg_path:
            print(f"✅ FFmpeg found: {self.ffmpeg_path}")
            # Add its folder to PATH so subprocess can find it
            ffmpeg_dir = os.path.dirname(self.ffmpeg_path)
            os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ.get("PATH", "")
        else:
            print("❌ FFmpeg not found!")
            print("\n   FFmpeg is installed but we couldn't locate ffmpeg.exe")
            print("   Please find where ffmpeg.exe is on your PC and do ONE of:")
            print("\n   OPTION 1 — Add folder to PATH:")
            print("   1. Search 'Environment Variables' in Windows Start")
            print("   2. Click 'Environment Variables'")
            print("   3. Under 'System variables' → find 'Path' → Edit")
            print("   4. Add the folder containing ffmpeg.exe")
            print("   5. Restart VS Code terminal")
            print("\n   OPTION 2 — Set path directly in this script:")
            print("   Open video_creator.py → find FFMPEG_MANUAL_PATH below")
            print("   Set it to the full path of your ffmpeg.exe")
            raise SystemExit(1)

    def get_audio_duration(self, mp3_path):
        """Get duration of MP3 file in seconds"""
        try:
            result = subprocess.run([
                self.ffprobe_path, "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                mp3_path
            ], capture_output=True, text=True)
            return float(result.stdout.strip())
        except Exception:
            return 60.0   # Default 60 seconds if detection fails

    def create_video_from_images(self, image_paths, durations, audio_path,
                                  output_path):
        """
        Combine images with durations + audio into final MP4 using FFmpeg.
        Each image gets Ken Burns zoom effect for animation feel.
        """
        print(f"\n🎬 Assembling final video...")
        print(f"   Images : {len(image_paths)}")
        print(f"   Audio  : {audio_path}")
        print(f"   Output : {output_path}")

        os.makedirs(VIDEOS_FOLDER, exist_ok=True)

        # Step 1: Create a video clip for each image with zoom effect
        clip_paths = []
        for i, (img_path, duration) in enumerate(zip(image_paths, durations)):
            clip_path = f"{VIDEOS_FOLDER}/clip_{i:02d}.mp4"
            n_frames = int(duration * FPS)

            # Ken Burns zoom-in effect
            zoom_filter = (
                f"zoompan="
                f"z='min(zoom+0.0015,1.3)':"
                f"x='iw/2-(iw/zoom/2)':"
                f"y='ih/2-(ih/zoom/2)':"
                f"d={n_frames}:"
                f"s={VIDEO_WIDTH}x{VIDEO_HEIGHT}:"
                f"fps={FPS}"
            )

            cmd = [
                self.ffmpeg_path, "-y",
                "-loop", "1",
                "-i", img_path,
                "-vf", zoom_filter,
                "-t", str(duration),
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                "-preset", "fast",
                clip_path
            ]
            subprocess.run(cmd, capture_output=True)
            clip_paths.append(clip_path)
            print(f"   ✅ Clip {i+1}/{len(image_paths)} done ({duration:.1f}s)")

        # Step 2: Write concat list file
        concat_file = f"{VIDEOS_FOLDER}/concat_list.txt"
        with open(concat_file, "w") as f:
            for cp in clip_paths:
                f.write(f"file '{os.path.abspath(cp)}'\n")

        # Step 3: Concatenate all clips
        raw_video = f"{VIDEOS_FOLDER}/raw_video.mp4"
        cmd = [
            self.ffmpeg_path, "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", concat_file,
            "-c", "copy",
            raw_video
        ]
        subprocess.run(cmd, capture_output=True)
        print("   ✅ All clips concatenated")

        # Step 4: Add audio + fade in/out
        cmd = [
            self.ffmpeg_path, "-y",
            "-i", raw_video,
            "-i", audio_path,
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            "-af", "afade=t=in:d=1,afade=t=out:st=0:d=2:type=t",
            output_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)

        # Cleanup temp clips
        for cp in clip_paths:
            if os.path.exists(cp):
                os.remove(cp)
        if os.path.exists(raw_video):
            os.remove(raw_video)
        if os.path.exists(concat_file):
            os.remove(concat_file)

        if os.path.exists(output_path):
            size_mb = os.path.getsize(output_path) / (1024 * 1024)
            print(f"\n  ✅ Final video: {output_path}  ({size_mb:.1f} MB)")
            return output_path
        else:
            print(f"  ❌ Video creation failed!")
            print(f"  FFmpeg error: {result.stderr[-500:]}")
            return None


# ============================================================
# 📂 HELPERS
# ============================================================
def get_files(folder, ext):
    files = glob.glob(f"{folder}/*{ext}")
    files.sort(reverse=True)
    return files

def load_json(fp):
    with open(fp, "r", encoding="utf-8") as f:
        return json.load(f)

def find_voice_for_story(story_base, preferred_voice="Aoede"):
    """Find the best matching voice MP3 for a story"""
    # First try to find Aoede voice (user's preferred)
    pattern = f"{VOICES_FOLDER}/{story_base}*{preferred_voice}*.mp3"
    matches = glob.glob(pattern)
    if matches:
        return matches[0]
    # Fallback: any MP3 matching story base name
    pattern = f"{VOICES_FOLDER}/{story_base}*.mp3"
    matches = [f for f in glob.glob(pattern) if "metadata" not in f]
    if matches:
        return matches[0]
    # Last resort: latest MP3 in voices folder
    all_mp3 = [f for f in get_files(VOICES_FOLDER, ".mp3") if "metadata" not in f]
    return all_mp3[0] if all_mp3 else None


# ============================================================
# 🚀 MAIN
# ============================================================
def main():
    print("\n" + "="*65)
    print("  🎬 చిట్టి కథలు — AI Video Creator")
    print("  Pollinations AI (Free Images) + FFmpeg (Video)")
    print("="*65)

    # Check FFmpeg
    assembler = VideoAssembler()

    # Pick story
    story_files = get_files(STORIES_FOLDER, ".json")
    if not story_files:
        print(f"❌ No stories in '{STORIES_FOLDER}/' — none to convert to video.")
        # offer to auto-generate a story by invoking step 1
        resp = input("Generate a new story now? (Y/n): ").strip().lower()
        if resp in ("", "y", "yes"):
            # run the story generator script in sibling folder
            script_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "story", "story_generator.py"))
            print(f"🔄 Running story generator: {script_path}")
            try:
                subprocess.run(["python", script_path], check=True)
            except Exception as e:
                print(f"⚠️  Failed to run story_generator.py: {e}")
                return
            # re-scan for stories
            story_files = get_files(STORIES_FOLDER, ".json")
            if not story_files:
                print("❌ Still no stories found after generation. Aborting.")
                return
        else:
            print("Please run story_generator.py first and try again.")
            return

    print(f"\n📚 Stories available:\n")
    for i, f in enumerate(story_files[:5], 1):
        s = load_json(f)
        print(f"  {i}. [{s.get('story_type'):12}]  {s.get('title_telugu')}  ({s.get('generated_date','')})")
    print("  L → Latest story")

    sc = input("\nPick story (1-5 or L): ").strip().upper()
    idx = 0 if sc == "L" else max(0, int(sc)-1) if sc.isdigit() else 0
    idx = min(idx, len(story_files)-1)

    story     = load_json(story_files[idx])
    story_base = os.path.splitext(os.path.basename(story_files[idx]))[0]

    print(f"\n✅ Story   : {story.get('title_telugu')}")
    print(f"   Type    : {story.get('story_type_telugu')} ({story.get('story_type')})")

    # Find matching voice
    voice_path = find_voice_for_story(story_base)
    if not voice_path:
        print(f"\n❌ No voice MP3 found! Run voice_generator.py first (Step 2)")
        return
    print(f"   Voice   : {voice_path}")

    # Get audio duration
    audio_duration = assembler.get_audio_duration(voice_path)
    print(f"   Duration: {audio_duration:.1f} seconds")

    # Build scene list
    scenes = story.get("scene_descriptions", [])
    if not scenes:
        print("❌ No scene descriptions in story JSON!")
        return

    print(f"\n🎨 Generating {len(scenes)} cartoon scenes + intro + outro...")
    print("   This takes 2-4 minutes (Pollinations AI is free but takes time)")
    print("-"*65)

    # Initialize image generator and overlay helper
    img_gen   = PollinationsImageGenerator()
    story_type = story.get("story_type", "moral")
    ts        = datetime.now().strftime("%Y%m%d_%H%M%S")

    # ── Generate all images ───────────────────────────────────
    image_paths = []
    durations   = []

    # 1. Intro card
    print("\n  📌 Creating intro title card...")
    intro_path = f"{IMAGES_FOLDER}/{ts}_intro.jpg"
    TextOverlay.create_intro_card(
        story.get("title_telugu", ""),
        story.get("title_english", ""),
        story.get("story_type_telugu", "కథ"),
        intro_path
    )
    image_paths.append(intro_path)
    durations.append(INTRO_DURATION)
    print(f"  ✅ Intro card created")

    # 2. Story scenes
    scene_duration = max(
        MIN_SCENE_SECS,
        (audio_duration - INTRO_DURATION - OUTRO_DURATION) / len(scenes)
    )

    for i, scene_desc in enumerate(scenes, 1):
        prompt    = build_cartoon_prompt(scene_desc, story_type)
        filename  = f"{ts}_scene_{i:02d}.jpg"
        img_path  = img_gen.generate_image(prompt, filename, i)

        # Add title overlay
        img_with_text = TextOverlay.add_story_title(
            img_path,
            story.get("title_telugu", ""),
            i, len(scenes)
        )

        image_paths.append(img_with_text)
        durations.append(scene_duration)
        time.sleep(2)  # Small delay between Pollinations requests

    # 3. Moral card
    print("\n  📌 Creating moral card...")
    moral_path = f"{IMAGES_FOLDER}/{ts}_moral.jpg"
    TextOverlay.create_moral_card(
        story.get("moral_telugu", ""),
        story.get("moral_english", ""),
        moral_path
    )
    image_paths.append(moral_path)
    durations.append(5)
    print(f"  ✅ Moral card created")

    # 4. Outro card
    print("\n  📌 Creating outro subscribe card...")
    outro_path = f"{IMAGES_FOLDER}/{ts}_outro.jpg"
    TextOverlay.create_outro_card(outro_path)
    image_paths.append(outro_path)
    durations.append(OUTRO_DURATION)
    print(f"  ✅ Outro card created")

    # ── Assemble final video ──────────────────────────────────
    print(f"\n{'='*65}")
    total_dur = sum(durations)
    print(f"  📊 Total video duration: ~{total_dur:.0f} seconds ({total_dur/60:.1f} min)")
    print(f"  🎬 Now assembling final MP4 with FFmpeg...")

    output_path = f"{VIDEOS_FOLDER}/{ts}_{story_type}_final.mp4"
    final_video = assembler.create_video_from_images(
        image_paths, durations, voice_path, output_path
    )

    if final_video:
        print("\n" + "="*65)
        print("  🎉 VIDEO CREATED SUCCESSFULLY!")
        print("="*65)
        print(f"  📹 File    : {final_video}")
        print(f"  ⏱️  Duration: ~{total_dur:.0f} seconds")
        print(f"\n  📺 YouTube Details:")
        print(f"  Title      : {story.get('youtube_title')}")
        print(f"  Hashtags   : {story.get('hashtags')}")
        print(f"\n  ✅ Ready for Step 4 → YouTube Auto-Upload! 🚀")
    else:
        print("\n❌ Video creation failed. Check FFmpeg installation.")


if __name__ == "__main__":
    main()
