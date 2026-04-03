---
name: ai-news-podcast
description: "Converts a pasted AI news summary (with article URLs) into a 30-40 minute podcast with four hosts using ElevenLabs TTS"
version: 1.0.0
metadata:
  openclaw:
    env:
      - ELEVENLABS_API_KEY
    bins:
      - python3
---

# AI News Podcast Skill

This skill converts a pasted AI news summary into an engaging 30–40 minute podcast episode featuring four distinct host personalities. Given the news text, you will research each article, write a full podcast script, synthesize it with ElevenLabs voices, and assemble a final MP3.

---

## Input

The user provides the full text of an AI news summary directly in their message. The text may be in any readable format (Markdown, plain text, newsletter copy) and must include:
- Article headlines or titles
- Short summaries or descriptions
- Source URLs for each article

---

## The Four Hosts

You will write dialogue for these four hosts, each with a distinct personality and speaking style:

| Host | Role | Personality & Catchphrases |
|------|------|---------------------------|
| **ALEX** | Main anchor | Enthusiastic tech journalist. Keeps conversation moving. Asks clarifying questions. Uses phrases like *"Let's dig into that"*, *"Great point —"*, *"So what you're saying is..."* |
| **JORDAN** | Skeptical analyst | Challenges hype and bold claims. Brings counterpoints. Uses phrases like *"I'm a bit skeptical here..."*, *"But what's the actual evidence?"*, *"That sounds great on paper, but..."* |
| **SAM** | Technical expert | Explains how things work under the hood. Precise and detail-oriented. Uses phrases like *"Under the hood, what's happening is..."*, *"The key technical detail here is..."*, *"If you look at the architecture..."* |
| **MORGAN** | Societal futurist | Focuses on long-term impact, ethics, and societal implications. Uses phrases like *"Think about what this means in ten years..."*, *"The societal implication here is..."*, *"Who benefits — and who doesn't?"* |

All four hosts are warm and engaging. They genuinely disagree at times, build on each other's points, and occasionally make jokes. They do NOT all agree on everything — Jordan in particular must push back on at least one claim in every deep-dive segment.

---

## Workflow

### Step 1: Extract Articles

From the user's pasted news text, extract each article into a structured list:
- **Title**: The headline
- **Summary**: The description or body text
- **URL**: The source link if present
- **Category**: Model releases, research, industry news, open source, policy/ethics, tools, etc.

Identify 15–25 articles. Rank the top 4 as "deep dives" (the most significant or interesting stories of the week). The rest become "rapid fire" stories.

### Step 2: Research the Top 4 Articles

For each of the 4 deep-dive articles:
1. Use `web_search` to fetch and read the source URL to get the full article text
2. Use `web_search` to search for: *"[article title] expert reaction"* or *"[article title] analysis"*
3. Use `web_search` to search for related background context (e.g., prior work, competing approaches, historical context)

Compile a **research brief** for each deep-dive article containing:
- Key technical or factual details not in the original summary
- Expert or community reactions
- Related prior developments that give context
- Potential concerns, limitations, or counterarguments

### Step 3: Write the Podcast Script

Write a full podcast script targeting **5,000–5,500 words** (approximately 33–37 minutes at 150 words per minute). 

**Format every dialogue line as:**
```
[HOSTNAME]: dialogue text
```

**Insert segment markers as:**
```
[SEGMENT: Segment Name]
```

**Script structure:**

