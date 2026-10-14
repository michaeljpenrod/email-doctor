# Email Doctor for ChatGPT

Email Doctor installs in ChatGPT as a plugin, in about two minutes.

1. Download [`email-doctor-plugin.zip`](email-doctor-plugin.zip).
2. In ChatGPT, open **Plugins**, click **Add** at the top right, and choose **Upload plugin archive**.
3. Choose `email-doctor-plugin.zip`, then click **Add plugin**.
4. On the plugin's page, click **Install plugin**.
5. In any chat, type **@email-doctor** and paste a cold email.

The reply starts with a score out of 100, then lists filter-related and reply-rate issues with fixes. On the "Try an example" email at velocitylab.ai/emaildoctor it scores 55/100, the same as the website.

## What's in the plugin

The zip holds a standard plugin package:

```
plugin.json                          name, version, description, author, links
skills/email-doctor/SKILL.md         the workflow: check, report, rewrite, re-check
skills/email-doctor/scripts/         the checker (Python, standard library only)
skills/email-doctor/references/      the 405-phrase catalog, rewrite rules, research
```

The skill folder is identical to the Claude skill in [`../claude/email-doctor`](../claude/email-doctor). The manifest is in [`plugin/plugin.json`](plugin/plugin.json). See OpenAI's guides on [skills](https://developers.openai.com/plugins/build/skills) and [packaging plugins](https://developers.openai.com/plugins/build/plugins).

## Legacy: Custom GPT

`instructions.md` and `knowledge/` set Email Doctor up as a Custom GPT. OpenAI retires Custom GPTs on December 11, 2026, so use the plugin above instead.
