"""
Hormone Hacker Content Agents
Standalone Python agents for Phyllis Thompson / Hormone Hacker
Runs on Railway via cron schedule — no Make.com required
Auto-posts to GHL Social Planner (Facebook, Instagram, LinkedIn, TikTok)
Emails all output to Phyllis@phyllishannahthompson.com via Resend API
"""

import os
import sys
import json
import requests
from datetime import datetime, timedelta, timezone

# ── Configuration ────────────────────────────────────────────────────────────
OPENAI_API_KEY  = os.environ.get("OPENAI_API_KEY", "")
RESEND_API_KEY  = os.environ.get("RESEND_API_KEY", "re_axgyN98F_F3A4LdYgiscpkDMzJRpHWUab")
GHL_API_KEY     = os.environ.get("GHL_API_KEY", "pit-7fe5537a-e091-4b8c-842d-8536cd9aa801")
GHL_LOCATION_ID = os.environ.get("GHL_LOCATION_ID", "jQOzG0xh0TF0mw1tyh8t")

FROM_EMAIL = "hormones@support.phyllishannahthompson.com"
TO_EMAIL   = "Phyllis@phyllishannahthompson.com"

# ── Branded Instagram Images (CDN URLs, mapped by day/pillar) ────────────────
INSTAGRAM_IMAGES = {
    "Monday":    "https://d2xsxph8kpxj0f.cloudfront.net/310519663375052884/KzUdmZmQg5hpo2Lg4ccVuH/hh_instagram_monday_glp1_d73ab32a.png",
    "Tuesday":   "https://d2xsxph8kpxj0f.cloudfront.net/310519663375052884/KzUdmZmQg5hpo2Lg4ccVuH/hh_instagram_tuesday_nutrition_bbc78077.png",
    "Wednesday": "https://d2xsxph8kpxj0f.cloudfront.net/310519663375052884/KzUdmZmQg5hpo2Lg4ccVuH/hh_instagram_quote_card_9d49358d.png",
    "Thursday":  "https://d2xsxph8kpxj0f.cloudfront.net/310519663375052884/KzUdmZmQg5hpo2Lg4ccVuH/hh_instagram_thursday_perimenopause_5fc82c23.png",
    "Friday":    "https://d2xsxph8kpxj0f.cloudfront.net/310519663375052884/KzUdmZmQg5hpo2Lg4ccVuH/hh_instagram_friday_workout_31e45f63.png",
    "Saturday":  "https://d2xsxph8kpxj0f.cloudfront.net/310519663375052884/KzUdmZmQg5hpo2Lg4ccVuH/hh_instagram_quote_card_9d49358d.png",
    "Sunday":    "https://d2xsxph8kpxj0f.cloudfront.net/310519663375052884/KzUdmZmQg5hpo2Lg4ccVuH/hh_instagram_quote_card_9d49358d.png",
}

# ── GHL User ID (from existing posts' createdBy field) ───────────────────────
GHL_USER_ID = os.environ.get("GHL_USER_ID", "LnjbrtBaqeOZDhGaILxA")

# ── GHL Social Account IDs ────────────────────────────────────────────────────
GHL_ACCOUNTS = {
    "facebook":   "6840dc7c53848e6d83bc6d0c_jQOzG0xh0TF0mw1tyh8t_654078311297817_page",
    "instagram":  "6840dcc55b573ff7c0a9d7d5_jQOzG0xh0TF0mw1tyh8t_17841400917824124",
    "linkedin":   "6840dcf25b573f565da9d7d6_jQOzG0xh0TF0mw1tyh8t_rP1hWbFZ0t_profile",
    "tiktok":     "6840ddc93af45bd31e027866_jQOzG0xh0TF0mw1tyh8t_000VmUcZ7kPpnhwDbTqhtxgQtkePnn238_profile",
    "tiktok2":    "6840dd03ef9a6027f37d8e07_jQOzG0xh0TF0mw1tyh8t_000bNyEnprq9Bxmn9boN8g1zGQTeDhiK0B_profile",
    "youtube":    "6840dd3590b35ec4af3296d4_jQOzG0xh0TF0mw1tyh8t_UCdQwQTVEAYBwbrf6mRZjcPQ_profile",
    "pinterest":  "69a2e0a4450aed0493ac4a2c_jQOzG0xh0TF0mw1tyh8t_982629349855657418_profile",
}

# ── Weekly Content Pillars ────────────────────────────────────────────────────
WEEKLY_PILLARS = {
    "Monday":    "GLP-1 Education — what GLP-1 does in the body, blood sugar, metabolism, brain signaling",
    "Tuesday":   "What I Eat in a Day — hormone-support nutrition, protein, fiber, blood sugar balance",
    "Wednesday": "Client or Personal Wins — behavior change, habit shifts, symptom improvements, transformation stories",
    "Thursday":  "Perimenopause Education — brain fog, hot flashes, anxiety, sleep, joint pain, mood swings",
    "Friday":    "Hormone Friendly Workouts — walking, strength training, cortisol balance, recovery",
    "Saturday":  "Lifestyle and Routines — morning routines, grocery shopping, supplements, tea routines",
    "Sunday":    "Mindset and Reflection — encouragement, midlife reinvention, faith-based stewardship, weekly reset",
}

