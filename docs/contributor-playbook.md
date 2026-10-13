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
| **Paid** | $20 sent by PayPal, Venmo, or Amazon.com eGift card, recorded | Within 7 days of publishing |
| **Lapsed / Declined** | No reply in 14 days (Template C), or declined (Template E) | — |

## Turning payment on or off (volunteer mode)

One switch controls everything: `payEnabled` in `js/contribute-config.js`. Set it to `false` for volunteer
mode (for outreach through admissions offices or ambassador programs), `true` to pay again. Then rebuild:

    python3 build.py && python3 build_schools.py

The build updates every page to match: the "Get Paid!" nav pill, the homepage banner, the contribute page,
the terms (the payment section and its numbering), the form's pay notices, submission emails ("Payment
program off"), and the link-preview text and image (`images/og-contribute-volunteer.png` when off).
Amount, cap and payment methods are kept, so turning it back on picks up where you left off.

Switch it a few days before outreach: Google snippets and cached link previews can lag by days or weeks.

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
   docstory.org
   ```
4. **Tracker:** a Google Sheet with one row per submission and these columns:
   `Reference · Received · School · Year · Full name · School email · Credit · Paid-eligible ·
   Status · Verification sent · Reminder sent · Verified on · Published on · Live URL ·
   Payment method · Payment handle · Paid on · Amount · Questions opt-in · Questions email ·
   Questions until · Notes`

   Add a second tab, **Reader questions**, with one row per question:
   `Received · Reader email · Interview ref · Student · Status (forwarded / not forwarded / relayed) ·
   Forwarded on · Notes`

## Step by step

### 1. A submission arrives
The subject reads like `Interview DS-261008-K7QM · Rush Medical College · MS3 · Paid $20`.
Add a row to the tracker with status **Received**, and send Template H so they know it arrived
(skip it if you'll send Template A within a day or two). The email contains:

- **Payment:** whether the school was eligible when they submitted (published count vs. the cap of 5)
- **School email (verify):** the address you'll verify
- **Interview file path** and **Interview file (markdown):** a ready-to-publish file
- **Reader questions:** `OPTED IN · send to … · until June 1, YYYY` or `Not opted in`. Copy the
  address into the tracker's **Questions email** column. It's deliberately not in the markdown file,
  which only says `reader_questions: true` and the end date; that's what shows the question box.
- **Writing check** and **Writing record (per answer):** how much of each answer was typed vs pasted,
  the largest single paste, roughly how long it took, and in how many sittings. If any answer is at
  least half pasted, the subject ends in `· ⚠ check writing`.

  Treat this as a prompt to read closely, not a verdict: some students draft in Notes or Docs and paste.
  Together with generic wording, a mostly-pasted answer written in under a minute is a strong sign of AI
  text. Ask for a rewrite in their own words (Template E) or decline under the terms (section 2).
  "No record" means the answer was written before tracking began (2026-10-12) or in another browser.

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

### 3. Edit (in the Interview Desk)
Use the **DocStory Interview Desk**, a private page only you can open:
https://claude.ai/artifact/JjseiF65jow5UQWL4rNXVu

1. **Add a submission:** paste the whole submission email (or choose the downloaded .eml file).
2. **Proofread all answers:** Claude fixes spelling, grammar, punctuation and capitalization only.
   Changes are highlighted, and the original stays one click away.
3. **Edit the final text** of each answer: lightly, for format, length and clarity, never for meaning.
4. **Ask for more detail** on any thin answer, with a one-line note on what you'd like added.
5. **Copy the approval email** (step 4 below is built for you, with your detail requests lettered) and
   send it from Gmail. Mark it **Sent for approval**.
6. When they reply, paste each addition under its answer and choose **Add to answer** (it gets the same
   spelling-only pass). Set the status to **Approved** and tell Claude "publish DS-XXXXXX-XXXX":
   Claude reads the final text from the desk, adds the file, and rebuilds the site.

### 4. Send the verification email (Template A)
Send a **new email** to their school address, not a reply to the Web3Forms notification. A
reply would quote the private fields back to them. Paste the edited interview into the body.

**A reply counts as verification only if:**
- it comes from **the same .edu address** you wrote to (in Gmail, open the message and check
  the full sender; be wary of “via” relays or a lookalike domain),
- it approves the edits, or asks for changes you then make and re-confirm, and
- for paid interviews, it includes a payment method and handle: a PayPal or Venmo username or
  email, or the email address for an Amazon.com eGift card.

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

If the contributor opted in to reader questions, keep the `reader_questions` and `questions_until`
lines in the file. The "Ask [name] a question" box then appears on their interview until that date.
To turn it off (they opt out, or ask early), delete those two lines and rebuild.

### 7. Pay (within 7 days of publishing)
- **PayPal or Venmo:** send $20 with the note `DocStory interview DS-XXXXXX-XXXX`. **Check the
  payee name** on the account roughly matches the contributor. If it doesn't, confirm by email first.
- **Amazon.com eGift card:** at amazon.com/gift-cards, buy a $20 **eGift card** (email delivery,
  not a physical card) to the address they gave. Put their first name in the "To" field and
  `DocStory interview DS-XXXXXX-XXXX. Thank you!` in the message, and send it from your DocStory
  Amazon account. Save the order number. A gift card can go to any email, so there's no name to
  check: the rule below about replies from the verified .edu address is what protects you.
- Record method, handle (or gift card email), date, amount, and the transaction or order number.
  If a handle or gift card email already appears in the tracker for another contributor, stop and
  check before paying. Mark **Paid**. Template D already tells them it's
  coming; no separate email needed unless something goes wrong.

### 8. Reader questions (for contributors who opted in)
A reader's question arrives with the subject `Reader question · DS-XXXXXX-XXXX · [Student] · [School]`.
It includes the interview link, the reader's email and first name, and the question. Add a row to the
**Reader questions** tab.

1. **Screen it.** Don't forward anything abusive, sexual, harassing, spammy, asking for patient
   information, or unrelated to medical school. Mark those **not forwarded**; there's no need to reply.
   Also check the student is still within their **Questions until** date.
2. **Forward it** with Template F to the student's **Questions email** from the tracker, and mark
   **Forwarded**. The student then either emails the reader directly or replies to you.
3. **If the student replies to you**, send their answer to the reader with Template G, from your
   DocStory address, without the student's email. Mark **Relayed**.
4. **Opt-outs:** if a student asks to stop, delete `reader_questions` and `questions_until` from
   their interview file, rebuild, and update the tracker.

### Safety rules
- Never pay before the interview is published.
- Never ask for bank details, Social Security numbers, or passwords. PayPal or Venmo handles, or a gift
  card email address, only.
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
> 2. [Paid only] How you'd like your $20: PayPal, Venmo, or an Amazon.com eGift card. For PayPal or
>    Venmo, the username or email to send it to; for a gift card, the email address to deliver it to.
>
> [If they opted in to reader questions] You also chose to receive follow-up questions from readers
> until **June 1, [YYYY]**, sent to **[address]**. If that's not right, or you'd rather not, just say
> so in your reply.
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
> payment choice (PayPal, Venmo, or Amazon.com eGift card) and where to send it] by **[date]**, and we'll take it from there.
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
> [Paid only] We'll send your $20 [by PayPal/Venmo to [handle] / as an Amazon.com eGift card to
> [email]] within 7 days, with the note “DocStory interview [REF]”.
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

### Template F: Forward a reader's question to the student
**Subject:** A reader has a question about [School] ([REF])

> Hi [First name],
>
> A reader of your DocStory interview sent you a question:
>
> > [Question]
>
> — [Reader first name, or "A reader"]
>
> **Want to answer?** You can email them directly at **[reader email]**. They'll see the address you
> reply from. Or, to keep your email private, just reply to this message and we'll pass your answer
> along without your address. If you'd rather not answer, no need to do anything.
>
> You're receiving this because you opted in to reader questions until **June 1, [YYYY]**. Reply
> "stop" anytime to opt out.
>
> [Signature]

### Template G: Pass a student's answer to the reader
**Subject:** Re: your question for [Student credit name] at [School]

> Hi [Reader first name],
>
> [Student credit name] answered your question:
>
> > [Answer]
>
> They chose to reply through DocStory, so please reply to this email if you'd like us to pass a
> short follow-up along.
>
> [Signature]

### Template H: Received (confirmation)
**Subject:** We received your DocStory interview ([REF])

> Hi [First name],
>
> Thanks for sharing your experience at [School]. Your interview arrived safely; your reference
> number is **[REF]**.
>
> We'll review it within 7 days. If any answers need a bit more detail, we'll ask then. After that,
> we'll email this address with your edited interview to verify and approve before anything goes live.
>
> [Signature]
