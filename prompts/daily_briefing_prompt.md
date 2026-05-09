# Daily AI, BI, Research & Reflection Briefing Prompt

Generate the Daily AI, BI & Research Briefing for today.

## Required repository inputs

Read the latest source pack from:

/data/source_packs/

Also read these memory and control files:

/data/memory/theme_roadmap.md
/data/memory/source_watchlist.md
/data/memory/learning_rotation.md
/data/memory/academic_rotation.md
/data/memory/memory_log.md if it exists

## Output and archive instruction

Preferred output format: clean Markdown.

If GitHub write access is available in the current ChatGPT session, create or update this file after generating the briefing:

/reports/daily/YYYY-MM-DD-daily-briefing.md

Use today's date in ISO format. Example:

/reports/daily/2026-05-09-daily-briefing.md

If GitHub write access is not available, output the full Markdown briefing in the chat and clearly say:

"GitHub write access was not available in this run. Copy this Markdown into /reports/daily/YYYY-MM-DD-daily-briefing.md."

Do not output strange citation placeholder characters. If source citations cannot be rendered cleanly, use normal Markdown links or cite source titles and URLs from the source pack.

PDF note: do not try to create a PDF unless a PDF-generation tool is explicitly available. The Markdown report is the source-of-truth archive. A PDF can be generated later from the Markdown if needed.

## Briefing structure

1. Executive brief - 5 bullets only
2. What changed since yesterday
3. News radar
4. Senior analyst insight
5. FMCG / sales & distribution practical implication
6. Academic paper brief relevant to the research theme
7. Technology learning bite
8. AI engineering concept
9. Daily reflection
10. Beginner German language drill
11. Source quality table
12. Memory update

## Quality rules

- Use source-backed facts.
- Do not invent statistics.
- Separate facts, assumptions and inferences.
- Do not use every source; select the strongest and most relevant items.
- Be sceptical about company/vendor blogs.
- Treat arXiv as preprint/early signal, not settled evidence.
- Flag irrelevant/noisy academic items instead of forcing them into the briefing.
- Clearly state which source categories are still missing.
- If evidence is weak, say so.
- Write like a senior strategy/BI analyst, not a generic newsletter.
- Keep the briefing readable in 8-12 minutes.

## Memory update instruction

At the end of the briefing, include a short memory update with:

- Main theme
- Strongest insight
- Strongest source signal
- Academic note
- Source weaknesses
- Next issue angle

If GitHub write access is available, also append or update the relevant memory entry in:

/data/memory/memory_log.md

If that file does not exist, create it.