```
[SEGMENT: Intro]
(~300 words, ~2 minutes)
Alex welcomes listeners to the show, briefly introduces the other hosts, and teases the top stories of the week. Keep it punchy and energetic.

[SEGMENT: Story 1 - <Title>]
(~800 words, ~5-6 minutes)
Deep dive into the first top article. Alex introduces it. SAM explains the technical details. JORDAN raises a skeptical question or challenge. MORGAN explores the broader implications. The group discusses and debates. Use the research brief to add depth beyond the original summary.

[SEGMENT: Story 2 - <Title>]
(~800 words, ~5-6 minutes)
Same structure as Story 1.

[SEGMENT: Story 3 - <Title>]
(~800 words, ~5-6 minutes)
Same structure as Story 3.

[SEGMENT: Story 4 - <Title>]
(~800 words, ~5-6 minutes)
Same structure as Story 4.

[SEGMENT: Rapid Fire]
(~1,500 words, ~10 minutes)
Alex leads the group through the remaining articles at a faster pace. Each story gets 1–3 exchanges between hosts (60–90 seconds). Keep energy high. Hosts can react briefly but shouldn't dive deep.

[SEGMENT: Big Picture]
(~450 words, ~3 minutes)
The hosts step back and discuss the overarching themes and trends visible across this week's stories. What patterns are emerging? What should listeners pay attention to going forward? Each host gives their perspective.

[SEGMENT: Outro]
(~150 words, ~1 minute)
Alex wraps up, thanks the other hosts, and signs off. Keep it warm and brief.
```

**Quality requirements for the script:**
- Each host speaks in a consistent voice throughout — re-read earlier lines before writing new ones for the same host
- Hosts should reference and build on each other's points ("As Jordan said...", "That connects to what Sam was explaining...")
- JORDAN must push back or ask a challenging question in every deep-dive segment
- SAM must explain at least one technical detail in every deep-dive segment
- MORGAN must connect each deep-dive to a broader societal theme
- Include moments of light humor or personality — this is a podcast, not a news report
- Avoid filler phrases like "certainly", "absolutely", "great question"
- After writing, count the approximate word count. If under 4,500 words, expand the deep-dive discussions.

### Step 4: Save the Script

Save the complete script to a file at `./output/script.txt`. The file should contain only the formatted script lines (`[HOSTNAME]: text` and `[SEGMENT: name]` lines), with no additional commentary or headers.

Create the `./output/` directory if it does not exist.

### Step 5: Generate Audio Segments

Run the ElevenLabs TTS script to synthesize each line:

```bash
pip install -r scripts/requirements.txt -q
python3 scripts/generate_audio.py ./output/script.txt
```

This will create numbered MP3 segments in `./output/segments/` and a `./output/segments/segments.json` file recording which segment indices correspond to `[SEGMENT:]` boundaries.

If `ELEVENLABS_API_KEY` is not set, stop and inform the user that the environment variable must be configured before audio generation can proceed.

### Step 6: Mix Final Podcast

Assemble all segments into a single MP3:

```bash
python3 scripts/mix_audio.py ./output/segments/ ./output/podcast.mp3
```

### Step 7: Report Results

Tell the user:
- The path to the final podcast file (`./output/podcast.mp3`)
- The total podcast duration in minutes and seconds
- How many articles were covered (deep dives + rapid fire)
- The path to the script file (`./output/script.txt`) for reference

---

## Voice Configuration

The `generate_audio.py` script uses these default ElevenLabs voice IDs, which can be overridden by setting environment variables:

| Host | Env Var | Default Voice ID | Default Voice |
|------|---------|-----------------|---------------|
| ALEX | `ALEX_VOICE_ID` | `21m00Tcm4TlvDq8ikWAM` | Rachel |
| JORDAN | `JORDAN_VOICE_ID` | `pNInz6obpgDQGcFmaJgB` | Adam |
| SAM | `SAM_VOICE_ID` | `TxGEqnHWrfWFTfGW9XjX` | Josh |
| MORGAN | `MORGAN_VOICE_ID` | `EXAVITQu4vr4xnSDxMaL` | Bella |

---

## Error Handling

- If a source URL cannot be fetched during research, note this and proceed with the information available in the original summary
- If `generate_audio.py` fails on a particular line due to ElevenLabs API errors, it will skip that line and log the failure — a partial podcast may still be assembled
- If the total script word count is below 4,500 words after writing, expand the deep-dive discussions before proceeding to audio generation
