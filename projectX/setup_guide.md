# 🤖 JARVIS Setup Guide - Complete from Zero

This guide walks you through setting up your personal AI assistant on Replit + Supabase.

---

## **STEP 1: Set Up Supabase (Database)**

### 1.1 Create Supabase Account
- Go to https://supabase.com
- Click "Sign up"
- Use GitHub or email
- Create new project (name it "jarvis")
- Wait for initialization (~2 min)

### 1.2 Create Database Table
- Go to "SQL Editor" in Supabase dashboard
- Click "New Query"
- Paste this SQL:

```sql
-- Create vector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create documents table
CREATE TABLE documents (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    source TEXT,
    subject TEXT,
    from_addr TEXT,
    date TEXT,
    content TEXT,
    embedding vector(1536),
    created_at TIMESTAMP DEFAULT now()
);

-- Create index for faster searches
CREATE INDEX ON documents USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Create RPC function for similarity search
CREATE OR REPLACE FUNCTION match_documents (
    query_embedding vector(1536),
    match_count int DEFAULT 5
)
RETURNS TABLE (
    id uuid,
    source TEXT,
    subject TEXT,
    from_addr TEXT,
    date TEXT,
    content TEXT,
    similarity float
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        documents.id,
        documents.source,
        documents.subject,
        documents.from_addr,
        documents.date,
        documents.content,
        1 - (documents.embedding <=> query_embedding) AS similarity
    FROM documents
    ORDER BY documents.embedding <=> query_embedding
    LIMIT match_count;
END;
$$ LANGUAGE plpgsql;
```

- Click "Run"
- You should see "✅ Success"

### 1.3 Get Your Credentials
- Go to Settings → Database → Connection string
- Copy the full connection string (looks like: `postgresql://...`)
- Go to Settings → API → Copy "URL" and "anon key"
- Save these somewhere safe

---

## **STEP 2: Set Up Google OAuth (For Gmail)**

### 2.1 Create Google Cloud Project
- Go to https://console.cloud.google.com/
- Click "Select a Project" → "New Project"
- Name it "Jarvis"
- Click "Create"

### 2.2 Enable APIs
- Search "Gmail API" in search bar → Click "Enable"
- Search "Google Calendar API" in search bar → Click "Enable"
- Search "Google Drive API" in search bar → Click "Enable"

### 2.3 Create OAuth Credentials
- Go to "Credentials" (left sidebar)
- Click "Create Credentials" → "OAuth client ID"
- Choose "Desktop application"
- Name it "Jarvis"
- Click "Create"
- You'll see a popup with Client ID and Secret
- **Save these!**

