# EPS Parser - EDGAR SEC Filings

This project parses EPS (Earnings Per Share) values from 8-K filings provided by the SEC’s EDGAR database. It extracts the most recent quarterly EPS for each filing and outputs the results in a CSV file.

## Overview

The EDGAR database contains complex, inconsistently formatted financial documents. To accurately extract EPS data, this parser leverages Google’s Gemini large language model (LLM), which is better at understanding and interpreting human like text patterns compared to traditional regex based methods.

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
If the confidence score from the traditional method falls below a defined threshold (default `0.6`), the system uses an **LLM** (Gemini) to extract EPS from the text. Google offers free Gemini 2.0 API keys. You can create one using the following url https://aistudio.google.com/app/apikey.

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

- Clone this repository
- Place your .html filings inside the filings/ directory.
- Input your Gemini API Key.
- Run the script: python parser.py
- Output will be saved to output/eps_output.csv

## Requirements

- pip install beautifulsoup4 lxml google-genai python- dotenv


## Notes

- EPS values over 100 or suspicious round values are penalized in confidence scoring.
- The LLM is only triggered when traditional parsing yields low confidence.
    - Only information that is believed to be relevant is fed into the LLM, in order to minimize token use.
- A few sample EDGAR Filings are provided, more can be found here https://www.sec.gov/search-filings
- It is best to store your Gemini API key as an environment variable.