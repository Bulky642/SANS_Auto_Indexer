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
PDF_PATH = f'FOR610-book1.pdf'
outfile = f'FOR610_Index_Book_{book}.csv'

# Set openai key
openai.api_key = OPENAI_API_KEY

# Initialize the data structure
index = defaultdict(lambda: {'pages': set(), 'definition': ''})

# Open the PDF
with pdfplumber.open(PDF_PATH, password=PDF_PASSWORD) as pdf:
    for i, page in enumerate(pdf.pages):
        text = page.extract_text()

        print(f'prompting for page {i}...\n')  # Just to see it's working

        # Prepare the prompt
        prompt = f"I'll be providing you one page from a SANS book at a time, and I want you identify the most important term or concept on the page as it relates to Malware analysis, the different phases of Malware analysis (static, behavioral, automated and code analysis) and how to analyse in order to create an index of the book. Some pages may not have an imporant term or phrase at all, especially pages that are just title pages or don't have much content, in these cases just say none. Please ensure the terms are concise, relevant and key to the page's content. Each page should have at most a single term identified. List the term along with a short (5-15) word definition for the term, separated by a comma, with no addittional text. The selected terms should be concrete concepts or succinct phrases of no more than 3-4 words at most, and only if the term is discussed in-depth on that page, and not simply mentioned in passing. Avoid phrases that are complex or overly descriptive, such as 'Logged in during a likely password spray'. Exclude people's names (I.e. student, and the authors of the book), anything about page numbers or licensing, the course title (FOR610 Reverse-Engineering Malware), and any terms that are too generic or broad. If a term is a API pattern for recognizing malware, put this in a separate .csv file and export this ones all books, 5 in total are processed.: \n\n{text}"

        # Use OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        print(response.choices[0].message['content'])

        # Parse the response
        for line in response.choices[0].message['content'].split('\n'):
            if line and line.lower().replace('.', '') != 'none':
                # Check if the line contains a comma before attempting to split
                if ',' in line:
                    term, definition = line.split(',', 1)
                else:
                    term = line.strip()
                    definition = "No definition provided"  # Default value

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
