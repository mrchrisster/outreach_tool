from services.linkedin_services import authenticate_linkedin, search_person, find_profiles_in_mining, send_linkedin_message
from services.ai_services import generate_email
from services.google_services import create_draft, send_email, update_sheet_with_contact_info
from config import SHEET_ID

def process_contact(index, rows, st):
    """Process the contact information from the Google Sheets."""
    if index >= len(rows):
        st.write("No more contacts to process.")
        return

    first_row = rows[index]
    first_name = first_row[0] if len(first_row) > 0 else None
    recipient_email = first_row[4] if len(first_row) > 4 else None
    company_name = first_row[2] if len(first_row) > 2 else None

    # Ensure we have a valid name
    if not first_name:
        st.write("Name is missing from the Google Sheet.")
        return

    # Store recipient email in session state
    st.session_state.recipient_email = recipient_email

    st.write(f"**Name:** {first_name}")
    if company_name:
        st.write(f"**Company:** {company_name}")
    else:
        st.write("Company name is missing from the Google Sheet.")
    if recipient_email:
        st.write(f"**Recipient Email:** {recipient_email}")
    else:
        st.write("Recipient email is missing from the Google Sheet.")

    # Authenticate with LinkedIn
    linkedin_api = authenticate_linkedin()

    # Perform LinkedIn search with name and company
    search_results = search_person(linkedin_api, first_name, company_name)

    profile = None  # Initialize profile

    if not search_results:
        st.write("Person not found in LinkedIn search results with the specified company.")

        # Perform a broader search by name only
        search_results = search_person(linkedin_api, first_name)

        if not search_results:
            st.write("Person not found in LinkedIn search results by name. Generating fallback email.")

            # Generate fallback email without LinkedIn post
            subject, email_content = generate_email(first_name, company_name, None)

            # Store generated email content in session state
            st.session_state.email_content = email_content
            st.session_state.subject = subject

            # Display fallback email content (no "Send Email" button here)
            st.text_area("Generated Email:", value=email_content, height=300, key='fallback_email_editor')

            return  # Return after displaying the fallback email
        else:
            # Filter results by mining companies
            mining_profiles = find_profiles_in_mining(linkedin_api, search_results)

            if not mining_profiles:
                st.write("No profiles found with past companies in the mining industry. Generating fallback email.")

                # Generate fallback email without LinkedIn post
                subject, email_content = generate_email(first_name, company_name, None)

                # Store generated email content in session state
                st.session_state.email_content = email_content
                st.session_state.subject = subject

                st.text_area("Generated Email:", value=email_content, height=300, key='fallback_email_editor')

                return  # Return after displaying the fallback email
            else:
                profile = mining_profiles[0]
    else:
        # If initial search with name and company found the person
        profile = search_results[0]

    st.session_state.profile = profile  # Store profile in session state

    urn_id = profile.get('urn_id')
    if urn_id:
        posts = linkedin_api.get_profile_posts(urn_id=urn_id, post_count=1)

        if posts:
            most_recent_post = posts[0]
            post_text = most_recent_post.get('commentary', {}).get('text', {}).get('text', 'No post content available.')
            st.session_state.post_text = post_text
            st.write(f"**Most Recent Post Text:**\n{post_text}")

            # Generate a personalized email using Gemini AI
            subject, email_content = generate_email(first_name, company_name, post_text)
            st.session_state.email_content = email_content  # Store generated email content
            st.session_state.subject = subject  # Store subject in session state

            # Display the subject and email content, allowing users to edit
            st.text_input("Edit Subject Line:", value=st.session_state.subject, key='subject_editor', on_change=lambda: update_subject(st))
            st.text_area("Edit the email below:", value=email_content, height=300, key='email_editor')
        else:
            st.write("No posts found for this profile.")
    else:
        st.write("No urn_id found for the profile.")


def update_subject(st):
    """Update the subject line in session state."""
    st.session_state.subject = st.session_state.subject_editor


def regenerate_email(st, rows):
    """Regenerate the email using AI and updated information."""
    first_row = rows[st.session_state.current_index]
    first_name = first_row[0] if len(first_row) > 0 else None
    company_name = first_row[2] if len(first_row) > 2 else None
    post_text = st.session_state.post_text

    if first_name and post_text:
        # Generate a personalized email using Gemini AI
        subject, email_content = generate_email(first_name, company_name, post_text)
        st.session_state.email_content = email_content
        st.session_state.subject = subject
        st.text_input("Edit Subject Line:", value=st.session_state.subject, key='subject_editor', on_change=lambda: update_subject(st))
        st.text_area("Edit the email below:", value=st.session_state.email_content, height=300, key='email_editor')


