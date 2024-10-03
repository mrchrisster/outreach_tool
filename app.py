import streamlit as st
from config import SHEET_ID, RANGE_NAME
from services.google_services import fetch_sheet_data
from utils.contact_controller import (
    process_contact, regenerate_email, next_contact, jump_to_line,
    save_to_drafts, send_email_action, send_linkedin_message_action
)
from utils.session_state import init_session_state

# Initialize session state variables
init_session_state(st)

# Fetch data from Google Sheets
rows = fetch_sheet_data(SHEET_ID, RANGE_NAME)

# Display the logo and the tool title side by side
col1, col2, col3 = st.columns([1, 3, 1])  # Adjusted for centering
with col1:
    st.image(
        "https://images.squarespace-cdn.com/content/v1/5d03f6bf049c4e00015b368f/1560542723365-85ABCFQ20D7OHCE0YPC0/WEB+LOGO+-+1-02.png?format=750w",
        width=150  # Adjust width as needed
    )
with col2:
    # Centered tool title
    st.markdown(
        "<h3 style='text-align: center; padding-top: 40px;'>Mining Outreach Automation</h3>",
        unsafe_allow_html=True
    )

# Add a separator below the title and logo
st.divider()

# Main app logic
if st.session_state.cancelled:
    st.write("Processing has been cancelled.")
else:
    # Process the current contact
    process_contact(st.session_state.current_index, rows, st)

    # Button section for actions
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        if st.button("Try Again", key='try_again'):
            regenerate_email(st, rows)
    with col2:
        if st.button("Save to Drafts", key='save_to_drafts'):
            save_to_drafts(st, rows)
    with col3:
        if st.button("Send Email", key='send_email'):
            send_email_action(st, rows)  # "Send Email" button now only exists here
    with col4:
        # Only show "Send via LinkedIn" if a valid LinkedIn profile (urn_id) exists
        if 'profile' in st.session_state and st.session_state.profile and st.session_state.profile.get('urn_id'):
            if st.button("Send via LinkedIn", key='send_linkedin'):
                send_linkedin_message_action(st, rows)
    with col5:
        if st.button("Next", key='next_contact'):
            next_contact(st)

    # Jump to line at the bottom, in one line
    col_jump1, col_jump2, col_jump3 = st.columns([1, 1, 2])

    with col_jump1:
        st.write("Jump to:")
    with col_jump2:
        st.selectbox("", list(range(1, len(rows) + 1)), key='jump_to_line', on_change=lambda: jump_to_line(st, rows))
    with col_jump3:
        st.text_input("Or enter line:", key='jump_to_line_manual', on_change=lambda: jump_to_line(st, rows))
