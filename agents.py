"""
Hormone Hacker Content Agents
Standalone Python agents for Phyllis Thompson / Hormone Hacker
Runs on Railway via cron schedule — no Make.com required
Emails all output to info@phyllishannahthompson.com via Resend API
"""

import os
import sys
import json
import requests
from datetime import datetime

# ── Configuration ────────────────────────────────────────────────────────────
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]  # Set in Railway Variables
RESEND_API_KEY = os.environ["RESEND_API_KEY"]  # Set in Railway Variables
FROM_EMAIL = "hormones@support.phyllishannahthompson.com"
TO_EMAIL = "info@phyllishannahthompson.com"

BRAND_CONTEXT = """You are a content agent for Hormone Hacker, a women's health brand created by Phyllis Thompson.
Hormone Hacker helps women 35-55 balance hormones naturally — especially during perimenopause and menopause.
Products: Hormone Hacker Membership ($24.99/month), Hannah's Hormone Tea, GLP-1 Reset Guide, one-on-one coaching.
Brand voice: warm, empowering, science-backed but accessible, like a knowledgeable best friend.
Audience: women 35-55 dealing with fatigue, weight gain, brain fog, hot flashes, mood swings.
Key platforms: Instagram, Facebook, TikTok, LinkedIn (B2B corporate wellness).
Never use em dashes. Format output as clean HTML."""

# ── OpenAI Helper ─────────────────────────────────────────────────────────────
def ask_openai(prompt, max_tokens=2000):
    resp = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": BRAND_CONTEXT},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": 0.7
        }
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]

# ── Resend Email Helper ───────────────────────────────────────────────────────
def send_email(subject, html_body, to=None):
    to_addr = to or TO_EMAIL
    resp = requests.post(
        "https://api.resend.com/emails",
        headers={
            "Authorization": f"Bearer {RESEND_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "from": FROM_EMAIL,
            "to": [to_addr],
            "subject": subject,
            "html": html_body
        }
    )
    resp.raise_for_status()
    result = resp.json()
    print(f"  Email sent: {subject} -> {to_addr} (ID: {result.get('id', 'unknown')})")
    return result

# ── Agent 1: Content Agent ────────────────────────────────────────────────────
def run_content_agent():
    print("Running Content Agent — AI Blog, Social & TikTok Draft Generator...")
    today = datetime.now().strftime("%B %d, %Y")
    prompt = f"""Today is {today}. Generate a full week of content for Hormone Hacker across all platforms.

Create the following:

1. INSTAGRAM POSTS (3 posts)
   - Each: 50-75 words, hook line, body, call to action, 10-15 hashtags
   - Topics: rotate between hormone balance tips, membership benefits, Hannah's Hormone Tea, GLP-1 Reset Guide

2. FACEBOOK POSTS (3 posts)
   - Each: 100-150 words, community-focused, shareable, question or poll idea
   - Match the Instagram topics but expand for Facebook's longer format

3. TIKTOK SCRIPTS (2 scripts)
   - Each: 150-200 words, hook (first 3 seconds), main content, CTA
   - Format: [HOOK], [CONTENT], [CTA] labels
   - Topics: one educational (hormone tip), one personal story / transformation

4. BLOG POST DRAFT
   - Title (SEO-optimized, 60 chars max)
   - Meta description (155 chars max)
   - Full post (600-800 words)
   - Target keywords (5)
   - Topic: choose the most timely hormone health topic for women 35-55

5. EMAIL NEWSLETTER DRAFT
   - Subject line (A/B test: provide 2 options)
   - Preview text (90 chars)
   - Full email body (300-400 words)
   - CTA button text and link destination

Format everything as clean HTML with clear section headers in purple (#7C3AED). Include a date stamp."""

    content = ask_openai(prompt, max_tokens=3000)
    send_email(
        subject=f"Hormone Hacker Content Agent — Weekly Content Drafts ({today})",
        html_body=f"<h2 style='color:#7C3AED;font-family:Georgia,serif;'>Hormone Hacker Weekly Content Package</h2><p style='color:#666;font-size:13px;'>Generated {today} by Railway Content Agent</p><hr>{content}"
    )
    print("  Content Agent complete.")

