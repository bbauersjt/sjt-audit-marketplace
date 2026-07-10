---
name: writing-styles
description: The firm's house writing voice for the prose parts of any deliverable. Use whenever drafting or wording workpaper documentation, memos, emails, client or staff facing materials (slides, presentations, training and resource docs), or the written portions of a financial statement set (footnotes and disclosures, MD&A type narrative, findings and responses). Governs voice, tone, and wording only. Pick the module that matches what is being written and apply it. Defers file format, layout, and mechanics to the relevant format skill (docx, pptx, workpapers, fs skills) and never overrides prescribed boilerplate such as auditor report and opinion language or required GAAP and GAGAS wording. Trigger even when not named. Any request to draft, write, or word up one of these deliverables should consult this skill. Extensible. Add a new module and a menu row for new voices.
---

# Writing Styles

The firm's writing voice, one module per kind of deliverable. Governs how something is worded: voice, tone, and the shape of the prose. It does not govern file format, layout, or mechanics (those belong to the docx, pptx, workpapers, and FS skills), and it never rewrites prescribed or boilerplate text.

## How to use

1. Identify what is being written from the menu.
2. Read that one module in styles/.
3. Apply its voice. If a deliverable mixes types (a memo inside a workpaper), the dominant document wins.

## Menu

| You're writing | Module |
|---|---|
| Workpaper documentation, binder files, testwork narrative, tickmark notes, conclusions | styles/workpapers.md |
| Memos (technical or position memos) and emails | styles/memos-emails.md |
| Client or staff facing materials that aren't FS or formal letters: slides, presentations, training, resource docs, skill documentation, and internal how-to or reference write-ups | styles/client-facing.md |
| The written parts of a financial statement set: footnotes and disclosures, accounting policy notes, MD&A type narrative, findings and responses | styles/financial-statements.md |

Completed: workpapers; memos-emails (both halves); client-facing (presentations and staff-facing docs); financial-statements (notes across commercial/nonprofit/governmental, plus the findings schedule). All four style modules are built.

## Scope guardrails (all modules)

Voice only. Apply wording and tone. Leave file format, pagination, table structure, and house formatting to the format skill that owns the document.

Never touch prescribed text. Auditor's reports and opinions, standard report paragraphs, required statement titles, and any wording mandated verbatim by GAAP, GAGAS, the Uniform Guidance, or a regulator follow their exact prescribed form. This skill is for the parts that are written, not the parts that are prescribed. When in doubt, leave it and flag it.

Match the document's own terms. Caption names, defined terms, and entity references already in the deliverable take precedence over any generic phrasing here.

## Shared baseline (every module)

Write for a knowledgeable professional. Assume the reader has at least a college-grad level and is familiar with the field, the standards, the methods, and the client. These docs are for other professionals. Give the parameters of the specific situation and stop. Never explain a concept, a standard, or how something works. "Plan matches 50% up to 6%, 3% max," not paragraphs on how matching works. If a knowledgeable reader would skim it as obvious, cut it. The one exception is client-facing material addressed to lay people (see client-facing.md), where you translate terms into plain outcomes.

No AI voice. This is the hardest rule and it applies to every module, client and internal alike. The output should read like a CPA documenting work, not like an AI or a copywriter wrote it. Cut marketing speak, metaphors, drama, and selling. No "this is the crux of the audit," no "the spine of planning," no heightening the stakes or dramatizing the work. State what was done and what it shows. Specifically:

- No em dashes. Use a period or a comma.
- No rule of three cadence ("clear, concise, and compelling"), no parallel triads for rhythm.
- No inflated or marketing words: crucial, essential, vital, robust, comprehensive, seamless, leverage, delve, underscore, showcase. Plain verbs. "Use" not "utilize," "to" not "in order to."
- No throat-clearing: "it's worth noting," "it's important to," "notably." State the thing.
- No metaphors or grand framing ("the spine of the engagement," "the driving cascade," "the crux of the audit").
- No drama. Don't heighten stakes, build tension, or narrate the work as a story. It's a record, not a pitch.
- No selling. Don't pitch the value, importance, or quality of the work, the process, or the firm. "AUD-100 tailors what is in scope," not "AUD-100 is the backbone that powers planning."
- No "-ing" editorial tails ("..., ensuring accuracy"). End at the fact.
- No transition padding (furthermore, moreover, additionally) and no summary restatement (in summary, overall).
- Don't hedge a fact you have. Give the number or the reference, not "significant."

Cold, direct, concise. Say it once, in as few words as carry the meaning.

## Adding a style

Create styles/<name>.md following the structure the existing modules use, then add a menu row. Keep each module to voice and wording, no formatting mechanics. Keep colons out of the description line in frontmatter or the YAML breaks.
