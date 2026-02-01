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

- This app is hosted online via Railway and can be accessed using this address https://sec-parser.up.railway.app/
- You can download SEC 8-K/10-K fillings via the Edgar database using this link https://www.sec.gov/search-filings

#### If you wish to run this locally follow the steps below
- Run both the frontend and backend. Frontend: npm run dev  Backend: python3 app.py
- Be sure to upload your own personal Gemini API key and configure the model you wish to use.
- Use the interactive UI to select which .html files you wish to upload.
- Outputs will be displayed in a table format and an option to download your results in a csv format.

## Requirements

- pip install -r requirements.txt


## Notes

- EPS values over 100 or suspicious round values are penalized in confidence scoring.
- The LLM is only triggered when traditional parsing yields low confidence.
    - Only information that is believed to be relevant is fed into the LLM, in order to minimize token use.
- Use these values at your own risk. From my own personal experience, this system is accurate more than 95% of the time. Feel free to edit the parser file to fit your own personal needs.
