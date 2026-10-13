# Search & AI visibility checks

A fixed set of questions premeds actually ask, checked once a month, so we can tell whether new
interviews and the SEO work move anything. Keep the questions identical between runs.

**How to run:** search each question in Google and Bing (logged out or in a private window), and ask it
in ChatGPT, Perplexity, and Claude with web search on. Record whether docstory.org shows up: the rank
in search results (1–10, or "–" if not on page 1), or "cited" / "–" for the AI tools.

## The questions

| # | Question | Kind |
|---|----------|------|
| 1 | What is student life like at Harvard Medical School? | School we cover |
| 2 | What's a typical day like for a medical student at UC Irvine School of Medicine? | School we cover |
| 3 | Is USC Keck School of Medicine collaborative or competitive? | School we cover |
| 4 | What do students say about the culture at Creighton University School of Medicine? | School we cover |
| 5 | Touro College of Osteopathic Medicine (Middletown) student experience, pros and cons | School we cover |
| 6 | What is the curriculum like at Mayo Clinic Alix School of Medicine, from a student's perspective? | School we cover |
| 7 | What is it like to be a student at University of Miami Miller School of Medicine? | School we cover |
| 8 | What is Wayne State University School of Medicine like, day to day? | School we cover |
| 9 | What is student life like at Kentucky College of Osteopathic Medicine? | School we cover |
| 10 | Where can I read interviews with medical students about what their school is really like? | General |
| 11 | Where can I find first-hand accounts from medical students about their schools? | General |
| 12 | How does studying in medical school differ from undergrad? | Topic |
| 13 | What advice do medical students have for premeds? | Topic |
| 14 | How do medical students maintain their mental health? | Topic |
| 15 | DocStory medical school | Brand |

## Baseline: October 13, 2026

Run by Claude before the At-a-glance summaries, IndexNow, and AI-visit tracking shipped.

| # | Google | Bing | Claude web search | ChatGPT | Perplexity |
|---|--------|------|-------------------|---------|------------|
| 1 | – | – | – | not run | not run |
| 2 | – | – | – | not run | not run |
| 3 | – | – | – | not run | not run |
| 4 | – | not run | – | not run | not run |
| 5 | – | – | – | not run | not run |
| 6 | not run | not run | – | not run | not run |
| 7 | not run | not run | – | not run | not run |
| 8 | not run | not run | – | not run | not run |
| 9 | not run | not run | – | not run | not run |
| 10 | not run | – | – | not run | not run |
| 11 | not run | not run | – | not run | not run |
| 12 | not run | not run | – | not run | not run |
| 13 | not run | not run | – | not run | not run |
| 14 | not run | not run | – | not run | not run |
| 15 | – | 1 | – | not run | not run |

Google rows 1–5 used close variants of the wording (e.g. "UC Irvine School of Medicine student interview
typical day"); also checked with no DocStory result: "Rush Medical College student experience",
"USC Keck medical school student culture". ChatGPT and Perplexity need a signed-in account, so those
columns are for the first manual run.

### What the baseline shows

- **DocStory appears nowhere except Bing's brand search.** Even "DocStory medical school" on Google
  returns UCLA, U.S. News and Wikipedia; Google reads it as "doc story".
- **Google has indexed the new site** (`site:docstory.org` lists the current school pages with the new
  titles and snippets). The pages are in the index; they just don't rank yet.
- **Bing's copy is stale:** about 50 pages, many under old `…/index.html` addresses with old snippets
  ("Explore 150+ medical schools across the US and Canada"), plus old WordPress tag pages and
  docstoryorg.wordpress.com. Bing feeds ChatGPT search, so refreshing it matters (IndexNow "send every
  page" once the branch is live).
- **The gap is real and specific.** For question 2, Claude's search answered that it *couldn't find a
  first-hand account of a typical day at UC Irvine*; DocStory has three. For USC Keck it found nothing
  on peer culture. AI tools are looking for exactly what we publish and not finding it.
- **Who wins today:** Student Doctor Network (old applicant interview-day reports, mostly 2009–2010),
  Reddit, the schools' own pages, and admissions-coaching sites (crackingmedadmissions, confetto.ai,
  nextgenmedprep). Accepted.com's "What is Medical School Really Like?" series is the closest
  competitor in format.
- **"Student interview" is ambiguous.** Searchers and search engines read "medical school student
  interview" as the *admissions* interview (questions, prep). Results for those words are all
  interview-prep sites. Our titles may need wording like "what it's like" or "student Q&A".
</content>
</invoke>
