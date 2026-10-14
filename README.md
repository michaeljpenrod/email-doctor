# Email Doctor

Check a cold email for spam-filter triggers and reply-rate problems, see why each phrase is flagged and where that comes from, and rewrite it into a short, research-backed version.

This is the same engine as the free web tool at **[velocitylab.ai/emaildoctor](https://velocitylab.ai/emaildoctor/)**, packaged as a Claude skill and a ChatGPT plugin.

## What it does

1. **Scores the email from 0 to 100** against 405 phrases in 10 categories. Every phrase cites a SpamAssassin rule, a mailbox provider guideline, or a published study.
2. **Lists every issue in two groups:** SPAM filter issues (phishing lures, deceptive framing, money claims, urgency, hidden characters, shortened links) and reply rate issues (clichés, hype, AI-sounding vocabulary, unfilled placeholders).
3. **Rewrites the email** using data on what gets replies: a 1 to 4 word subject, 50 to 100 words, problem-first, one low-pressure ask, and no invented facts.
4. **Re-checks the rewrite** and shows the score change.

It's honest about scope. Wording matters less than most spam-word lists imply, because Gmail and Outlook decide mostly on sender reputation, authentication, and volume. `research.md` covers both.

## Use it in Claude

**Claude.ai:** download [`email-doctor-skill.zip`](email-doctor-skill.zip), then open **Settings → Capabilities → Skills** and upload it. Code execution must be on, so the checker can run.

**Claude Code:** copy the [`claude/email-doctor`](claude/email-doctor) folder into `~/.claude/skills/`.

Then paste any cold email and ask Claude to check or fix it.

## Use it in ChatGPT

ChatGPT now runs custom workflows as plugins, and Custom GPTs retire on December 11, 2026. The quickest path is to create Email Doctor as a GPT from the files in [`chatgpt/`](chatgpt), then click **Migrate to plugin**. Step-by-step setup is in [`chatgpt/README.md`](chatgpt/README.md).

## Run the checker yourself

Python 3.8 or later, standard library only:

```bash
python claude/email-doctor/scripts/email_doctor.py --file email.txt
```

Start `email.txt` with a `Subject: ...` line, or pass `--subject` and `--body`. Add `--json` for structured output.

## What's inside

| Path | Contents |
|---|---|
| `claude/email-doctor/SKILL.md` | The Claude skill: when to use it and the check → report → rewrite → re-check workflow |
| `claude/email-doctor/scripts/email_doctor.py` | The checker, matching the website's scoring exactly |
| `claude/email-doctor/references/catalog.json` | 405 phrases with severity, reason, source URL, and suggested fixes |
| `claude/email-doctor/references/rewrite-rules.md` | The rules "Fix it!" uses on the website |
| `claude/email-doctor/references/research.md` | What filters weigh, scoring, reply-rate evidence, and the pre-send checklist |
| `chatgpt/` | ChatGPT setup: instructions and knowledge files for a GPT that migrates to a plugin |

## Feedback

Email Doctor is in beta. Send feedback to [mike@velocitylab.ai](mailto:mike@velocitylab.ai).

## License

MIT. See [LICENSE](LICENSE). Rule names and scores attributed to Apache SpamAssassin are cited from its Apache-2.0 licensed rule files; vendor lists and studies are cited by URL in `catalog.json` and `research.md`.
