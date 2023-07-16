import os
import pdfplumber
from dotenv import load_dotenv
import openai
import pandas as pd
from collections import defaultdict

# Load .env file
load_dotenv()

# Extract variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
PDF_PASSWORD = os.getenv('PDF_PASSWORD')

# Adjust and run until you've indexed all books individually
book = 1

# Adjust to the name of the course and whatever you want to name the files
PDF_PATH=f'SEC### - Book {book}_####.pdf'
outfile=f'GXXX_Index_Book_{book}.csv'

# Set openai key
openai.api_key = OPENAI_API_KEY

# Initialize the data structure
index = defaultdict(lambda: {'pages': set(), 'definition': ''})

# Open the PDF
with pdfplumber.open(PDF_PATH, password=PDF_PASSWORD) as pdf:
    for i, page in enumerate(pdf.pages):
        text = page.extract_text()

        print(f'prompting for page {i}...\n') # Just to see it's working

        # Prepare the prompt, adjust to meet any preferences in throughness of the index
        prompt = f"I'll be providing you one page from a SANS book at a time, and I want you identify the most important term or concept on the page as it relates to Cloud, Cybsercurity, and Threat Detection, in order to create an index of the book. Some pages may not have an imporant term or phrase at all, especially pages that are just title pages or don't have much content, in these cases just say none. Please ensure the terms are concise, relevant and key to the page's content. Each page should have at most a single term identified. List the term along with a short (5-15) word definition for the term, separated by a comma, with no addittional text. The selected terms should be concrete concepts or succinct phrases of no more than 3-4 words at most, and only if the term is discussed in-depth on that page, and not simply mentioned in passing. Avoid phrases that are complex or overly descriptive, such as 'Logged in during a likely password spray'. Exclude people's names (I.e. Your Name, and the authors of the book), anything about page numbers or licensing, the course title (SECXXX Course Title), and any terms that are too generic or broad. If a term is a MITRE ATT&CK technique, include only the T-code and the short name of the technique, not 'MITRE ATT&CK'. Here is the next page: \n\n{text}"

        # Prompt for an overly thorough index (think 350 terms for 130 pages)
        # I'm providing you pages from a SANS book, one at a time, and I want you to identify only the most essential, concise keywords or terms from each page for inclusion in a SANS index. List one term per line along with a short (5-15 word) definition for the term, the term and definition should be separated by a comma, with no additional text. Please ensure the terms are concise, relevant, and key to the page's content. Remember, a fair number of pages will not have any critical terms - pages like title pages or those with sparse information should have none, and in these cases, simply respond with none. Each content-rich page should have no more than 1-2 pivotal terms. The selected terms should be concrete concepts or succinct phrases of no more than 3-4 words at most, and only if the term is discussed in-depth on that page, and not simply mentioned in passing. Avoid phrases that are complex or overly descriptive, such as 'Logged in during a likely password spray'. Exclude people's names (I.e. Your Name, and the authors of the book), anything about page numbers or licensing, the course title (SECXXX Course Title), and any terms that are too generic or broad. If a term is a MITRE ATT&CK technique, include only the T-code and the short name of the technique, not 'MITRE ATT&CK'. Here is the next page
    
        # Use OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        print(response.choices[0].message['content'])

        # Parse the response
        for line in response.choices[0].message['content'].split('\n'):
            if line and line.lower().replace('.', '') != 'none':
                term, definition = line.split(',', 1) # could add some error handling here if GPT response is not properly formatted, benefit would be you wouldn't lose the current progress, down side is it'll mess up the final CSV
                term = term.strip()
                term = term.replace('"', '')
                term = term.replace("'", '')
                definition = definition.strip()

                index[term]['pages'].add(i-1)  # Math to account for the first 2 pages of the book not counting
                if not index[term]['definition']:
                    index[term]['definition'] = definition

# Convert the data into a pandas DataFrame
df = pd.DataFrame(
    [(term, ', '.join(map(str, sorted(data['pages']))), data['definition']) for term, data in index.items()],
    columns=['Term', 'Pages', 'Definition']
)

# Save it as a CSV
print("converting to CSV...\n")
df.to_csv(outfile, index=False)
