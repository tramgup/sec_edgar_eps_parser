# EDGAR EPS Parser

## Overview

This project addresses parsing and extracting quarterly Earnings Per Share (EPS) data from HTML based financial reports from the SEC's EDGAR database. The parser is designed to reliably extract Basic EPS values from a wide variety of document formats.


---

## Project Objectives

- Parse SEC filings in HTML format
- Extract the Basic EPS for the most recent quarter
- Prefer GAAP EPS over Non-GAAP (adjusted EPS)
- Return output in a structured CSV format
- Generalize across different and unseen formats

---

## Approach

This project uses a **two-stage hybrid parsing system**:

### 1. Traditional Parsing (Rule-Based)
- **HTML table analysis** to detect structured financial tables
- **Regex scanning** for lines referencing EPS, GAAP/Non-GAAP terminology
- **Number normalization** to correctly interpret formats like `(1.23)` -> `-1.23`
- **Context aware confidence scoring** based on:
  - Presence of keywords
  - Table structure
  - Value consistency
  - Reasonable value bounds

### 2. AI-Powered Fallback (LLM with Google Gemini)
If the confidence score from the traditional method falls below a defined threshold (default `0.6`), the system uses an **LLM** (Gemini) to extract EPS from the text. Gemini 2.0 offers free API keys.

#### Why LLMs?
LLMs excel at understanding and interpreting language, especially **human written financial language**, which is often ambiguous or irregular. They offer a semantic understanding that rule based systems lack, making them ideal for extracting structured data from unstructured filings.

---

## Output Format

The parser outputs a CSV file with the following fields:

| filename                       | EPS   |
|-------------------------------|-------|
| 0001564590-20-019726.html     | 0.08  |
| 0000066570-20-000013.html     | 1.12  |
| 0000008947-20-000044.html     | -0.41 |
| 0001564590-20-019431.html     | 1.08  |
| 0001564590-20-019396.html     | -3.15 |

---

## How to Run

- Place your .html filings inside the filings/ directory.
- Run the script: python parser.py
- Output will be saved to output/eps_output.csv

## Requirements

- pip install beautifulsoup4 lxml google-genai


## Notes

- EPS values over 100 or suspicious round values are penalized in confidence scoring.
- The LLM is only triggered when traditional parsing yields low confidence.
    - Only information that is believed to be relevant is fed into the LLM, in order to minimize token use.
-  I included my own personal Gemini API Key so you do not have to provide your own. I understand it is bad security practice, but this is purely for demonstration.