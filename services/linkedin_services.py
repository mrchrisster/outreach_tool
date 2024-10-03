# services/linkedin_services.py

from linkedin_api import Linkedin
from config import LINKEDIN_USERNAME, LINKEDIN_PASSWORD

def authenticate_linkedin():
    """Authenticate with LinkedIn API."""
    linkedin_api = Linkedin(LINKEDIN_USERNAME, LINKEDIN_PASSWORD)
    return linkedin_api

def search_person(linkedin_api, first_name, company_name=None):
    """Search for a person on LinkedIn."""
    query = first_name
    if company_name:
        query += f' {company_name}'
    search_results = linkedin_api.search_people(query)
    return search_results

def find_profiles_in_mining(linkedin_api, search_results):
    """Filter profiles that have experience in mining companies."""
    mining_profiles = []
    for profile in search_results:
        profile_urn = profile.get('urn_id')
        profile_detail = linkedin_api.get_profile(profile_urn)
        experiences = profile_detail.get('experience', [])
        for exp in experiences:
            company = exp.get('companyName', '').lower()
            if 'mining' in company:
                mining_profiles.append(profile)
                break
    return mining_profiles


def send_linkedin_message(linkedin_api, urn_id, message):
    """Send a LinkedIn message to a specific user and print the response for debugging."""
    try:
        # Send the message using LinkedIn's API
        response = linkedin_api.send_message(message_body=message, recipients=[urn_id])
        
        if response:
            print(f"Message sent successfully to URN ID: {urn_id}")
        else:
            print(f"Failed to send message to URN ID: {urn_id}")
        
        # Print the actual response for debugging purposes
        print(f"LinkedIn API Response: {response}")
        return response
    except Exception as error:
        print(f"An error occurred while sending the LinkedIn message: {error}")
        return False  # Return False if there is an error