# ── Agent 2: Email Agent — Nurture Sequence ───────────────────────────────────
def run_email_nurture_agent():
    print("Running Email Agent — Nurture Email Draft Generator...")
    today = datetime.now().strftime("%B %d, %Y")
    prompt = f"""Today is {today}. Write a 5-email nurture sequence for Hormone Hacker.

This sequence is for women who signed up for a free lead magnet (GLP-1 Reset Guide or hormone quiz) but have not yet joined the membership.

For each email provide:
- Email number and send timing (e.g., Email 1: Send immediately, Email 2: Send Day 2)
- Subject line (A/B test: 2 options)
- Preview text (90 chars max)
- Full email body (250-350 words)
- CTA (what to click, where it goes)

Sequence arc:
- Email 1: Welcome + deliver the lead magnet, set expectations
- Email 2: Biggest hormone myth busted (educational value)
- Email 3: Success story / transformation (social proof)
- Email 4: What's inside the Hormone Hacker Membership (soft sell)
- Email 5: Last chance / urgency (direct offer, $24.99/month)

Brand voice: warm, empowering, like a knowledgeable best friend. Never use em dashes.
Format as clean HTML with purple (#7C3AED) headers."""

    content = ask_openai(prompt, max_tokens=3000)
    send_email(
        subject=f"Hormone Hacker Email Agent — Nurture Sequence Drafts ({today})",
        html_body=f"<h2 style='color:#7C3AED;font-family:Georgia,serif;'>Hormone Hacker Nurture Email Sequence</h2><p style='color:#666;font-size:13px;'>Generated {today} by Railway Email Agent</p><hr>{content}"
    )
    print("  Email Nurture Agent complete.")

# ── Agent 3: Email Agent — Workshop Lead Welcome ──────────────────────────────
def run_email_workshop_agent():
    print("Running Email Agent — Workshop Lead Welcome Sequence...")
    today = datetime.now().strftime("%B %d, %Y")
    prompt = f"""Today is {today}. Write a workshop lead welcome sequence for Hormone Hacker.

This is for women who registered for a free Hormone Hacker workshop or webinar (e.g., "5 Signs Your Hormones Are Out of Balance" or "GLP-1 and Your Hormones").

Write 3 emails:

Email 1 — Confirmation (send immediately after registration)
- Confirm their spot
- Build excitement about what they will learn
- Add to calendar link placeholder
- Introduce Phyllis Thompson briefly

Email 2 — Pre-workshop prep (send 1 day before)
- Remind them of the workshop date/time
- Give them 1 quick action to do before the workshop
- Share a teaser of the most valuable thing they will learn
- Build urgency (limited spots, live only)

Email 3 — Post-workshop follow-up (send 1 hour after workshop ends)
- Thank them for attending
- Recap the 3 biggest takeaways
- Offer the Hormone Hacker Membership as the next step ($24.99/month)
- Include a special offer or bonus for workshop attendees

For each email: subject line (2 A/B options), preview text, full body, CTA.
Format as clean HTML with purple (#7C3AED) headers. Never use em dashes."""

    content = ask_openai(prompt, max_tokens=2500)
    send_email(
        subject=f"Hormone Hacker Email Agent — Workshop Welcome Sequence ({today})",
        html_body=f"<h2 style='color:#7C3AED;font-family:Georgia,serif;'>Hormone Hacker Workshop Email Sequence</h2><p style='color:#666;font-size:13px;'>Generated {today} by Railway Email Agent</p><hr>{content}"
    )
    print("  Email Workshop Agent complete.")

# ── Agent 4: LinkedIn B2B Newsletter Agent ────────────────────────────────────
def run_linkedin_agent():
    print("Running LinkedIn B2B Newsletter Agent — Monday Corporate Wellness...")
    today = datetime.now().strftime("%B %d, %Y")
    prompt = f"""Today is {today}. Write a LinkedIn newsletter article for Phyllis Thompson targeting HR Directors, Chief People Officers, and corporate wellness decision-makers.

Article topic: Choose the most compelling and timely topic about perimenopause, menopause, or hormonal health in the workplace for women 35-55. Make it feel urgent and relevant to business leaders.

Article requirements:
- LinkedIn article title (compelling, professional, 60-80 chars)
- Opening hook (2-3 sentences that stop the scroll)
- Full article body (600-800 words)
- Structure: Problem -> Data/Research -> Business Impact -> Solution -> Call to Action
- Include 2-3 statistics about menopause in the workplace (you may cite general research)
- Position Phyllis Thompson as the expert companies should hire to create perimenopause/menopause wellness programs
- End with a soft CTA: invite HR Directors to book a discovery call or reply to discuss a corporate wellness program
- 5 LinkedIn hashtags

Also write:
- A LinkedIn post to promote the article (150 words, hook + summary + link placeholder)
- A LinkedIn comment reply template (50 words) for when people engage with the post

Format as clean HTML with professional dark blue (#1E3A5F) headers. Never use em dashes."""

    content = ask_openai(prompt, max_tokens=2500)
    send_email(
        subject=f"Hormone Hacker LinkedIn Agent — Corporate Wellness Article ({today})",
        html_body=f"<h2 style='color:#1E3A5F;font-family:Georgia,serif;'>LinkedIn B2B Newsletter — Corporate Wellness</h2><p style='color:#666;font-size:13px;'>Generated {today} by Railway LinkedIn Agent | Copy-paste into LinkedIn Newsletter</p><hr>{content}"
    )
    print("  LinkedIn Agent complete.")

