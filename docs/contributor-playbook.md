# Contributor playbook: verification, publishing, and payment

How a submitted interview becomes a verified, published, paid DocStory interview. Every
contributor-facing promise on the site (review within 7 days, 14 days to reply, payment within
7 days of publishing) lives in `js/contribute-config.js`. If you change a number there, follow
the new number here too.

## The pipeline at a glance

| Status | What happens | Your deadline |
|---|---|---|
| **Received** | Web3Forms emails you the submission | — |
| **In review** | You screen it and edit it | Within 7 days of receipt |
| **Verification sent** | You email the contributor's .edu address (Template A) | Same day as editing |
| **Reminder sent** | No reply after 7 days (Template B) | Day 7 after verification email |
| **Verified & approved** | They reply from the .edu address approving | They have 14 days |
| **Published** | Interview file committed, site rebuilt, live link emailed (Template D) | — |
| **Paid** | $50 sent by PayPal or Venmo, recorded | Within 7 days of publishing |
| **Lapsed / Declined** | No reply in 14 days (Template C), or declined (Template E) | — |

## One-time setup

1. **Use one dedicated sending address** for all contributor email, and put it in
   `contactEmail` in `js/contribute-config.js`. The site then tells contributors, “We only email
   you from …”, which protects them from impersonators and makes your emails recognizable.
2. **Gmail label and filter:** filter messages from Web3Forms into a label such as
   `DocStory/Submissions`. Web3Forms' free plan keeps submissions for only 30 days, so these
   emails are your permanent record. Never delete them.
3. **Email signature** for the sending address:
   ```
   — Arnie
   DocStory · Real stories from real med schools
   docstory-website.vercel.app
   ```
4. **Tracker:** a Google Sheet with one row per submission and these columns:
   `Reference · Received · School · Year · Full name · School email · Credit · Paid-eligible ·
   Status · Verification sent · Reminder sent · Verified on · Published on · Live URL ·
   Payment method · Payment handle · Paid on · Amount · Notes`

## Step by step

### 1. A submission arrives
The subject reads like `Interview DS-261008-K7QM · Rush Medical College · MS3 · Paid $50`.
Add a row to the tracker with status **Received**. The email contains:

- **Payment:** whether the school was eligible when they submitted (published count vs. the cap of 5)
- **School email (verify):** the address you'll verify
- **Interview file path** and **Interview file (markdown):** a ready-to-publish file

### 2. Screen it (within 7 days)
- **Domain matches the school.** Rush students use `@rush.edu`, not some other college's
  domain. If unsure, search the domain plus “medical school” or check the school's site.
  An undergraduate or unrelated .edu means: ask for their medical school address, or decline.
- **One paid interview per person.** Search the tracker for the same name and email.
- **Content check:** real, specific answers; no patient details (dates + places + conditions
  can identify someone); nothing defamatory; no exam content.
- **Quality bar** (Contributor Terms, section 5): roughly the caliber of the average
  interview already on the site. If it falls short, don't decline straight away. Send
  Template E naming the answers that need more detail, and wait for the expanded version
  before sending the verification email. Decline (unpaid) only if it still falls short.
- **Paid-eligibility still holds.** Honor what the email says. It reflects the count when
  they submitted, which is the promise in the Contributor Terms.

### 3. Edit
Copy the markdown block from the email into the suggested path (for example
`content/interviews/rush-medical-college/jordan-lee.md`). Edit lightly for format, length,
spelling, and clarity, never for meaning. Don't commit it yet.

### 4. Send the verification email (Template A)
Send a **new email** to their school address, not a reply to the Web3Forms notification. A
reply would quote the private fields back to them. Paste the edited interview into the body.

**A reply counts as verification only if:**
- it comes from **the same .edu address** you wrote to (in Gmail, open the message and check
  the full sender; be wary of “via” relays or a lookalike domain),
- it approves the edits, or asks for changes you then make and re-confirm, and
- for paid interviews, it includes a payment handle.

Mark **Verification sent** in the tracker.

### 5. No reply? (Templates B and C)
Day 7: send Template B. Day 14: send Template C and mark **Lapsed**. If they write back later,
pick it up again; lapsing is about not leaving things open forever.

### 6. Publish (Template D)
1. Commit the edited file (I can do this when you tell me the reference number).
2. Rebuild (`python3 build.py` and `python3 build_schools.py`) and push. The school's
   published count goes up automatically, and once a school reaches 5 the form stops offering
   payment for it.
3. Send Template D with the live link. Mark **Published**.

### 7. Pay (within 7 days of publishing)
- Send $50 by their chosen method with the note `DocStory interview DS-XXXXXX-XXXX`.
- **Check the payee name** on the PayPal or Venmo account roughly matches the contributor. If
  it doesn't, confirm by email first.
- Record method, handle, date, and amount. Mark **Paid**. Template D already tells them it's
  coming; no separate email needed unless something goes wrong.

### Safety rules
- Never pay before the interview is published.
- Never ask for bank details, Social Security numbers, or passwords. PayPal or Venmo handles only.
- Only send payment to a handle that arrived in a reply from the verified .edu address.

---

## Email templates

Replace the bracketed parts. Keep the reference number in every subject line.

### Template A: Verification and approval
**Subject:** Your DocStory interview ([REF]): please verify and approve

> Hi [First name],
>
> Thank you for sharing your experience at [School] with DocStory. Your reference number is
> **[REF]**.
>
> We've lightly edited your interview for format and clarity. It's below exactly as it will
> appear, credited as **[Credit line]**.
>
> **To verify and approve, reply to this email from this address** with:
> 1. “I approve,” or any changes you'd like.
> 2. [Paid only] How you'd like your $50: PayPal or Venmo, and the username or email to send it to.
>
> Please reply by **[date, 14 days out]**. Once you approve, we'll publish your interview
> [paid only: and send payment within 7 days of it going live].
>
> We'll only ever contact you from this address, and we'll never ask for passwords or bank
> details.
>
> [Edited interview pasted here]
>
> [Signature]

### Template B: Reminder (day 7)
**Subject:** Reminder: your DocStory interview ([REF])

> Hi [First name],
>
> Just a quick reminder that your interview about [School] is ready to go live. Reply to our
> email below from your school address with “I approve” (or any edits)[paid only: and your
> PayPal or Venmo details] by **[date]**, and we'll take it from there.
>
> [Signature]

### Template C: Lapsed (day 14)
**Subject:** Your DocStory interview ([REF]) is on hold

> Hi [First name],
>
> We haven't heard back, so we've put your interview on hold and won't publish it. If you'd
> still like it to go live, just reply from your school address. We'd be glad to pick it back up.
>
> [Signature]

### Template D: Published
**Subject:** Your DocStory interview is live ([REF])

> Hi [First name],
>
> Your interview is now live: [link]
>
> [Paid only] We'll send your $50 to [handle] by [method] within 7 days, with the note
> “DocStory interview [REF]”.
>
> Thank you for helping applicants see what [School] is really like. If you ever want it
> changed, made anonymous, or taken down, just reply from your school address.
>
> [Signature]

### Template E: Revise or decline
**Subject:** About your DocStory interview ([REF])

> Hi [First name],
>
> Thank you for your submission. Before we can publish it, [we need a little more detail in a
> few answers / we need to remove some details that could identify a patient / we need to
> verify a medical school email address]. [Specifics.]
>
> [If declining: Unfortunately we're not able to publish this interview because [reason].
> We really appreciate the time you took.]
>
> [Signature]
