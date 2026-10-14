# Email Doctor for ChatGPT

Set up Email Doctor as a Custom GPT in about five minutes. You need a ChatGPT plan that can create GPTs.

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
7. **Capabilities:** turn on **Code Interpreter & Data Analysis**, so the GPT can run the checker. Web browsing and image generation aren't needed.
8. Click **Create**, and choose who can use it.

To check it works, paste any cold email. The reply should start with a score out of 100, then list SPAM filter issues and reply rate issues.