def next_contact(st):
    """Move to the next contact in the list."""
    st.session_state.current_index += 1
    st.session_state.email_content = ''
    st.session_state.post_text = ''
    st.session_state.profile = None
    st.session_state.subject = ''


def save_to_drafts(st, rows):
    """Save the generated email to Gmail drafts."""
    recipient_email = st.session_state.get('recipient_email')  # Get from session state
    subject = st.session_state.get('subject')  # Get from session state
    body = st.session_state.get('email_content')  # Get from session state

    if recipient_email and body:
        draft_response = create_draft(subject, body, recipient_email)
        if draft_response:
            st.success("Email saved to drafts successfully.")
        else:
            st.error("Failed to save email to drafts.")
    else:
        st.error("Recipient email or email content is missing.")


def send_email_action(st, rows):
    """Send the generated email via Gmail and update Google Sheets."""
    recipient_email = st.session_state.get('recipient_email')  # Get from session state
    subject = st.session_state.get('subject')  # Get from session state
    body = st.session_state.get('email_content')  # Get from session state
    row_number = st.session_state.current_index + 2  # Adjust for header row

    if recipient_email and body:
        # Implement the logic to send the email here
        email_response = send_email(subject, body, recipient_email)
        if email_response:
            st.success("Email sent successfully.")
            
            # Update the sheet to indicate the contact method and message
            update_sheet_with_contact_info(SHEET_ID, row_number, "Email", body)
        else:
            st.error("Failed to send email.")
    else:
        st.error("Recipient email or email content is missing.")


def send_linkedin_message_action(st, rows):
    """Send the generated message via LinkedIn and update Google Sheets."""
    first_row = rows[st.session_state.current_index]
    first_name = first_row[0] if len(first_row) > 0 else None
    company_name = first_row[2] if len(first_row) > 2 else None
    row_number = st.session_state.current_index + 2  # Adjust for header row

    linkedin_api = authenticate_linkedin()

    # Perform LinkedIn search with name and company
    search_results = search_person(linkedin_api, first_name, company_name)
    
    if search_results:
        st.write(f"Found LinkedIn profile for {first_name} at {company_name}.")
        profile = search_results[0]
        urn_id = profile.get('urn_id')

        # Generate an email with LinkedIn post if available
        post_text = st.session_state.post_text if st.session_state.post_text else None
        subject, email_content = generate_email(first_name, company_name, post_text)

        st.text_area("Generated Email:", value=email_content, height=300, key='email_editor')

        if st.button("Send Email"):
            send_email_action(st, rows)
        if urn_id and st.button("Send via LinkedIn"):
            response = send_linkedin_message(linkedin_api, urn_id, email_content)
            if response:
                st.success("Message sent via LinkedIn successfully.")
            else:
                st.error("Failed to send message via LinkedIn.")
    else:
        # Log and confirm no person was found by company
        st.write(f"Person not found in LinkedIn search results for {first_name} at {company_name}.")

        # Generate fallback email without LinkedIn post
        subject, email_content = generate_email(first_name, company_name, None)

        # Store fallback email content in session state
        st.session_state.email_content = email_content
        st.session_state.subject = subject

        # Display fallback email
        st.text_area("Generated Email:", value=email_content, height=300, key='email_editor')

        if st.button("Send Email"):
            send_email_action(st, rows)


def jump_to_line(st, rows):
    """Jump to the selected line in the list."""
    try:
        # Check for manual input first, otherwise use the dropdown value
        if st.session_state.jump_to_line_manual != '':
            target_index = int(st.session_state.jump_to_line_manual) - 1  # Adjusted index
        else:
            target_index = int(st.session_state.jump_to_line) - 1

        if target_index < 0 or target_index >= len(rows):
            st.error("Invalid line number. Please enter a valid number.")
        else:
            st.session_state.current_index = target_index
            st.experimental_set_query_params(jump=str(target_index))  
    except ValueError:
        st.error("Please enter a valid number.")
