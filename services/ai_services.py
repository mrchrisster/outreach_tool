# services/ai_services.py

import re
import google.generativeai as genai
from config import GEMINI_API_KEY

# Configure the Google Gemini API with the key from config.py
genai.configure(api_key=GEMINI_API_KEY)

def generate_email(first_name, company_name, post_text=None):
    """Generate a personalized email using the Gemini AI model."""
    
    # If there's no LinkedIn post, generate a simpler email
    if post_text:
        prompt = f"Craft a personalized email for {first_name} working at {company_name} based on this LinkedIn post: {post_text}. \
        Be personable and less salesy. Keep it brief."
    else:
        # Simpler email without LinkedIn post
        prompt = f"Craft a personalized email for {first_name} working at {company_name}. \
        Start by mentioning that ... Be personable and less salesy. Keep it brief."

    # Generate content using Gemini AI
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    response = model.generate_content(prompt)
    email_content = response.text

    # Extract the subject line and clean up the email content
    subject, cleaned_email_content = extract_subject_and_clean(email_content)

    return subject, cleaned_email_content

def extract_subject_and_clean(email_content):
    """Extract the subject line and clean up the email content by removing the subject and converting links."""
    # 1. Extract the "Subject: ..." line
    subject_match = re.search(r"Subject: (.*)\n", email_content)
    subject = subject_match.group(1).strip() if subject_match else "No Subject"
    
    # 2. Remove "Subject: ..." line from the body
    email_body = re.sub(r"Subject:.*\n", "", email_content, count=1).strip()

    # 3. Convert Markdown links [text](url) to just the URL
    email_body = re.sub(r"\[.*?\]\((.*?)\)", r"\1", email_body)

    return subject, email_body
