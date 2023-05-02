import openai
import os
from dotenv import load_dotenv
import csv
import yaml
import requests

load_dotenv()

# Get OpenAI API key
api_key = os.getenv("OPENAI_API_KEY")
unsplash_access_key = os.getenv("UNSPLASH_ACCESS_KEY")

# Authenticate with OpenAI API key
openai.api_key = api_key

if not os.path.exists('output'):
    os.makedirs('output')

# Load prompts
with open('prompts.yml') as f:
    prompts = yaml.safe_load(f)

# Load file info
with open('file_info.csv', newline='') as f:
    reader = csv.DictReader(f)
    file_info = [row for row in reader]

# Load template
with open('template.md') as f:
    template = f.read()

# Generate content for a given prompt
def generate_content(prompt):
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        temperature=0.7,
        max_tokens=1024,
        n=1,
        stop=None,
        frequency_penalty=0,
        presence_penalty=0
    )
    return response.choices[0].text.strip()

# Fetch an image from Unsplash based on the topic
def fetch_unsplash_image(topic):
    response = requests.get(f"https://api.unsplash.com/search/photos?query={topic}&client_id={unsplash_access_key}")
    data = response.json()
    if data['results']:
        return data['results'][0]['urls']['regular'], data['results'][0]['user']['links']['html']
    else:
        return None, None

# Loop over pages and generate output
for page in file_info:
    # Generate output for current page
    progress_made = generate_content(prompts['Progress Made']['prompt'].replace('{Topic}', page['Topic']))
    lessons_learned = generate_content(prompts['Lessons Learned']['prompt'].replace('{Topic}', page['Topic']))
    challenges_ahead = generate_content(prompts['Challenges Ahead']['prompt'].replace('{Topic}', page['Topic']))
    best_path_forward = generate_content(prompts['Best Path Forward']['prompt'].replace('{Topic}', page['Topic']))

    # Fetch an image from Unsplash
    image_url, credit_url = fetch_unsplash_image(page['Topic'])

    # Populate the template with the generated content and image URL
    output = template.format(
        topic=page['Topic'],
        progress_made=progress_made,
        lessons_learned=lessons_learned,
        challenges_ahead=challenges_ahead,
        best_path_forward=best_path_forward,
        image_url=image_url or '',
        credit_url=credit_url or ''
    )

    # Write output to file
    with open(f"output/{page['File Name']}", 'w') as f:
        f.write(output)
