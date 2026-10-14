# The research behind Email Doctor

Read this when the user asks why something is flagged, how much wording matters, or what else affects deliverability. Every claim has its source. Vendor-published data is labeled as such.

## Contents

1. What spam filters actually weigh
2. How the word catalog is built and scored
3. Reply-rate rules, with sample sizes and effects
4. Before you send: the infrastructure checklist

## 1. What spam filters actually weigh

- **No mailbox provider publishes a spam-word list.** Google's sender guidelines regulate deception and structure, not vocabulary: no fake "Re:"/"Fwd:", no hidden text, links must be clear about where they lead (https://support.google.com/a/answer/81126).
- **Google says a single "spammy" trait doesn't make a message spam.** Its models weigh thousands of signals together (https://workspace.google.com/blog/product-announcements/ridding-gmail-of-100-million-more-spam-messages-with-tensorflow).
- **Disguising a word is worse than using it.** Gmail's RETVec classifier raised spam detection 38% and was built to catch homoglyphs, leetspeak, and invisible characters (https://security.googleblog.com/2023/11/improving-text-classification.html).
- **SpamAssassin, the source of most "trigger word" lists, now scores plain vocabulary near zero.** An ALL-CAPS subject is 0.5 points and "ACT NOW" 0.1, against a 5.0 spam threshold. Fraud greetings, obfuscation, and image-only bodies carry 2.5 to 3.8 points (https://raw.githubusercontent.com/apache/spamassassin/trunk/rules/50_scores.cf).
- **Infrastructure decides most placement.** Gmail and Microsoft reject unauthenticated mail at volume (550 5.7.26 and 550 5.7.515). Gmail requires a spam-complaint rate under 0.3% and recommends under 0.1% (https://support.google.com/a/answer/14229414).
- **Sending volume matters more than copy.** Peeker's Q3 2026 data on 43M cold emails (vendor-published) found 44% of Google Workspace domains sending 15 to 19 emails per inbox per day were burned, vs 19% under 10 per day (https://www.peeker.ai/state-of-deliverability-Q3-2026).

So word flags predict how legacy corporate filters (SpamAssassin, Proofpoint, Mimecast) and human readers react. Gmail and Outlook decide mostly on reputation, authentication, and volume. Say this plainly when it's relevant, rather than implying a word count predicts placement.

## 2. How the word catalog is built and scored

`catalog.json` holds 405 phrases in 10 categories. Each entry has a pattern, severity, a one-sentence reason, a source URL, and suggested fixes. Phrases come from Apache SpamAssassin's rules (68 entries cite a rule and its score), a consensus core from 22 vendor lists, and modern additions (phishing lures, fake reply chains, AI-sounding vocabulary).

| Category | Group | Default severity |
|---|---|---|
| Phishing / security lures | SPAM filter issues | critical |
| Deceptive framing | SPAM filter issues | critical |
| Money claims | SPAM filter issues | high |
| Guarantee / overpromise | SPAM filter issues | high |
| Health, pharma, gambling, adult | SPAM filter issues | high |
| Urgency / scarcity | SPAM filter issues | medium |
| Free / discount | SPAM filter issues | medium |
| Tech / crypto hype | SPAM filter issues | medium |
| Hype / social-proof claims | Reply rate issues | low |
| Clichés / AI vocabulary | Reply rate issues | low |

**Scoring:** critical 15 points, high 6, medium 3, low 1. Phrases in the subject count double. ALL-CAPS matches count 1.5x. When two or more high or critical phrases appear together, they count 1.5x. Format checks (stacked "!!", hidden characters, shortened links, raw-IP links, 3+ links, ALL-CAPS subject, attachments) add fixed points. Score = 100 − 34 × ln(1 + points/10). Bands: Strong 85+, Good 70 to 84, Needs work 50 to 69, Poor under 50.

**Deliberately not flagged:** ordinary English that older lists flag alone, such as free, now, offer, deal, click, order, new, price, and money. These count only inside a listed phrase. Merge tags like {{first_name}} are a low-severity note, because they're normal in sequencer templates.

## 3. Reply-rate rules

All datasets below are vendor-published and correlational. Reply rate is the metric that matters; open rates since 2021 are inflated by Apple Mail Privacy Protection.

| Rule | Target | Evidence | Strength |
|---|---|---|---|
| Subject length | 1 to 4 words | Belkins 5.5M: 2-4 words 46% opens vs 34% at 10 words; Boomerang 40M; Gong/30MPC 85M | Strong |
| Subject not empty | Always write one | Gong/30MPC 85M: blank subjects +30% opens but −12% replies | Strong |
| Personalized subject | Company or name | Belkins 5.5M: 7% vs 3% replies | Strong |
| No salesy subject | No urgency or hype | 30MPC: salesy language cuts opens up to 17.9% | Strong |
| One ask | Exactly one | Saleshandy 30.3M (2026): single soft CTA +78% positive replies | Strong |
| Interest-based ask | "Worth a chat?" not "Tuesday at 2?" | Gong 304K: 2x+ replies in cold first touches | Strong |
| Problem-first opener | Their problem before your product | 30MPC/Gong 85M: +20% replies; pitching cuts replies up to 57% | Moderate |
| Credibility after the problem | One line | 30MPC: +41% | Moderate |
| No ROI stats in first touch | Avoid "2x", "30% more" | Gong 132K: −15% meetings | Moderate |
| Company or problem personalization | Reference their situation | Woodpecker 20M: ~2x replies; Backlinko 12M: +32.7% | Strong |
| Body length | 50 to 100 words | Smartlead 3.2M: 9.1% replies at 50-80 words vs 2.1% under 30; Hunter 34M: weak correlation (−0.09) | Strong direction, small effect |
| Reading level | Grade 7 or under | Boomerang 40M (2016): 3rd-grade level +36% vs college level | Single source |
| Questions | 1 to 3 | Boomerang 40M: +50% vs none | Single source |
| Links | 0 to 1, no shorteners | SmartReach 2.3M: 5+ links often flagged | Moderate |
| Tracking pixel | Off for cold first touch | Snov.io 44M: 2.36% replies without vs 1.08% with | Strong direction |
| Follow-ups | 3 to 6 over 14 to 28 days | Backlinko 12M: one follow-up +65.8%; Smartlead 3.2M: third follow-up peaks at 7.4% | Strong |

## 4. Before you send

The copy can't fix these, and they decide more than wording does:

1. **SPF, DKIM, and DMARC pass with your From domain aligned.** Gmail and Microsoft reject mail that fails this at volume.
2. **Sends per inbox per day:** 10 or fewer on Google Workspace, 5 or fewer on Microsoft (Peeker Q3 2026, 43M emails, vendor-published).
3. **Sending domain:** at least a month old, warmed up, and a .com rather than .info or .xyz (Peeker: .info replied at 81% of the same sender's .com).
4. **List quality:** verified addresses, bounce rate under 2% (Saleshandy 30.3M: bad lists bounce 10.6% vs 1.2% verified).
5. **Open tracking off** for the first touch (Snov.io 44M).
