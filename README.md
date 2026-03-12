# Hormone Hacker Content Agents

Autonomous content agents for Phyllis Thompson / Hormone Hacker. Runs on Railway via cron scheduling — no Make.com required.

## Agents

| Agent | Command | Schedule |
|-------|---------|----------|
| Daily Task Dispatcher | `python3 agents.py dispatcher` | Mon-Fri 8am ET |
| Trial Reel Brief | `python3 agents.py trial_reel` | Mon-Fri 8am ET |
| Content Agent (Blog, Social, TikTok) | `python3 agents.py content` | Every Monday 9am ET |
| Email Nurture Sequence | `python3 agents.py email_nurture` | Every Monday 9am ET |
| Workshop Email Sequence | `python3 agents.py email_workshop` | Every Monday 9am ET |
| App Improvement Brief | `python3 agents.py app` | Every Monday 9am ET |
| LinkedIn B2B Newsletter | `python3 agents.py linkedin` | Every Monday 9am ET |

## Schedules

- **Daily (Mon-Fri 8am ET):** `python3 agents.py daily` — runs dispatcher + trial reel. On Mondays also runs linkedin + content.
- **Weekly (Mon 9am ET):** `python3 agents.py weekly` — runs content, email_nurture, email_workshop, app

## Output

All agents email results to: `info@phyllishannahthompson.com`
Sent from: `hormones@support.phyllishannahthompson.com` via Resend

## Environment Variables

Set these in Railway dashboard under Variables:

```
OPENAI_API_KEY=sk-proj-...
RESEND_API_KEY=re_...
```

## Running Locally

```bash
pip install -r requirements.txt
python3 agents.py daily
python3 agents.py content
python3 agents.py all
```

## Railway Deployment

This project uses Railway cron jobs (requires paid plan). Two cron schedules are configured in `railway.toml`:
- Daily: `0 13 * * 1-5` (Mon-Fri 8am ET)
- Weekly: `0 14 * * 1` (Monday 9am ET)

*Built by Manus AI — March 2026*