# ── Agent 5: App Agent ────────────────────────────────────────────────────────
def run_app_agent():
    print("Running App Agent — Hormone Hacker App & Dashboard Improvements...")
    today = datetime.now().strftime("%B %d, %Y")
    prompt = f"""Today is {today}. Generate a weekly improvement brief for the Hormone Hacker App and member dashboard.

The Hormone Hacker App is a membership platform ($24.99/month) with:
- 4-week hormone reset roadmap
- Hormone-balancing recipes
- Workout plans
- FSA/HSA eligible
- Thursday 7PM Instagram Lives with Phyllis
- GLP-1 Reset Guide
- One-on-one coaching booking

Generate the following:

1. WEEKLY APP IMPROVEMENT IDEAS (5 ideas)
   - Feature or content improvement
   - Why it would increase retention or conversion
   - Estimated effort (Low/Medium/High)
   - Priority score (1-10)

2. MEMBER ENGAGEMENT EMAIL (ready to send)
   - Subject line
   - 200-word email to current members encouraging them to use a specific feature this week
   - Personalization tips

3. MEMBER SUPPORT RESPONSE TEMPLATES (5 templates)
   - Common questions members ask
   - Warm, helpful response for each
   - Topics: cancellation, billing, content access, coaching booking, GLP-1 questions

4. WEEKLY MEMBER WIN SPOTLIGHT
   - Template for featuring a member success story on social media
   - Instagram caption, Facebook post, and email newsletter snippet

Format as clean HTML with purple (#7C3AED) headers. Never use em dashes."""

    content = ask_openai(prompt, max_tokens=2500)
    send_email(
        subject=f"Hormone Hacker App Agent — Weekly Improvement Brief ({today})",
        html_body=f"<h2 style='color:#7C3AED;font-family:Georgia,serif;'>Hormone Hacker App Agent — Weekly Brief</h2><p style='color:#666;font-size:13px;'>Generated {today} by Railway App Agent</p><hr>{content}"
    )
    print("  App Agent complete.")

# ── Agent 6: Daily Task Dispatcher ───────────────────────────────────────────
def run_task_dispatcher():
    print("Running Daily Task Dispatcher — Hormone Hacker Command Center...")
    today = datetime.now().strftime("%B %d, %Y")
    day_of_week = datetime.now().strftime("%A")
    prompt = f"""Today is {day_of_week}, {today}. Generate a daily action brief for Phyllis Thompson at Hormone Hacker.

This is her daily command center briefing. Based on the day of the week, generate the most relevant tasks and content.

Include:

1. TODAY'S PRIORITY TASKS (3-5 tasks)
   - Specific, actionable tasks for today
   - Tailored to {day_of_week} (e.g., Monday = LinkedIn article, Thursday = Instagram Live prep)
   - Each task: what to do, why it matters today, time estimate

2. CONTENT TO POST TODAY
   - 1 Instagram post (ready to copy-paste with caption and hashtags)
   - 1 Facebook post (ready to copy-paste)
   - If {day_of_week} is Monday: LinkedIn article reminder
   - If {day_of_week} is Thursday: Instagram Live reminder and talking points

3. DAILY AFFIRMATION / BRAND MESSAGE
   - One powerful sentence Phyllis can share as a story or quote post
   - Aligned with hormone health and women's empowerment

4. QUICK WINS (2-3 items)
   - Small actions that take under 5 minutes
   - Examples: reply to top comment, share a member win, update a story

5. THIS WEEK'S FOCUS REMINDER
   - One sentence reminding Phyllis of the week's main content theme

Format as clean HTML with a warm, motivating tone. Use purple (#7C3AED) headers. Never use em dashes."""

    content = ask_openai(prompt, max_tokens=2000)
    send_email(
        subject=f"Hormone Hacker Daily Brief — {day_of_week}, {today}",
        html_body=f"<h2 style='color:#7C3AED;font-family:Georgia,serif;'>Good morning, Phyllis! Here is your Daily Brief.</h2><p style='color:#666;font-size:13px;'>Generated {today} by Railway Task Dispatcher</p><hr>{content}"
    )
    print("  Task Dispatcher complete.")

