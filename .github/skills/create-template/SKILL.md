---
name: create-template
description: "Create a new JSON template file for the Simple File Helper document converter. Use when: adding a new document type (bank statement, clearance log, invoice, etc.), defining Gemini extraction columns and prompts, or setting up summary metrics. Triggers: new template, add template, create template, document type, bank statement template."
---

# Create Template

## Overview

Templates define how Gemini extracts data from uploaded documents. Each template is a `.json` file in `backend/templates/` and is loaded into memory at server startup. This skill guides the creation of a complete, validated template.

## Workflow

### 1. Gather Requirements

Ask the user:

- **What type of document?** (bank statement, clearance log, invoice, etc.)
- **What columns should be extracted?** List each field with its data type (string or number).
- **What summary metrics?** (e.g., total amount, count of transactions)
- **Do they have a sample file?** If yes, examine it to determine realistic column names, date formats, and edge cases.

### 2. Build the Gemini Prompt

Write a prompt that:

- Starts with a role: "You are an expert [domain] parser."
- Instructs Gemini to extract ALL rows — never truncate or omit.
- Lists every field to extract with type hints: `field_name (the data type, any formatting notes)`.
- Ends with: "Return ONLY a valid JSON array with no other text. Do not wrap in markdown fences."

### 3. Define Columns

For each column, specify:

```json
{ "key": "snake_case_key", "label": "Human-Readable Header", "type": "string|number", "width": 14 }
```

- `key`: matches the field name in the Gemini prompt (snake_case)
- `label`: Excel column header — clear, human-readable
- `type`: `"string"` or `"number"` — determines Excel formatting
- `width`: approximate character width for column auto-fit

### 4. Define Summary Metrics

Each metric in the `summary_metrics` array:

```json
{ "label": "Total Amount", "column": "amount_key", "agg": "sum|count|avg|min|max" }
```

- `column`: must match a column `key`
- `agg`: only `"sum"` and `"count"` are supported in v1

### 5. Assemble the JSON File

Full template structure (see existing templates in `backend/templates/`):

```json
{
  "name": "Human-Readable Template Name",
  "category": "lowercase_snake_case",
  "icon": "tabler-icon-name",
  "description": "One-line description shown in the UI sidebar.",
  "gemini_prompt": "You are an expert... Return ONLY a valid JSON array...",
  "columns": [ ... ],
  "summary_metrics": [ ... ]
}
```

**Categories** use lowercase_snake_case: `bank_statement`, `bank_clearance`, `invoice`, etc.

**Icons** are [Tabler Icons](https://tabler.io/icons) names. Common choices: `building-bank`, `file-invoice`, `file-check`, `file-spreadsheet`, `receipt`, `report`.

### 6. Save and Validate

- Save to `backend/templates/<snake_case_name>.json`
- The filename stem becomes the template key (e.g., `transaction_status_inquiry`)
- Verify JSON is valid — no trailing commas, all required fields present
- Restart the server to load the new template

## Validation Checklist

After creating, confirm:

- [ ] `name` is human-readable
- [ ] `category` is lowercase_snake_case
- [ ] `icon` is a valid Tabler icon name
- [ ] `gemini_prompt` includes "Return ONLY a valid JSON array"
- [ ] Every `columns[].key` appears in the Gemini prompt
- [ ] Every `summary_metrics[].column` matches a `columns[].key`
- [ ] JSON parses without errors
- [ ] File is in `backend/templates/` with `.json` extension

## Reference

See `backend/templates/transaction_status_inquiry.json` for a complete working example.
