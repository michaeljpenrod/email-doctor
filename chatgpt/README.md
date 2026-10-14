# Email Doctor for ChatGPT

ChatGPT is replacing Custom GPTs with plugins. OpenAI retires Custom GPTs on December 11, 2026, and a migrated GPT becomes a plugin whose instructions are a skill and whose knowledge files are reference files. The steps below create Email Doctor as a GPT and then migrate it, which gives you a working plugin in about seven minutes.

## 1. Create the GPT

1. In ChatGPT, open **Explore GPTs**, then **Create**, then the **Configure** tab.
2. **Name:** Email Doctor
3. **Description:** Checks cold emails for spam-filter triggers and reply-rate problems, explains every flag with its source, and rewrites them. From velocitylab.ai.
4. **Instructions:** paste the full contents of [`instructions.md`](instructions.md).
5. **Conversation starters:**
   - Check this cold email for spam triggers
   - Rewrite my outreach email to get more replies
   - Why would this subject line land in spam?
   - What else affects deliverability besides wording?
6. **Knowledge:** upload all four files in [`knowledge/`](knowledge/): `email_doctor.py`, `catalog.json`, `rewrite-rules.md`, and `research.md`.
7. **Capabilities:** turn on **Code Interpreter & Data Analysis**, so it can run the checker. Web search and image generation aren't needed.
8. Click **Create** and save it as **Only me**.

## 2. Migrate it to a plugin

1. Open **My GPTs** and find Email Doctor.
2. Click **Migrate to plugin**, then **Migrate to plugin** again to confirm. The checks should all say "No issues found".
3. Click **Try in chat**. Paste any cold email after the `@Email Doctor` prompt.

The reply should start with a score out of 100, then list SPAM filter issues and reply rate issues. On the "Try an example" email at velocitylab.ai/emaildoctor it scores 55/100, the same as the website.

## Notes

- The plugin starts private. Sharing it inside a workspace is up to your workspace admin, and the public plugin directory requires OpenAI's review.
- ChatGPT plugin skills use the same layout as the Claude skill in [`../claude/email-doctor`](../claude/email-doctor): a folder with `SKILL.md`, `references/`, and `scripts/`. If you build plugins directly, you can package that folder as the plugin's skill. See OpenAI's [skills guide](https://developers.openai.com/plugins/build/skills) and [plugin packaging guide](https://developers.openai.com/plugins/build/plugins).
- If your account no longer lets you create GPTs, ask ChatGPT's plugin creator to build a plugin from the files in [`../claude/email-doctor`](../claude/email-doctor).