### 2.4 Download credentials.json
- Click the download icon next to your created credential
- Save as `credentials.json`
- Keep this file safe (don't share!)

---

## **STEP 3: Create Discord Bot**

### 3.1 Create Discord Application
- Go to https://discord.com/developers/applications
- Click "New Application"
- Name it "Jarvis"
- Go to "Bot" → "Add Bot"

### 3.2 Copy Bot Token
- Under "TOKEN", click "Copy"
- Save this somewhere safe

### 3.3 Set Bot Permissions
- Go to "OAuth2" → "URL Generator"
- Select scopes: `bot`
- Select permissions: `Send Messages`, `Read Messages/View Channels`
- Copy the generated URL
- Paste in browser to add bot to your Discord server

---

## **STEP 4: Set Up Replit**

### 4.1 Create Replit Project
- Go to https://replit.com
- Click "Create Repl"
- Choose "Python"
- Name it "jarvis"

### 4.2 Upload Files
In Replit file explorer, create these files:

**requirements.txt** - Copy from the file provided

**bot.py** - Copy from the file provided

**rag.py** - Copy from the file provided

**.env** - Create and fill in:
```
OPENAI_API_KEY=your_openai_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
DISCORD_BOT_TOKEN=your_discord_token
```

### 4.3 Install Dependencies
- Click "Run"
- Replit will install from requirements.txt

### 4.4 Start Bot
- Click "Run" again
- You should see: `✅ Jarvis is online as Jarvis#...`

### 4.5 Keep Running 24/7
- Click on your username → Replit+ (upgrade, but there's a free tier option)
- Or use: https://uptimerobot.com (free)

---

## **STEP 5: Add Gmail Data (Laptop)**

### 5.1 Set Up Locally
```bash
# Create folder
mkdir jarvis && cd jarvis

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 5.2 Add credentials.json
- Place your `credentials.json` in the jarvis folder

### 5.3 Create .env
```
OPENAI_API_KEY=your_openai_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

### 5.4 Run Ingestions (in order)

**Gmail:**
```bash
python ingest_gmail.py
```
- Browser will open for Gmail authentication
- Click "Allow"
- You'll see: `✅ Ingestion complete! Added X email chunks`

**Google Drive:**
```bash
python ingest_drive.py
```
- Browser will open for Drive authentication
- Click "Allow"
- You'll see: `✅ Drive ingestion complete! Added X file chunks`

**Google Calendar:**
```bash
python ingest_calendar.py
```
- Browser will open for Calendar authentication
- Click "Allow"
- Choose: `1` for future events, `2` for past, `3` for both
- You'll see: `✅ Calendar ingestion complete! Added X events`

---

## **STEP 6: Test from Discord**

1. Go to your Discord server
2. Type: `!ask What emails did I get today?`
3. Jarvis will answer! 🎉

---

## **Troubleshooting**

### "SUPABASE_URL not found"
- Make sure .env file exists and has all keys
- Restart the bot

### "credentials.json not found"
- Download from Google Cloud Console
- Place in same folder as ingest_gmail.py

### "No emails found"
- Make sure Gmail authentication succeeded
- Check that you have emails in Gmail

### "Error connecting to Supabase"
- Verify SUPABASE_URL and SUPABASE_KEY are correct
- Check that table "documents" was created

### Bot won't start on Replit
- Check .env has DISCORD_BOT_TOKEN
- Make sure bot is added to your Discord server
- Check Replit console for error messages

---

## **Next Steps**

1. **Test with Discord**: `!ask <your question>`
2. **Add more data**: Create ingest_drive.py, ingest_calendar.py (similar to ingest_gmail.py)
3. **Schedule syncs**: Use APScheduler to auto-update data
4. **Improve**: Fine-tune on your writing style, customize prompts

---

## **Important Files Checklist**

```
jarvis/
├── bot.py                 # Discord bot
├── rag.py                 # Core AI logic
├── ingest_gmail.py        # Email ingestion
├── requirements.txt       # Dependencies
├── .env                   # Your secrets (DON'T share!)
└── credentials.json       # Google auth (DON'T share!)
```

---

## **Cost Breakdown**

| Service | Cost |
|---------|------|
| OpenAI API | Pay per use (~$0.01 per request) |
| Supabase | Free (500MB) |
| Replit | Free with limits |
| Discord | Free |
| Google | Free |

**Total: ~$0 startup, minimal ongoing**

---

## **You're Done! 🚀**

Your personal AI assistant is now running 24/7 with full context of your emails.

Ask it anything: `!ask <question>`




# ✅ JARVIS Quick Start Checklist

Print this and check off each item as you complete it.

---

## **PHASE 1: Account Setup (15 minutes)**

### Supabase
- [ ] Sign up at https://supabase.com
- [ ] Create new project "jarvis"
- [ ] Run SQL setup (paste from SETUP_GUIDE.md)
- [ ] Copy SUPABASE_URL from Settings → API
- [ ] Copy SUPABASE_KEY (anon key)

### Google Cloud
- [ ] Go to https://console.cloud.google.com/
- [ ] Create new project
- [ ] Enable Gmail API
- [ ] Enable Google Calendar API
- [ ] Enable Google Drive API
- [ ] Create OAuth credentials (Desktop app)
- [ ] Download credentials.json
- [ ] Save GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET

### Discord
- [ ] Go to https://discord.com/developers/applications
- [ ] Create new application "Jarvis"
- [ ] Add Bot
- [ ] Copy bot TOKEN
- [ ] Set permissions (Send Messages, Read Messages)
- [ ] Invite bot to your server

### OpenAI
- [ ] Go to https://platform.openai.com/
- [ ] Create API key
- [ ] Save OPENAI_API_KEY

---

## **PHASE 2: Local Setup (10 minutes)**

- [ ] Create folder: `mkdir jarvis && cd jarvis`
- [ ] Create virtual env: `python -m venv venv`
- [ ] Activate venv: `source venv/bin/activate`
- [ ] Download all files from this setup
- [ ] Place credentials.json in folder
- [ ] Create .env with all 4 API keys:
  - [ ] OPENAI_API_KEY
  - [ ] SUPABASE_URL
  - [ ] SUPABASE_KEY
  - [ ] DISCORD_BOT_TOKEN
- [ ] Run: `pip install -r requirements.txt`

---

## **PHASE 3: Test Locally (10 minutes)**

- [ ] Run: `python ingest_gmail.py`
- [ ] Allow Gmail access in browser
- [ ] Wait for emails to be added (~1 min)
- [ ] See "✅ Ingestion complete!" message
- [ ] Run: `python ingest_drive.py`
- [ ] Allow Drive access in browser
- [ ] See "✅ Drive ingestion complete!" message
- [ ] Run: `python ingest_calendar.py`
- [ ] Allow Calendar access in browser
- [ ] Choose option 3 (past + future events)
- [ ] See "✅ Calendar ingestion complete!" message
- [ ] Run: `python bot.py`
- [ ] See "✅ Jarvis is online" message

---

## **PHASE 4: Test Discord (2 minutes)**

- [ ] Open Discord
- [ ] In your server, type: `!ask What emails did I get from gmail?`
- [ ] Jarvis responds! 🎉
- [ ] Try: `!status` to check database
- [ ] Try: `!help` for all commands

---

## **PHASE 5: Deploy to Replit (10 minutes)**

- [ ] Go to https://replit.com
- [ ] Create new Repl (Python)
- [ ] Create bot.py, rag.py, requirements.txt
- [ ] Create .env with API keys
- [ ] Click "Run"
- [ ] See "✅ Jarvis is online" in console

---

## **PHASE 6: Keep Running 24/7 (Optional)**

Option A: Use Replit Always On (paid feature)
- [ ] Upgrade to Replit+
- [ ] Enable "Always On"

Option B: Use UptimeRobot (Free)
- [ ] Go to https://uptimerobot.com
- [ ] Create free account
- [ ] Add uptimerobot.com as "ping" endpoint
- [ ] Set to check every 5 minutes

---

## **NEXT: Add More Data Sources**

After Phase 6, you can expand with even more data:

### Already Included ✅
- [x] Gmail emails
- [x] Google Drive documents
- [x] Google Calendar events

### Coming Soon (Optional)
- [ ] Auto-sync (APScheduler for automatic updates)
- [ ] Web interface (React frontend)
- [ ] Slack integration
- [ ] Note-taking apps (Notion, Obsidian)

---

## **Troubleshooting Quick Fixes**

| Problem | Solution |
|---------|----------|
| "KeyError: SUPABASE_URL" | Add all 4 keys to .env and restart |
| "credentials.json not found" | Download from Google Cloud and place in folder |
| "bot won't start" | Check DISCORD_BOT_TOKEN in .env |
| "no emails found" | Make sure Gmail auth worked (check token.pickle) |
| "Supabase connection error" | Verify URL and KEY are correct |

---

## **You're All Set! 🚀**

Your personal AI assistant is ready.

**From anywhere on your phone:**
```
Discord Server → !ask <question> → Jarvis answers instantly
```

**With full context of:**
- ✅ All your emails
- ✅ All your documents (Google Drive)
- ✅ All your calendar events (past & future)
- ✅ Any other data source you add

**Next improvement ideas:**
- Fine-tune on your writing style
- Add document summarization
- Create custom commands
- Build web dashboard

---

## **Questions?**

Check SETUP_GUIDE.md for detailed help on each step.