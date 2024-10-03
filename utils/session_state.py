# utils/session_state.py

def init_session_state(st):
    if 'current_index' not in st.session_state:
        st.session_state.current_index = 0
    if 'email_content' not in st.session_state:
        st.session_state.email_content = ''
    if 'post_text' not in st.session_state:
        st.session_state.post_text = ''
    if 'profile' not in st.session_state:
        st.session_state.profile = None
    if 'cancelled' not in st.session_state:
        st.session_state.cancelled = False
    if 'subject' not in st.session_state:
        st.session_state.subject = ''
    if 'jump_to_line' not in st.session_state:
        st.session_state.jump_to_line = 1
    if 'jump_to_line_manual' not in st.session_state:
        st.session_state.jump_to_line_manual = ''