# ── Brand Context ─────────────────────────────────────────────────────────────
BRAND_CONTEXT = """You are the content agent for Phyllis H. Thompson, known as The Hormone Hacking Coach.

ABOUT PHYLLIS:
Certified Integrative Nutritionist, Certified Personal Trainer, and Double Certified Menopause Specialist.
She helps women in perimenopause and menopause support their hormones naturally to reduce symptoms, improve metabolism, stabilize energy, reduce cravings, and lose hormonal weight.
Her approach focuses on science-backed lifestyle inputs that support natural GLP-1 production and metabolic signaling.

BRAND VOICE:
Empowering, educational, conversational, slightly humorous, story-driven, authoritative but compassionate.
Never shame women. Always validate their experience. Empower them with solutions.
Use phrases like: "You are not broken." "Your hormones are shifting." "There are things you can do to support your body."
NEVER use em dashes. Write in a warm, direct, conversational tone.

AUDIENCE:
Women 35-55 dealing with perimenopause and menopause symptoms: fatigue, weight gain, brain fog, hot flashes, mood swings, anxiety, sleep disruption, joint pain, digestion changes.

PRODUCTS AND FUNNEL:
Free content -> Natural GLP-1 Midlife Reset Guide -> Hormone Hacker Membership ($97/month) -> Coaching/programs
Primary CTA: Comment RESET to receive the Natural GLP-1 Midlife Reset Guide
Secondary CTAs: Save this post, Share with a friend, DM me RESET

HIGH PERFORMING CONTENT TYPES:
"Things nobody told me about perimenopause", myth-busting posts, symptom explanation posts, lifestyle intervention posts, hormone science simplified, client transformation stories.

HOOKS THAT PERFORM WELL:
"Most women are never told this about perimenopause"
"If you are over 40 and struggling with energy, read this"
"The real reason midlife weight loss feels harder"
"Things nobody told me about menopause"
"Your body is not broken, your hormones changed"
"Why hot flashes get worse for some women"

STORY STRATEGY:
Daily stories open with: "Good morning ladies, your Hormone Hacking Coach clocking in. The hormone reset store is open today."
Goal: generate DM conversations.

Format all output as clean plain text (no HTML, no markdown) unless specifically asked for HTML."""

# ── OpenAI Helper ─────────────────────────────────────────────────────────────
def ask_openai(prompt, max_tokens=2000, system=None):
    resp = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": system or BRAND_CONTEXT},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": 0.75
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

