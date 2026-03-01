# 🌟 చిట్టి కథలు (Chitti Kathalu) — YouTube Automation
## Telugu Kids Stories Channel — Step by Step Setup

---

## 📁 Project Steps (Build One by One)
| Step | File | Status |
|------|------|--------|
| Step 1 | `story_generator.py` | ✅ Ready |
| Step 2 | `voice_generator.py` | 🔜 Coming Next |
| Step 3 | `video_creator.py` | 🔜 Coming Soon |
| Step 4 | `youtube_uploader.py` | 🔜 Coming Soon |
| Step 5 | `scheduler.py` | 🔜 Coming Soon |

---

## 🚀 STEP 1 SETUP — Story Generator

### 1. Install Python package
```bash
pip install google-generativeai
```

### 2. Get FREE Gemini API Key
1. Go to 👉 https://aistudio.google.com
2. Sign in with your Google account
3. Click **"Get API Key"** → **"Create API key in new project"**
4. Copy the key (starts with `AIza...`)

### 3. Add your API key
Open `story_generator.py` and find this line:
```python
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE"
```
Replace with your actual key:
```python
GEMINI_API_KEY = "AIzaXXXXXXXXXXXXXXXXXXX"
```

### 4. Run the script
```bash
python story_generator.py
```

### 5. Output
Stories are saved in `generated_stories/` folder as JSON files containing:
- Full story in Telugu
- YouTube title + description
- Hashtags
- Scene descriptions for animation

---

## 📊 Free Tier Limits (Gemini 2.0 Flash)
| Limit | Value |
|-------|-------|
| Requests per minute | 15 |
| Requests per day | 1,500 |
| Cost | FREE |

---

## 📺 Channel Info
- **Channel Name:** చిట్టి కథలు (Chitti Kathalu)
- **Story Types:** Moral, Fairy Tale, Animal, Mythological
- **Video Length:** 2-3 minutes
- **Upload Time:** 6:30 PM IST daily
- **Target:** Telugu kids aged 3-8 years
