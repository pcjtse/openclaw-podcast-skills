# AI News Podcast Skill for openclaw

Converts a pasted AI news summary into a fully-produced 30–40 minute podcast featuring four distinct host personalities. The skill researches each article, writes an engaging multi-host script using your configured LLM, and synthesizes audio via ElevenLabs TTS.

---

## Prerequisites

- **Python 3** 3.10 or newer
- An [ElevenLabs](https://elevenlabs.io) API key

---

## Installation

### 1. Install the skill

**From GitHub:**

```bash
clawhub clone pcjtse/openclaw-podcast-skills
clawhub install ./openclaw-podcast-skills
```

**From a local checkout:**

```bash
git clone https://github.com/pcjtse/openclaw-podcast-skills.git
clawhub install ./openclaw-podcast-skills
```

**Development mode (changes picked up automatically):**

```bash
clawhub install ./openclaw-podcast-skills --dev
```

### 2. Install Python dependencies

```bash
pip install -r scripts/requirements.txt
```

### 3. Configure your ElevenLabs API key

Add your ElevenLabs API key to `openclaw.json`. The skill reads from this file automatically.

**Option A — skill working directory** (takes priority):

```json
{
  "ELEVENLABS_API_KEY": "your-elevenlabs-api-key"
}
```

**Option B — user-level config** (applies to all skills):

Add the key to `~/.openclaw/openclaw.json`:

```json
{
  "ELEVENLABS_API_KEY": "your-elevenlabs-api-key"
}
```

> **Security note:** Do not commit `openclaw.json` containing API keys to version control. Add it to `.gitignore`.

#### Optional: customise host voices

By default the skill uses four pre-selected ElevenLabs voices. Override any of them in `openclaw.json`:

```json
{
  "ELEVENLABS_API_KEY": "your-elevenlabs-api-key",
  "ALEX_VOICE_ID":   "21m00Tcm4TlvDq8ikWAM",
  "JORDAN_VOICE_ID": "pNInz6obpgDQGcFmaJgB",
  "SAM_VOICE_ID":    "TxGEqnHWrfWFTfGW9XjX",
  "MORGAN_VOICE_ID": "EXAVITQu4vr4xnSDxMaL"
}
```

Browse available voice IDs at [elevenlabs.io/voice-library](https://elevenlabs.io/voice-library).

---

## Usage

Invoke the skill by pasting your AI news summary into the openclaw chat. The text can be in any readable format (Markdown, plain text, newsletter copy) as long as it includes article headlines, summaries, and source URLs.

**Example:**

```
/ai-news-podcast

# Weekly AI News — April 2, 2026

## GPT-5 released with 1M token context window
OpenAI has released GPT-5, featuring a 1 million token context window...
Source: https://openai.com/blog/gpt-5

## Google DeepMind's AlphaFold 3 predicts protein-ligand interactions
...
```

The skill will:
1. Extract and rank all articles from your input
2. Research the top 4 stories using web search
3. Write a 5,000–5,500 word podcast script with four hosts
4. Synthesise audio segments via ElevenLabs
5. Mix everything into a single MP3

Output files are saved to `./output/`:

```
output/
├── podcast.mp3        # Final podcast (~30-40 minutes)
└── script.txt         # Full transcript
```

---

## The four hosts

| Host | Role |
|------|------|
| **Alex** | Main anchor — keeps the conversation moving |
| **Jordan** | Skeptical analyst — challenges claims and hype |
| **Sam** | Technical expert — explains how things actually work |
| **Morgan** | Societal futurist — explores long-term implications |

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ELEVENLABS_API_KEY is not set` | Add the key to `openclaw.json` (see step 3) |
| Audio segments generated but no final MP3 | Run `python3 scripts/mix_audio.py ./output/segments/ ./output/podcast.mp3` manually |
| Script is under 4,500 words | Ask the skill to expand the deep-dive discussions before generating audio |
