# Langflow workflow: Finance & HR Smart Data Analyst

`finance_hr_data_analyst_mcp_flow.json` is a Langflow **1.9.6** flow built for
a Finance / HR / Admin leader (GST, IND-AS, FEMA, SEZ, Transfer Pricing,
Payroll, MIS Reporting) to run natural-language data analysis over the
Pandas Excel Analytics MCP server, using a free OpenRouter LLM as the
reasoning agent.

## What's in the flow

```
Chat Input ─────────────────┐
                             ▼
Finance & HR System Prompt ─► Agent (OpenRouter, free model) ─► Chat Output
                             ▲
MCP Tools (Pandas-Excel-EDA)─┘  (Tools port — all 27 tools)
```

- **Chat Input / Output** — the conversational front end.
- **Finance & HR System Prompt** — a domain-tuned instruction set that tells
  the agent how to use `upload_dataset`, `eda_report`, `data_quality_report`,
  `group_by`, `pivot_table`, `outlier_analysis`, `excel_chart`, `export_*`,
  etc., framed around budgets, payroll, GST, and MIS reporting.
- **MCP Tools** — connects to your deployed
  `https://YOUR-SERVICE.onrender.com/mcp` and exposes all 27 tools as a
  Toolset.
- **Agent** — set to a **Custom / OpenAI-compatible** provider pointed at
  `https://openrouter.ai/api/v1`, so any free OpenRouter model works
  (`meta-llama/llama-3.1-8b-instruct:free`,
  `google/gemini-2.0-flash-exp:free`, `qwen/qwen-2.5-72b-instruct:free`, etc).

## Import it

1. Langflow → **Projects** → **Upload a flow** (or drag the JSON file onto
   the canvas).
2. Open the **MCP Tools** node and replace the placeholder URL
   `https://YOUR-SERVICE.onrender.com/mcp` with your real Render URL.
3. Open the **Agent** node and set the model name to whichever free
   OpenRouter model you have access to.

## Set your API keys as Global Variables (don't paste them into nodes)

Settings → **Global Variables** → add:

| Name | Value | Used by |
|---|---|---|
| `OPENROUTER_API_KEY` | your OpenRouter key | Agent node |
| `MCP_API_TOKEN` | your Render `MCP_API_TOKEN` | MCP Tools node header |

The flow references these as `${OPENROUTER_API_KEY}` / `${MCP_API_TOKEN}` —
Langflow resolves them at run time so the raw keys never live inside the
exported JSON.

## Try it

In the Playground, ask things like:
- *"Upload payroll_march.xlsx and run a data quality report."*
- *"Group expenses by cost center and show total vs budget."*
- *"Build a pivot table of GST input credit by vendor and month, then export it to Excel with a chart."*
- *"Flag outlier transactions in the ledger using IQR."*

## Notes on compatibility

Langflow's exact JSON field names shift slightly between minor versions.
This file was hand-built against the documented 1.9.x `Agent` and
`MCP Tools` component parameters. If any dropdown (Model Provider, Tool)
shows blank after import, just re-select the value from the dropdown once —
Langflow will repopulate the underlying field correctly. If you'd rather
build the same flow from a blank canvas, use the diagram above as the
wiring guide.

## Adding embeddings / RAG later (optional, phase 2)

You mentioned you also have OpenRouter embedding-model access. This flow
intentionally does **not** wire embeddings in yet — see the main
[README's "Future: embeddings / RAG"](../README.md#how-to-connect-it-further)
section. A natural next add-on: load a short Finance & HR glossary
(GST, IND-AS, FEMA, SEZ, Transfer Pricing definitions) into a Chroma vector
store via an OpenRouter-compatible embeddings component, and give the Agent
a second tool for terminology lookup — useful when the agent explains
results to non-finance stakeholders.
