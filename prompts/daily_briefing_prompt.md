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

The preferred final report format is PDF.

Produce two separate outputs:

### Output 1 - PDF briefing

Create a polished PDF briefing titled:

Daily AI, BI & Research Briefing - YYYY-MM-DD

The PDF should be suitable for upload to:

/reports/daily/pdf/YYYY-MM-DD-daily-briefing.pdf

The PDF should include:
- Executive brief
- What changed since yesterday
- News radar
- Senior analyst insight
- FMCG / sales & distribution practical implication
- Academic paper brief
- Technology learning bite
- AI engineering concept
- Daily reflection
- Beginner German language drill
- Source quality review

Use clean formatting, readable headings, bullets, and normal source links. Do not output strange citation placeholder symbols.

### Output 2 - Markdown memory update

After the PDF, output a separate Markdown block that can be copied directly into:

/data/memory/memory_log.md

Use this exact structure:

## YYYY-MM-DD

### Main theme
...

### Strongest insight
...

### Strongest source signal
...

### Academic note
...

### Source weaknesses
...

### Next issue angle
...

If PDF creation is unavailable, output the full briefing as clean GitHub-ready Markdown and clearly state that the user should convert it to PDF manually.

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
