import os
from dotenv import load_dotenv
import re
import csv
from bs4 import BeautifulSoup
from google import genai
from google.genai import types
from typing import Optional, Tuple, List

load_dotenv()  # Load environment variables from .env file


class EPSParser:
    def __init__(self, gemini_api_key: str):
        # Initialize parser with Gemini API key.
        self.client = genai.Client(api_key=gemini_api_key)
        
        # Regex for numbers like 1.23, (4.56), $2.34, 1,234.56
        self.NUM_RE = re.compile(r'\(?\$?\s*\d{1,3}(?:,\d{3})*(?:\.\d{2,4})?\s*\)?')

    def clean_number(self, num_str: str) -> Optional[float]:
        # Convert number string to float, handling negatives. Formatting
        try:
            clean = re.sub(r'[\$\s]', '', num_str)
            if clean.startswith('(') and clean.endswith(')'):
                clean = '-' + clean[1:-1]
            clean = clean.replace(',', '')
            return float(clean)
        except:
            return None

    def extract_numbers(self, text: str) -> List[float]:
        # Get all numbers from text, filtering out those >= 1000.
        numbers = []
        for match in self.NUM_RE.finditer(text):
            num = self.clean_number(match.group())
            if num is not None and abs(num) < 1000:
                numbers.append(num)
        return numbers

    def find_eps_in_table(self, table) -> Optional[float]:
        # Find EPS in a table element. Will be called when searching for EPS in HTML tables.
        eps_words = ["earnings", "per", "share", "eps"]
        basic_words = ["basic", "basic eps"]
        
        table_text = table.get_text().lower()
        if not any(word in table_text for word in eps_words):
            return None
        
        for tr in table.find_all('tr'):
            cells = tr.find_all(['th', 'td'])
            if not cells:
                continue
            first_cell = cells[0].get_text(strip=True).lower()
            if any(word in first_cell for word in basic_words):
                row_text = " ".join(c.get_text(strip=True) for c in cells[1:])
                numbers = self.extract_numbers(row_text)
                if numbers:
                    return numbers[0]
        return None

    def calculate_confidence(self, eps_value: Optional[float], extraction_context: dict) -> float:
        # Confidence score for each EPS value, low scores will then trigger AI call in order to find actual EPS.
        if eps_value is None:
            return 0.0
        confidence = 0.0

        #Table based extraction is more reliable
        if extraction_context.get('found_in_table', False):
            confidence += 0.4

        #If EPS keywords detected, it is more likely to be correct
        if extraction_context.get('clear_eps_keywords', False):
            confidence += 0.3

        # Table has "standard" structure, dummy value that adds more confidence
        if extraction_context.get('standard_structure', False):
            confidence += 0.2

        # If multiple consistent values found, it adds confidence
        if extraction_context.get('consistent_values', 0) > 1:
            confidence += 0.1

        #Sanity Checks - These reduce confidence score
        if -50 <= eps_value <= 50:
            confidence += 0.1
        else:
            confidence -= 0.4

        # Very suspicious high, or round numbers that are likely wrong
        suspicious_values = [99.0, 100.0, 200.0, 202.0, 300.0, 500.0, 548.0, 999.0, 1000.0]
        if eps_value in suspicious_values or eps_value > 100:
            confidence -= 0.5
        if abs(eps_value) > 100:
            confidence -= 0.3
        if eps_value > 10 and eps_value == int(eps_value):
            confidence -= 0.2
        return min(1.0, max(0.0, confidence))

    def extract_with_traditional_methods(self, html_path: str) -> Tuple[Optional[float], dict]:
        # First layer of extraction using table parsing and regex
        try:
            with open(html_path, encoding='utf-8', errors='ignore') as f:
                soup = BeautifulSoup(f, 'lxml')
        except:
            return None, {}
        context = {
            'found_in_table': False,
            'clear_eps_keywords': False,
            'standard_structure': False,
            'consistent_values': 0
        }
        candidates = []
        # Search for EPS in tables first
        for table in soup.find_all('table'):
            eps = self.find_eps_in_table(table)
            if eps is not None:
                candidates.append(eps)
                context['found_in_table'] = True
                context['clear_eps_keywords'] = True
                context['standard_structure'] = True

        # Fallback to text extraction if no candidates found in tables
        text = soup.get_text()
        for line in text.split('\n'):
            line_lower = line.lower()
            if "per share" in line_lower or "eps" in line_lower:
                context['clear_eps_keywords'] = True
                numbers = self.extract_numbers(line)
                if numbers:
                    candidates.extend(numbers)
        patterns = [
            r'Basic\s+earnings\s+per\s+share[:\s]+\$?\s*([\d,.-]+)',
            r'Basic\s+EPS[:\s]+\$?\s*([\d,.-]+)',
        ]
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                eps = self.clean_number(match)
                if eps is not None:
                    candidates.append(eps)

        # Calculate length of consistent values
        if candidates:
            context['consistent_values'] = len(set(candidates))
            return candidates[0], context
        return None, context

    def extract_with_ai(self, html_path: str) -> Optional[float]:
        # Fallback method using Gemini AI to extract EPS from HTML content. Second Layer. Triggered if traditional has low confidence.
        try:
            with open(html_path, encoding='utf-8', errors='ignore') as f:
                soup = BeautifulSoup(f, 'lxml')

            text = soup.get_text()

            lines = text.split('\n')
            relevant_lines = []

            #looking for keywords in text to find relevant lines
            for i, line in enumerate(lines):
                line_lower = line.lower()
                if any(keyword in line_lower for keyword in [
                    'income statement', 'earnings', 'per share', 'eps',
                    'basic earnings', 'diluted earnings', 'net income','share','per common share'
                ]):
                    # Collect lines around the keyword for context, helps LLM understand whats happening.
                    start = max(0, i - 10)
                    end = min(len(lines), i + 10)
                    relevant_lines.extend(lines[start:end])
                    
            # If no relevant lines found, use first 200 lines as fallback
            if not relevant_lines:
                relevant_lines = lines[:200]

            relevant_text = '\n'.join(relevant_lines[:500])

            prompt = f"""
            You are analyzing a financial document (SEC filing) to extract the Basic Earnings Per Share (EPS) for the most recent quarter.

            Important rules:
            1. Look for "Basic" EPS, not "Diluted" EPS
            2. Prefer GAAP over Non-GAAP (adjusted) EPS
            3. If multiple quarters are shown, extract the most recent one
            4. Numbers in parentheses like (1.23) represent negative values: -1.23
            5. Return only the numerical value as a decimal (e.g., 1.23 or -0.45)
            6. If no EPS found, return "NOT_FOUND"

            Document text:
            {relevant_text}

            Extract the Basic EPS value:
            """
            print("Calling Gemini API...")
            response = self.client.models.generate_content(
                model="gemini-2.0-flash",
                config=types.GenerateContentConfig(
                    system_instruction="You are a financial document analyst. Extract earnings per share data accurately from SEC filings."
                ),
                contents=prompt
            )
            if response and response.text:
                result = response.text.strip()
                print(f"AI raw response: '{result}'")
                if result == "NOT_FOUND":
                    return None
                
                # Attempt to parse the result as a float
                try:
                    parsed_value = float(result)
                    print(f"AI parsed value: {parsed_value}")
                    return parsed_value
                except ValueError:
                    print(f"Could not parse '{result}' as float, trying to extract numbers...")
                    # Trying to make sure a number is only output from llm response, bc sometimes it outputs text.
                    numbers = self.extract_numbers(result)
                    if numbers:
                        print(f"Extracted number from AI response: {numbers[0]}")
                        return numbers[0]
                    else:
                        print("No numbers found in AI response")
                        return None
            else:
                print("Empty or no response from AI")
                return None
        except Exception as e:
            print(f"AI extraction error for {html_path}: {e}")
            import traceback; traceback.print_exc()
            return None

    def parse_eps_from_html(self, html_path: str, confidence_threshold: float = 0.6) -> Optional[float]:
        # Main method to parse EPS from HTML file, using traditional methods first, then AI if needed.
        
        # Step 1: Tradtional methods using table and regex
        eps_traditional, context = self.extract_with_traditional_methods(html_path)

        # Step 2: Calculate confidence based on step 1 results
        confidence = self.calculate_confidence(eps_traditional, context)

        print(f"Traditional method: EPS={eps_traditional}, Confidence={confidence:.2f}")

        # Step 3: Use AI if confidence is low
        if confidence < confidence_threshold:
            print("Low confidence, trying AI extraction...")
            eps_ai = self.extract_with_ai(html_path)
            if eps_ai is not None:
                print(f"AI method: EPS={eps_ai}")
                return eps_ai
            else:
                print("AI extraction failed, using traditional result")
        return eps_traditional

    def process_directory(self, input_dir: str, output_csv: str, confidence_threshold: float = 0.6):
        # Processes html files and writes results to a CSV file.

        html_files = sorted([f for f in os.listdir(input_dir) if f.lower().endswith('.html')])
        os.makedirs(os.path.dirname(output_csv), exist_ok=True)
        with open(output_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["filename", "EPS"])
            for filename in html_files:
                print(f"\nProcessing {filename}...")
                path = os.path.join(input_dir, filename)
                eps = self.parse_eps_from_html(path, confidence_threshold)
                if eps is not None:
                    writer.writerow([filename, f"{eps:.2f}"])
                    print(f"{filename}: {eps:.2f}")
                else:
                    writer.writerow([filename, ""])
                    print(f"{filename}: not found")


def main():
    # Configuration - update these paths and your Gemini API key below
    input_dir = "filings"
    output_csv = "output/eps_output.csv"
    
    api_key = os.getenv("GEMINI_API_KEY")
    threshold = 0.6

    eps_parser = EPSParser(api_key)
    eps_parser.process_directory(input_dir, output_csv, threshold)


if __name__ == "__main__":
    main()