# ── Agent 7: Trial Reel System ────────────────────────────────────────────────
def run_trial_reel_agent():
    print("Running Trial Reel Agent — Daily TikTok Growth Brief...")
    today = datetime.now().strftime("%B %d, %Y")
    day_of_week = datetime.now().strftime("%A")
    prompt = f"""Today is {day_of_week}, {today}. Generate a TikTok Trial Reel brief for Hormone Hacker.

Phyllis Thompson is testing TikTok content to find what resonates with women 35-55 dealing with hormone imbalance. She records short reels (30-90 seconds) and tracks which formats perform best.

Generate:

1. TODAY'S REEL BRIEF
   - Format: choose one of (Trend Remix, Raw Thought/Lesson, Hook Test)
   - Hook (first 3 seconds — must stop the scroll)
   - Full script (150-200 words, conversational, like talking to a friend)
   - On-screen text suggestions (3-5 text overlays)
   - Trending audio suggestion (describe the vibe/style, not a specific song)
   - Hashtags (10-15, mix of niche and broad)
   - Why this reel has viral potential

2. HOOK VARIATIONS (3 alternative hooks for A/B testing)
   - Each hook is a different angle on the same topic
   - Label: Curiosity Hook, Pain Point Hook, Controversy Hook

3. ENGAGEMENT PROMPT
   - A question to ask in the caption to drive comments
   - A reply template for the first 10 comments (to boost algorithm)

{"4. WEEKLY REEL STRATEGY (Monday only)" if day_of_week == "Monday" else ""}
{"   - 5 reel ideas for the week ahead" if day_of_week == "Monday" else ""}
{"   - Content calendar: which format to test each day" if day_of_week == "Monday" else ""}
{"   - One trend to jump on this week" if day_of_week == "Monday" else ""}

Format as clean HTML with dark TikTok-style headers (#1a1a1a background, white text for headers). Never use em dashes."""

    content = ask_openai(prompt, max_tokens=2000)
    send_email(
        subject=f"Hormone Hacker Trial Reel Brief — {day_of_week}, {today}",
        html_body=f"<h2 style='color:#7C3AED;font-family:Georgia,serif;'>TikTok Trial Reel Brief</h2><p style='color:#666;font-size:13px;'>Generated {today} by Railway Trial Reel Agent</p><hr>{content}"
    )
    print("  Trial Reel Agent complete.")

# ── Main Runner ───────────────────────────────────────────────────────────────
AGENTS = {
    "content": run_content_agent,
    "email_nurture": run_email_nurture_agent,
    "email_workshop": run_email_workshop_agent,
    "linkedin": run_linkedin_agent,
    "app": run_app_agent,
    "dispatcher": run_task_dispatcher,
    "trial_reel": run_trial_reel_agent,
}

def main():
    args = sys.argv[1:]
    today = datetime.now().strftime("%A")  # Monday, Tuesday, etc.

    if not args or args[0] == "all":
        # Run all agents
        print(f"\n=== Hormone Hacker Agents — Running ALL ({datetime.now().strftime('%Y-%m-%d %H:%M')}) ===\n")
        for name, fn in AGENTS.items():
            try:
                fn()
            except Exception as e:
                print(f"  ERROR in {name}: {e}")
    elif args[0] == "daily":
        # Run daily agents (dispatcher + trial reel every day, linkedin on Mondays)
        print(f"\n=== Hormone Hacker Agents — Daily Run ({today}) ===\n")
        daily_agents = ["dispatcher", "trial_reel"]
        if today == "Monday":
            daily_agents += ["linkedin", "content"]
        if today in ["Tuesday", "Wednesday"]:
            daily_agents += ["email_nurture"]
        for name in daily_agents:
            try:
                AGENTS[name]()
            except Exception as e:
                print(f"  ERROR in {name}: {e}")
    elif args[0] == "weekly":
        # Run weekly agents (content, email sequences)
        print(f"\n=== Hormone Hacker Agents — Weekly Run ===\n")
        for name in ["content", "email_nurture", "email_workshop", "app"]:
            try:
                AGENTS[name]()
            except Exception as e:
                print(f"  ERROR in {name}: {e}")
    elif args[0] in AGENTS:
        # Run a specific agent
        print(f"\n=== Running: {args[0]} ===\n")
        try:
            AGENTS[args[0]]()
        except Exception as e:
            print(f"  ERROR: {e}")
            sys.exit(1)
    else:
        print(f"Unknown agent: {args[0]}")
        print(f"Available: {', '.join(AGENTS.keys())} | all | daily | weekly")
        sys.exit(1)

    print(f"\n=== All done. ===\n")

if __name__ == "__main__":
    main()
