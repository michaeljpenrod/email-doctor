# Email Doctor for ChatGPT

## Install

1. Download [**email-doctor-plugin.zip**](https://github.com/michaeljpenrod/email-doctor/raw/main/chatgpt/email-doctor-plugin.zip).
2. In ChatGPT, open **Plugins**, click **Add**, and choose **Upload plugin archive**.
3. Select the zip, click **Add plugin**, then **Install plugin**.

## Use it

Start a message with **@email-doctor** and paste a cold email. Ask it to check the email, or to fix it.

## What's inside

```
plugin.json                          name, version, description, links
skills/email-doctor/SKILL.md         the workflow: check, report, rewrite, re-check
skills/email-doctor/scripts/         the checker
skills/email-doctor/references/      the phrase catalog, rewrite rules, and research notes
```

The manifest is in [`plugin/plugin.json`](plugin/plugin.json), and the skill is the same one in [`../claude/email-doctor`](../claude/email-doctor).
