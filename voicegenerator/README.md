# 🌟 చిట్టి కథలు (Chitti Kathalu) — YouTube Automation

## 📁 Project Steps
| Step | File | Status |
|------|------|--------|
| Step 1 | `story_generator.py` | ✅ Done |
| Step 2 | `voice_generator.py` | ✅ Done |
| Step 3 | `video_creator.py` | 🔜 Next |
| Step 4 | `youtube_uploader.py` | 🔜 Coming |
| Step 5 | `scheduler.py` | 🔜 Coming |

---

## 🚀 STEP 2 SETUP — Telugu Voice Over

### 1. Install package
```bash
pip install google-cloud-texttospeech
```

### 2. Get FREE Google Cloud TTS API Key
1. Go to → https://console.cloud.google.com
2. Create new project → name it **chitti-kathalu**
3. Search **"Cloud Text-to-Speech API"** → Click Enable
4. Go to **APIs & Services → Credentials**
5. Click **Create Credentials → API Key**
6. Copy the key and paste in `voice_generator.py`

### 3. Run
```bash
python voice_generator.py
```

### 4. Output
```
generated_voices/
  ├── 20260228_143805_moral_female.mp3   ← Female voice
  ├── 20260228_143805_moral_male.mp3     ← Male voice
  └── 20260228_143805_moral_metadata.json
```

---

## 🎙️ Telugu Voices Used
| Voice | Type | Gender |
|-------|------|--------|
| te-IN-Standard-A | Standard | Female స్త్రీ |
| te-IN-Standard-B | Standard | Male పురుష |

## 📊 Free Tier Limits
| Tier | Monthly Free |
|------|-------------|
| Standard voices | 4 Million characters |
| WaveNet voices | 1 Million characters |

---

## 🗺️ Pipeline Flow
```
story_generator.py  →  generated_stories/*.json
       ↓
voice_generator.py  →  generated_voices/*.mp3
       ↓
video_creator.py    →  generated_videos/*.mp4   (Step 3)
       ↓
youtube_uploader.py →  YouTube Channel          (Step 4)
```
