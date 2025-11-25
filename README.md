# 🌍 GlobalAdSync
### AI-Powered Multilingual Ad Copy Management & Translation Platform

GlobalAdSync lets marketers write ad copy once and automatically translate it into multiple languages with scoring, editing, and management capabilities. Built for real-world marketing workflows.

---

## 🚀 Features

- ✍️ Create & manage base ad copy  
- 🌎 Multi-language translation  
- 🧠 Quality scoring per translation  
- 🧩 Placeholder integrity (keeps `<product>` etc.)  
- 🔁 New-country backfill  
- 📊 Progress bar for translation batches  
- 🔍 Filtering & search  
- 🗄 Supabase storage  
- 🤖 Custom prompt-driven translation  

---

## 🧩 Architecture

Frontend: Streamlit
Backend: Python
Database: Supabase (Postgres)
Translation Models: AI language models
Authentication: Supabase (optional)

---

# 📚 Documentation

## 1. Technical Documentation
GlobalAdSync consists of:

### Supabase Tables:
- `ad_copies`
- `countries`
- `translations`
- `quality_scores` (optional)

### Key behaviors:
- Adding a new country triggers optional translation backfill  
- Editing the base ad enables re-translation  
- Quality scoring runs after translation  
- UI updates live from the database  

---

## 2. QA & Testing Summary

Testing was performed manually in real use flow:

- Created multiple test ads  
- Added countries (JP, DE, FR, ES…)  
- Ran bulk & single translation  
- Verified placeholder retention  
- Confirmed correct writing tone  
- Tested editing & scoring  
- Checked DB writes & updates  
- Tried invalid user actions to test warnings  
- Checked UI responsiveness  

Example test:
- Created: `"Get 50% off today!"`  
- Translated to FR  
- Received score: **92/100**, badge: 🟢  

Edge cases:
- Empty ad creation ⇒ blocked  
- No country selected ⇒ warning  
- Missing optional fields still translate correctly  

---

## 3. Ideas for Future Improvements

### Technical:
- Redis caching  
- Async job queue  
- Role-based permissions  
- Translation versioning  
- A/B testing system  

### UX:
- Inline edit in table  
- Dark/light mode  
- Country flags  
- Saveable filter presets  
- Smart search  

---

# 📖 User Manual (Marketer-Friendly)

### Step 1 — Create your base ad
Go to **Ad Copy Manager**  
Enter:
- Headline
- Main ad text  
- Product placeholder  
- Link text  

---

### Step 2 — Add countries
Go to **Country Manager**  
Examples:
- 🇫🇷 French  
- 🇯🇵 Japanese  
- 🇩🇪 German  
- 🇪🇸 Spanish  

Each has its own marketing tone & context.

---

### Step 3 — Translate  
Go to **Translation Dashboard**  
Select:
- Ads  
- Countries  
Click **Translate**

Watch the progress bar.

---

### Step 4 — Review quality  
Scores:
- 🟢 High (80–100)  
- 🟡 Medium (60–79)  
- 🔴 Low (<60)  

Edit translations as needed.

---

### Step 5 — Export  
Use results for:
- Google Ads  
- Meta Ads  
- TikTok  
- Emails  
- Landing pages  

---

# 💾 Installation

```bash
git clone git@github.com:AhsanWasim/ad-translation-tool.git
cd globaladsync
pip install -r requirements.txt
streamlit run app.py
```


## 🔑 Environment Setup

Create a `.env` file with:

SUPABASE_URL=
SUPABASE_KEY=
AI_API_KEY=



---

## 🧠 Developer Notes

- All translation is prompt-based  
- Placeholders remain intact  
- DB syncing is immediate  
- UI is fully extensible  

---

## 🤝 Contributing

Pull requests welcome!  
Open an issue for larger feature discussions.

---

## 🛡 License

MIT License

---

## 💬 Contact

For support, feature proposals, or collaboration — submit via GitHub issues.

---



