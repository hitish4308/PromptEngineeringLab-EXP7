# Prompt Engineering Lab - Experiment 7

## Constraint Specification and Iterative Refinement

Demonstrates how constraint compliance improves when prompts are
refined with examples and clearer phrasing.

## Task

Generate a short description of a smartwatch (max 60 words) under three
constraints:

1. Exactly 3 bullet points
2. Each bullet point starts with a verb
3. No use of the word "smart" anywhere

## Method

| Stage | Prompt Style |
|-------|--------------|
| Initial | Plain prose constraints |
| Refined | Numbered constraints + explicit example + renamed product ("fitness watch") |

The script checks each response programmatically for:

- Bullet count (exactly 3)
- First word of each bullet is a verb (heuristic: ends with 's')
- The word "smart" is absent
- Total word count ≤ 60

## Model and Parameters

- Model: openai/gpt-oss-20b
- Temperature: 0.5
- Max tokens: 300

## Setup

Reuse the environment from Experiment 1:

    Copy-Item ..\EXP_1\.env .
    python -m pip install -r requirements.txt

## Run

    python constraint_refine.py

## Expected Output

- Initial prompt + response + violation report
- Refined prompt + response + violation report
- A before/after comparison table
- A summary of findings

## Key Findings

- Ambiguous constraints produce inconsistent output
- Renaming the product removes the temptation to use the banned word
- Providing an example anchors format, style, and verb choice
- Numbering constraints and using "MUST" / "Do NOT" makes them emphatic
- Programmatic checks catch violations that humans miss

## Security

- Never commit .env
- Never paste API keys in chat, logs, or screenshots

## License

For educational / lab use only.