# ── Video Generation Helper ──────────────────────────────────────────────────
def generate_reel_video(image_url, caption_text, day_of_week):
    """
    Downloads the branded image, converts it to a 9:16 reel video (15 seconds),
    uploads to CDN, and returns the CDN video URL.
    """
    try:
        from moviepy.editor import ImageClip, TextClip, CompositeVideoClip
        from PIL import Image, ImageDraw, ImageFont
        import tempfile, os, textwrap

        # Download the branded image
        resp = requests.get(image_url, timeout=30)
        resp.raise_for_status()
        tmp_img = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        tmp_img.write(resp.content)
        tmp_img.close()

        # Resize to 9:16 (1080x1920) for reels
        img = Image.open(tmp_img.name).convert('RGB')
        target_w, target_h = 1080, 1920
        w, h = img.size
        scale = target_w / w
        new_h = int(h * scale)
        img = img.resize((target_w, new_h), Image.LANCZOS)
        if new_h < target_h:
            padded = Image.new('RGB', (target_w, target_h), (20, 15, 10))
            padded.paste(img, (0, (target_h - new_h) // 2))
            img = padded
        elif new_h > target_h:
            top = (new_h - target_h) // 2
            img = img.crop((0, top, target_w, top + target_h))

        # Add a subtle caption overlay at the bottom
        draw = ImageDraw.Draw(img)
        # Dark overlay bar at bottom
        overlay = Image.new('RGBA', (target_w, 220), (0, 0, 0, 160))
        img_rgba = img.convert('RGBA')
        img_rgba.paste(overlay, (0, target_h - 220), overlay)
        img = img_rgba.convert('RGB')

        # Save the processed image
        tmp_reel_img = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        img.save(tmp_reel_img.name)
        tmp_reel_img.close()

        # Create 15-second video from image
        clip = ImageClip(tmp_reel_img.name, duration=15)
        clip = clip.set_fps(30)

        tmp_video = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
        tmp_video.close()
        clip.write_videofile(
            tmp_video.name,
            codec='libx264',
            audio=False,
            verbose=False,
            logger=None,
            ffmpeg_params=['-crf', '28', '-preset', 'fast']
        )

        # Upload to catbox.moe (free, permanent public CDN, no auth required)
        cdn_url = None
        with open(tmp_video.name, 'rb') as vf:
            upload_resp = requests.post(
                'https://catbox.moe/user/api.php',
                data={'reqtype': 'fileupload', 'userhash': ''},
                files={'fileToUpload': ('reel.mp4', vf, 'video/mp4')},
                timeout=120
            )
        if upload_resp.status_code == 200 and upload_resp.text.strip().startswith('https://'):
            cdn_url = upload_resp.text.strip()

        # Cleanup
        os.unlink(tmp_img.name)
        os.unlink(tmp_reel_img.name)
        os.unlink(tmp_video.name)

        if cdn_url:
            print(f'  Reel video uploaded: {cdn_url}')
            return cdn_url
        else:
            print(f'  Reel video upload failed: {upload_resp.text[:200]}')
            return None
    except Exception as e:
        print(f'  Reel video generation error: {e}')
        return None


# ── GHL Social Planner Helper ─────────────────────────────────────────────────
def ghl_post(text, platforms, scheduled_at_iso=None, image_url=None, video_url=None, post_type='post'):
    """
    Post to GHL Social Planner.
    platforms: list of platform keys from GHL_ACCOUNTS e.g. ["facebook", "instagram"]
    scheduled_at_iso: ISO 8601 string e.g. "2026-03-13T14:00:00.000Z" — if None, posts immediately
    image_url: CDN URL of image to attach (required for Instagram)
    """
    account_ids = [GHL_ACCOUNTS[p] for p in platforms if p in GHL_ACCOUNTS]
    if not account_ids:
        print("  GHL post skipped: no valid account IDs")
        return None

    # Build media array — Instagram requires image, TikTok/YouTube require video
    media = []
    if video_url:
        media = [{"url": video_url, "type": "video/mp4"}]
    elif image_url:
        media = [{"url": image_url, "type": "image/png"}]

    body = {
        "accountIds": account_ids,
        "summary": text,
        "status": "scheduled" if scheduled_at_iso else "published",
        "type": post_type,
        "media": media,
        "userId": GHL_USER_ID,
    }
    if scheduled_at_iso:
        body["scheduleDate"] = scheduled_at_iso

    resp = requests.post(
        f"https://services.leadconnectorhq.com/social-media-posting/{GHL_LOCATION_ID}/posts",
        headers={
            "Authorization": f"Bearer {GHL_API_KEY}",
            "Version": "2021-07-28",
            "Content-Type": "application/json"
        },
        json=body
    )
    if resp.status_code in (200, 201):
        result = resp.json()
        post_id = result.get("post", {}).get("id", "unknown")
        print(f"  GHL post created: {platforms} | scheduled: {scheduled_at_iso or 'now'} | ID: {post_id}")
        return result
    else:
        print(f"  GHL post FAILED: {resp.status_code} -> {resp.text[:300]}")
        return None

def schedule_today_posts(posts_by_platform, image_url=None, video_url=None):
    """
    Schedule 3 posts today at 10am, 1pm, 7pm ET (14:00, 17:00, 23:00 UTC).
    posts_by_platform: dict with keys like "facebook", "instagram"
    Each value is a list of 3 post texts.
    image_url: CDN URL for Instagram image (required for Instagram posts)
    """
    # ET = UTC-4 (EDT) or UTC-5 (EST) — use UTC-4 for March-November
    now_utc = datetime.now(timezone.utc)
    today = now_utc.date()

    # Post times in UTC (ET + 4 hours for EDT)
    post_times_utc = [
        datetime(today.year, today.month, today.day, 14, 0, 0, tzinfo=timezone.utc),   # 10am ET
        datetime(today.year, today.month, today.day, 17, 0, 0, tzinfo=timezone.utc),   # 1pm ET
        datetime(today.year, today.month, today.day, 23, 0, 0, tzinfo=timezone.utc),   # 7pm ET
    ]

    # Build the actual schedule: use today's future slots, then overflow to tomorrow
    from datetime import timedelta as td
    tomorrow = today + td(days=1)
    tomorrow_slots = [
        datetime(tomorrow.year, tomorrow.month, tomorrow.day, 14, 0, 0, tzinfo=timezone.utc),
        datetime(tomorrow.year, tomorrow.month, tomorrow.day, 17, 0, 0, tzinfo=timezone.utc),
        datetime(tomorrow.year, tomorrow.month, tomorrow.day, 23, 0, 0, tzinfo=timezone.utc),
    ]
    # Build ordered list of all available slots (today future + tomorrow)
    all_slots = [t for t in post_times_utc if t > now_utc + td(minutes=5)] + tomorrow_slots
    # Ensure we always have at least 3 slots
    while len(all_slots) < 3:
        all_slots.append(all_slots[-1] + td(hours=3))

    results = []
    for platform, post_texts in posts_by_platform.items():
        for i, text in enumerate(post_texts[:3]):
            # Use the i-th available future slot
            slot = all_slots[i] if i < len(all_slots) else all_slots[-1]
            scheduled_at = slot.strftime("%Y-%m-%dT%H:%M:%S.000Z")
            # Determine media type per platform
            vid = video_url if platform in ("tiktok", "tiktok2", "youtube") else None
            img = image_url if platform in ("instagram", "pinterest") else None
            ptype = "reel" if vid else "post"
            result = ghl_post(text, [platform], scheduled_at, image_url=img, video_url=vid, post_type=ptype)
            results.append(result)
    return results

# ── Agent 1: Daily Auto-Post Agent ───────────────────────────────────────────
def run_daily_post_agent():
    """
    Core autonomous posting agent.
    Generates 3 posts per platform (Facebook + Instagram) based on today's weekly pillar.
    Posts are scheduled to GHL Social Planner at 10am, 1pm, 7pm ET.
    Also emails Phyllis a summary of what was posted.
    """
    print("Running Daily Auto-Post Agent...")
    today = datetime.now().strftime("%B %d, %Y")
    day_of_week = datetime.now().strftime("%A")
    pillar = WEEKLY_PILLARS.get(day_of_week, "Hormone health tips for women in midlife")

    prompt = f"""Today is {day_of_week}, {today}.
Today's content pillar: {pillar}

Generate exactly 3 social media posts for today. Each post must follow the daily structure:
- POST 1: Education or authority content
- POST 2: Relatable or lifestyle content
- POST 3: Actionable tip or conversation starter

CAROUSEL STRUCTURE (when applicable):
Slide 1: Strong hook
Slides 2-6: Education or insight
Slide 7: Authority positioning
Slide 8: Soft CTA

REQUIREMENTS FOR EACH POST:
- Strong scroll-stopping hook (first line)
- Body: 60-90 words, warm and conversational
- End with CTA: "Comment RESET for the Natural GLP-1 Midlife Reset Guide" or "Save this post" or "Share with a friend who needs this"
- 3-5 relevant hashtags (Instagram and TikTok limit — keep it tight and targeted)
- No em dashes
- No salesy language — educational and relatable first

FORMAT YOUR RESPONSE EXACTLY LIKE THIS (use these exact labels):

POST 1 CAPTION:
[full caption text with hashtags]

POST 2 CAPTION:
[full caption text with hashtags]

POST 3 CAPTION:
[full caption text with hashtags]

STORY SCRIPT:
[1-2 sentence story opener Phyllis can record today]"""

    content = ask_openai(prompt, max_tokens=2500)

    # Parse the 3 posts from the response
    posts = []
    story = ""
    lines = content.split("\n")
    current_post = []
    current_label = None

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("POST 1 CAPTION:"):
            current_label = "post"
            current_post = []
        elif stripped.startswith("POST 2 CAPTION:"):
            if current_post:
                posts.append("\n".join(current_post).strip())
            current_label = "post"
            current_post = []
        elif stripped.startswith("POST 3 CAPTION:"):
            if current_post:
                posts.append("\n".join(current_post).strip())
            current_label = "post"
            current_post = []
        elif stripped.startswith("STORY SCRIPT:"):
            if current_post:
                posts.append("\n".join(current_post).strip())
            current_label = "story"
            current_post = []
        elif current_label == "post":
            current_post.append(line)
        elif current_label == "story":
            story += line + "\n"

    if current_post:
        if current_label == "post":
            posts.append("\n".join(current_post).strip())

    # Fallback: if parsing failed, split by double newline
    if len(posts) < 3:
        print("  Warning: post parsing fallback triggered")
        chunks = [c.strip() for c in content.split("\n\n") if len(c.strip()) > 50]
        posts = chunks[:3]
        while len(posts) < 3:
            posts.append(posts[-1] if posts else content[:500])

    print(f"  Generated {len(posts)} posts for {day_of_week} ({pillar[:40]}...)")

    # Get the branded image for today's Instagram posts
    instagram_image = INSTAGRAM_IMAGES.get(day_of_week, INSTAGRAM_IMAGES["Sunday"])

    # Generate reel video from today's branded image
    print("  Generating reel video from branded image...")
    reel_video_url = generate_reel_video(instagram_image, posts[0] if posts else "", day_of_week)

    # Schedule to GHL Social Planner: all platforms
    # Facebook + Instagram + LinkedIn: image posts
    # TikTok + TikTok2 + YouTube: video reels
    # Pinterest: image post
    posted_results = schedule_today_posts(
        {
            "facebook":  posts,
            "instagram": posts,
            "linkedin":  posts,
            "pinterest": posts,
        },
        image_url=instagram_image
    )

    # Post reel video to TikTok and YouTube if video was generated
    if reel_video_url:
        reel_results = schedule_today_posts(
            {
                "tiktok":  posts,
                "tiktok2": posts,
                "youtube": posts,
            },
            video_url=reel_video_url
        )
        posted_results.extend(reel_results)
    else:
        print("  Skipping TikTok/YouTube — video generation failed")

    # Count successful posts
    successful = sum(1 for r in posted_results if r is not None)
    print(f"  GHL: {successful}/{len(posted_results)} posts scheduled successfully")

    # Build email summary
    posts_html = ""
    for i, post in enumerate(posts, 1):
        post_html = post.replace("\n", "<br>")
        posts_html += f"""
        <div style='background:#f9f5ff;border-left:4px solid #b85c38;padding:16px;margin-bottom:16px;border-radius:8px;'>
            <div style='font-weight:700;color:#b85c38;margin-bottom:8px;font-size:13px;text-transform:uppercase;letter-spacing:0.05em;'>Post {i}</div>
            <p style='color:#2d2d2d;font-size:14px;line-height:1.6;margin:0;'>{post_html}</p>
        </div>"""

    story_html = f"<div style='background:#eef5ef;border-left:4px solid #7a9e7e;padding:16px;border-radius:8px;'><div style='font-weight:700;color:#3a6e3e;margin-bottom:8px;font-size:13px;text-transform:uppercase;'>Story Script</div><p style='color:#2d2d2d;font-size:14px;line-height:1.6;margin:0;'>{story.replace(chr(10), '<br>')}</p></div>" if story.strip() else ""

    send_email(
        subject=f"Hormone Hacker Auto-Post Summary — {day_of_week}, {today}",
        html_body=f"""
        <div style='font-family:Georgia,serif;max-width:600px;margin:0 auto;'>
            <h2 style='color:#b85c38;'>Daily Auto-Post Summary</h2>
            <p style='color:#666;font-size:13px;'>Generated and scheduled {today} | {day_of_week} Pillar: <strong>{pillar}</strong></p>
            <p style='color:#3a6e3e;font-size:13px;font-weight:600;'>Scheduled to: Facebook, Instagram, LinkedIn, Pinterest (image) + TikTok, YouTube (reel video) | Times: 10am, 1pm, 7pm ET</p>
            <hr style='border:none;border-top:1px solid #e8d8cc;margin:16px 0;'>
            {posts_html}
            {story_html}
            <p style='color:#999;font-size:12px;margin-top:24px;'>Posts are live in your GHL Social Planner. Review at app.gohighlevel.com > Marketing > Social Planner.</p>
        </div>"""
    )
    print("  Daily Auto-Post Agent complete.")

# ── Agent 2: Weekly Reel Ideas Email ─────────────────────────────────────────
def run_reel_ideas_agent():
    """
    Runs every Monday. Generates 5 reel ideas for the week based on trending content
    in the perimenopause/hormone health niche. Emails Phyllis so she can batch record.
    """
    print("Running Weekly Reel Ideas Agent...")
    today = datetime.now().strftime("%B %d, %Y")

    prompt = f"""Today is Monday, {today}. Generate the weekly reel ideas brief for Phyllis Thompson, The Hormone Hacking Coach.

Phyllis records 2-3 reels per week and batches them. She needs ideas that are:
- Trending in the perimenopause, menopause, and hormone health niche RIGHT NOW
- Likely to perform well on TikTok and Instagram Reels
- Easy to record in one take (no props needed, just talking to camera)
- 30-90 seconds long

Generate exactly 5 reel ideas. For each idea provide:

REEL [NUMBER]:
TITLE: [catchy title for the reel]
FORMAT: [choose: Talking Head, Hook Test, Myth Bust, Story Time, Quick Tip, Day in My Life]
HOOK (first 3 seconds): [exact words to say — must stop the scroll]
SCRIPT OUTLINE: [3-5 bullet points of what to cover, 60-90 seconds total]
ON-SCREEN TEXT: [3 text overlays to add in editing]
TRENDING ANGLE: [why this topic is trending right now in the niche]
VIRAL POTENTIAL: [High/Medium] and one sentence why
CTA: [what to say at the end]
HASHTAGS: [10 hashtags]

Also include at the end:
BATCH RECORDING ORDER: Which 3 to record first this week and why
BEST DAY TO POST: Recommended posting day for each reel

Focus on topics like: GLP-1 and natural weight loss, perimenopause symptoms nobody talks about, hormone-disrupting foods, cortisol and belly fat, strength training for women 40+, sleep and hormones, things doctors do not tell you about menopause."""

    content = ask_openai(prompt, max_tokens=3000)

    send_email(
        subject=f"Hormone Hacker Weekly Reel Ideas — Week of {today}",
        html_body=f"""
        <div style='font-family:Georgia,serif;max-width:600px;margin:0 auto;'>
            <h2 style='color:#1a1a1a;background:#f0f0f0;padding:16px;border-radius:8px;'>
                Weekly Reel Ideas Brief
            </h2>
            <p style='color:#666;font-size:13px;'>Week of {today} | Batch record 2-3 of these this week</p>
            <hr style='border:none;border-top:1px solid #e8d8cc;margin:16px 0;'>
            <div style='white-space:pre-wrap;font-size:14px;line-height:1.7;color:#2d2d2d;'>{content}</div>
            <div style='background:#fdf0eb;border-radius:8px;padding:16px;margin-top:24px;'>
                <p style='color:#b85c38;font-weight:700;margin:0 0 8px;'>Recording Tips</p>
                <p style='color:#5a4a40;font-size:13px;margin:0;'>Record in natural light. No need for a ring light. Authentic is better than polished. Use the hook as your first words — no intro, no "hey guys". Post within 24 hours of recording for best reach.</p>
            </div>
        </div>"""
    )
    print("  Reel Ideas Agent complete.")

# ── Agent 3: Content Agent (Weekly Package) ───────────────────────────────────
def run_content_agent():
    print("Running Content Agent — Weekly Content Package...")
    today = datetime.now().strftime("%B %d, %Y")
    day_of_week = datetime.now().strftime("%A")

    prompt = f"""Today is {day_of_week}, {today}. Generate a full weekly content package for Hormone Hacker.

WEEKLY CONTENT PILLARS:
Monday: GLP-1 Education
Tuesday: What I Eat in a Day
Wednesday: Client or Personal Wins
Thursday: Perimenopause Education
Friday: Hormone Friendly Workouts
Saturday: Lifestyle and Routines
Sunday: Mindset and Reflection

Create the following:

1. BLOG POST DRAFT
   - SEO-optimized title (60 chars max)
   - Meta description (155 chars max)
   - Full post (700-900 words)
   - Target keywords (5)
   - Topic: choose the most timely hormone health topic for women 35-55

2. EMAIL NEWSLETTER DRAFT
   - Subject line (A/B test: 2 options)
   - Preview text (90 chars)
   - Full email body (300-400 words)
   - CTA: Comment RESET or link to GLP-1 Reset Guide

3. LINKEDIN ARTICLE DRAFT
   - Professional title targeting HR Directors and corporate wellness buyers
   - Full article (500-700 words)
   - 5 LinkedIn hashtags

4. WEEKLY STORY SCRIPTS (5 stories, one per day Mon-Fri)
   - Each: 2-3 sentences, opens with "Good morning ladies, your Hormone Hacking Coach clocking in"
   - Include a question or poll idea to generate DM conversations

Format as clean HTML with section headers in #b85c38. Never use em dashes."""

    content = ask_openai(prompt, max_tokens=3500)
    send_email(
        subject=f"Hormone Hacker Weekly Content Package — {today}",
        html_body=f"<div style='font-family:Georgia,serif;max-width:600px;margin:0 auto;'><h2 style='color:#b85c38;'>Weekly Content Package</h2><p style='color:#666;font-size:13px;'>Generated {today} by Railway Content Agent</p><hr style='border:none;border-top:1px solid #e8d8cc;'>{content}</div>"
    )
    print("  Content Agent complete.")

# ── Agent 4: Email Nurture Sequence ──────────────────────────────────────────
def run_email_nurture_agent():
    print("Running Email Agent — Nurture Sequence...")
    today = datetime.now().strftime("%B %d, %Y")
    prompt = f"""Today is {today}. Write a 5-email nurture sequence for Hormone Hacker.

Audience: women who downloaded the Natural GLP-1 Midlife Reset Guide but have not joined the membership.

Sequence arc:
- Email 1: Welcome + deliver the guide, set expectations
- Email 2: Biggest hormone myth busted (educational value)
- Email 3: Success story / transformation (social proof)
- Email 4: What is inside the Hormone Hacker Membership (soft sell)
- Email 5: Last chance / urgency (direct offer, $97/month)

For each email: subject line (2 A/B options), preview text, full body (250-350 words), CTA.
Brand voice: warm, empowering, like a knowledgeable best friend. Never use em dashes.
Format as clean HTML with #b85c38 headers."""

    content = ask_openai(prompt, max_tokens=3000)
    send_email(
        subject=f"Hormone Hacker Email Agent — Nurture Sequence ({today})",
        html_body=f"<div style='font-family:Georgia,serif;max-width:600px;margin:0 auto;'><h2 style='color:#b85c38;'>Nurture Email Sequence</h2><p style='color:#666;font-size:13px;'>Generated {today}</p><hr style='border:none;border-top:1px solid #e8d8cc;'>{content}</div>"
    )
    print("  Email Nurture Agent complete.")

# ── Agent 5: Workshop Email Sequence ─────────────────────────────────────────
def run_email_workshop_agent():
    print("Running Email Agent — Workshop Welcome Sequence...")
    today = datetime.now().strftime("%B %d, %Y")
    prompt = f"""Today is {today}. Write a 3-email workshop welcome sequence for Hormone Hacker.

Audience: women who registered for a free Hormone Hacker workshop.

Email 1 (send immediately): Confirm their spot, build excitement, introduce Phyllis briefly.
Email 2 (send 1 day before): Reminder, 1 quick action to do before the workshop, teaser of the most valuable insight.
Email 3 (send 1 hour after workshop): Thank them, recap 3 biggest takeaways, offer the Hormone Hacker Membership ($97/month) as the next step.

For each email: subject line (2 A/B options), preview text, full body, CTA.
Format as clean HTML with #b85c38 headers. Never use em dashes."""

    content = ask_openai(prompt, max_tokens=2500)
    send_email(
        subject=f"Hormone Hacker Email Agent — Workshop Sequence ({today})",
        html_body=f"<div style='font-family:Georgia,serif;max-width:600px;margin:0 auto;'><h2 style='color:#b85c38;'>Workshop Email Sequence</h2><p style='color:#666;font-size:13px;'>Generated {today}</p><hr style='border:none;border-top:1px solid #e8d8cc;'>{content}</div>"
    )
    print("  Email Workshop Agent complete.")

# ── Agent 6: LinkedIn B2B Agent ───────────────────────────────────────────────
def run_linkedin_agent():
    print("Running LinkedIn B2B Newsletter Agent...")
    today = datetime.now().strftime("%B %d, %Y")
    prompt = f"""Today is {today}. Write a LinkedIn newsletter article for Phyllis Thompson targeting HR Directors, Chief People Officers, and corporate wellness decision-makers.

Article topic: Choose the most compelling and timely topic about perimenopause, menopause, or hormonal health in the workplace for women 35-55.

Requirements:
- LinkedIn article title (compelling, professional, 60-80 chars)
- Opening hook (2-3 sentences that stop the scroll)
- Full article body (600-800 words)
- Structure: Problem -> Data/Research -> Business Impact -> Solution -> Call to Action
- Include 2-3 statistics about menopause in the workplace
- Position Phyllis Thompson as the expert companies should hire for corporate wellness programs
- End with soft CTA: invite HR Directors to book a discovery call
- 5 LinkedIn hashtags

Also write:
- A LinkedIn post to promote the article (150 words, hook + summary + link placeholder)
- A LinkedIn comment reply template (50 words) for when people engage

Format as clean HTML with #1E3A5F headers. Never use em dashes."""

    content = ask_openai(prompt, max_tokens=2500)
    send_email(
        subject=f"Hormone Hacker LinkedIn Agent — Corporate Wellness Article ({today})",
        html_body=f"<div style='font-family:Georgia,serif;max-width:600px;margin:0 auto;'><h2 style='color:#1E3A5F;'>LinkedIn B2B Newsletter</h2><p style='color:#666;font-size:13px;'>Generated {today}</p><hr style='border:none;border-top:1px solid #e8d8cc;'>{content}</div>"
    )
    print("  LinkedIn Agent complete.")

# ── Agent 7: App Agent ────────────────────────────────────────────────────────
def run_app_agent():
    print("Running App Agent — Weekly Improvement Brief...")
    today = datetime.now().strftime("%B %d, %Y")
    prompt = f"""Today is {today}. Generate a weekly improvement brief for the Hormone Hacker App and member dashboard.

The Hormone Hacker App is a membership platform ($97/month) with: 4-week hormone reset roadmap, hormone-balancing recipes, workout plans, FSA/HSA eligible, Thursday 7PM Instagram Lives with Phyllis, GLP-1 Reset Guide, one-on-one coaching booking.

Generate:
1. WEEKLY APP IMPROVEMENT IDEAS (5 ideas) — feature or content improvement, why it increases retention, effort (Low/Medium/High), priority score (1-10)
2. MEMBER ENGAGEMENT EMAIL (ready to send) — subject line, 200-word email to current members
3. MEMBER SUPPORT RESPONSE TEMPLATES (5 templates) — common questions with warm responses
4. WEEKLY MEMBER WIN SPOTLIGHT — template for featuring a member success story

Format as clean HTML with #b85c38 headers. Never use em dashes."""

    content = ask_openai(prompt, max_tokens=2500)
    send_email(
        subject=f"Hormone Hacker App Agent — Weekly Brief ({today})",
        html_body=f"<div style='font-family:Georgia,serif;max-width:600px;margin:0 auto;'><h2 style='color:#b85c38;'>App Agent Weekly Brief</h2><p style='color:#666;font-size:13px;'>Generated {today}</p><hr style='border:none;border-top:1px solid #e8d8cc;'>{content}</div>"
    )
    print("  App Agent complete.")

# ── Agent 8: Daily Task Dispatcher ───────────────────────────────────────────
def run_task_dispatcher():
    print("Running Daily Task Dispatcher...")
    today = datetime.now().strftime("%B %d, %Y")
    day_of_week = datetime.now().strftime("%A")
    pillar = WEEKLY_PILLARS.get(day_of_week, "Hormone health")

    prompt = f"""Today is {day_of_week}, {today}. Today's content pillar: {pillar}.

Generate a daily action brief for Phyllis Thompson at Hormone Hacker.

Include:

1. TODAY'S PRIORITY TASKS (3-5 tasks)
   - Specific, actionable tasks for today
   - Tailored to {day_of_week} (e.g., Monday = LinkedIn article + GLP-1 content, Thursday = Instagram Live prep)
   - Each task: what to do, why it matters today, time estimate

2. CONTENT POSTED TODAY (auto-scheduled to GHL)
   - Confirm 3 posts were scheduled to Facebook and Instagram at 10am, 1pm, 7pm ET
   - Today's pillar: {pillar}

3. DAILY AFFIRMATION / BRAND MESSAGE
   - One powerful sentence Phyllis can share as a story or quote post

4. QUICK WINS (2-3 items)
   - Small actions under 5 minutes: reply to top comment, share a member win, update a story

5. THIS WEEK'S FOCUS REMINDER
   - One sentence reminding Phyllis of the week's main content theme

Format as clean HTML with a warm, motivating tone. Use #b85c38 headers. Never use em dashes."""

    content = ask_openai(prompt, max_tokens=2000)
    send_email(
        subject=f"Hormone Hacker Daily Brief — {day_of_week}, {today}",
        html_body=f"<div style='font-family:Georgia,serif;max-width:600px;margin:0 auto;'><h2 style='color:#b85c38;'>Good morning, Phyllis! Here is your Daily Brief.</h2><p style='color:#666;font-size:13px;'>Generated {today} | Today's pillar: <strong>{pillar}</strong></p><hr style='border:none;border-top:1px solid #e8d8cc;'>{content}</div>"
    )
    print("  Task Dispatcher complete.")

# ── Agent 9: Trial Reel Brief ─────────────────────────────────────────────────
def run_trial_reel_agent():
    print("Running Trial Reel Agent...")
    today = datetime.now().strftime("%B %d, %Y")
    day_of_week = datetime.now().strftime("%A")
    pillar = WEEKLY_PILLARS.get(day_of_week, "Hormone health")

    prompt = f"""Today is {day_of_week}, {today}. Today's pillar: {pillar}.
Generate a TikTok Trial Reel brief for Hormone Hacker.

1. TODAY'S REEL BRIEF
   - Format: choose one of (Trend Remix, Raw Thought/Lesson, Hook Test)
   - Hook (first 3 seconds)
   - Full script (150-200 words, conversational)
   - On-screen text suggestions (3-5 overlays)
   - Trending audio suggestion (describe the vibe)
   - Hashtags (10-15)
   - Why this reel has viral potential

2. HOOK VARIATIONS (3 alternative hooks)
   - Curiosity Hook, Pain Point Hook, Controversy Hook

3. ENGAGEMENT PROMPT
   - Question for the caption to drive comments
   - Reply template for the first 10 comments

Format as clean HTML with dark headers (#1a1a1a). Never use em dashes."""

    content = ask_openai(prompt, max_tokens=2000)
    send_email(
        subject=f"Hormone Hacker Trial Reel Brief — {day_of_week}, {today}",
        html_body=f"<div style='font-family:Georgia,serif;max-width:600px;margin:0 auto;'><h2 style='color:#1a1a1a;'>TikTok Trial Reel Brief</h2><p style='color:#666;font-size:13px;'>Generated {today} | Pillar: {pillar}</p><hr style='border:none;border-top:1px solid #e8d8cc;'>{content}</div>"
    )
    print("  Trial Reel Agent complete.")

# ── Main Runner ───────────────────────────────────────────────────────────────
AGENTS = {
    "daily_post":      run_daily_post_agent,
    "reel_ideas":      run_reel_ideas_agent,
    "content":         run_content_agent,
    "email_nurture":   run_email_nurture_agent,
    "email_workshop":  run_email_workshop_agent,
    "linkedin":        run_linkedin_agent,
    "app":             run_app_agent,
    "dispatcher":      run_task_dispatcher,
    "trial_reel":      run_trial_reel_agent,
}

def main():
    args = sys.argv[1:]
    today = datetime.now().strftime("%A")

    if not args or args[0] == "all":
        print(f"\n=== Hormone Hacker Agents — Running ALL ({datetime.now().strftime('%Y-%m-%d %H:%M')}) ===\n")
        for name, fn in AGENTS.items():
            try:
                fn()
            except Exception as e:
                print(f"  ERROR in {name}: {e}")

    elif args[0] == "daily":
        # Daily run: auto-post + dispatcher + trial reel every weekday
        # Monday also gets reel_ideas + linkedin + content
        print(f"\n=== Hormone Hacker Agents — Daily Run ({today}) ===\n")
        daily_agents = ["daily_post", "dispatcher", "trial_reel"]
        if today == "Monday":
            daily_agents += ["reel_ideas", "linkedin", "content"]
        if today in ["Tuesday", "Wednesday"]:
            daily_agents += ["email_nurture"]
        for name in daily_agents:
            try:
                AGENTS[name]()
            except Exception as e:
                print(f"  ERROR in {name}: {e}")

    elif args[0] == "weekly":
        print(f"\n=== Hormone Hacker Agents — Weekly Run ===\n")
        for name in ["content", "email_nurture", "email_workshop", "app"]:
            try:
                AGENTS[name]()
            except Exception as e:
                print(f"  ERROR in {name}: {e}")

    elif args[0] in AGENTS:
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
