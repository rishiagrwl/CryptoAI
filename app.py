import streamlit as st
from src.main import get_response, check_username, refetch_crypto_ids, refetch_curr

# Initialize session state for conversation history
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []

# Title of the app
st.title("Cryptocurrency Query App")

# User input section
username = st.text_input("Enter your username:", value='Rishika50')
if st.button("Submit username"):
    st.text(check_username(username))

user_question = st.text_input("Ask your question about cryptocurrencies:")

# Button to submit the question
if st.button("Get Response"):
    if username and user_question:
        answer = get_response(user_query=user_question, user_id=username)
        # Append question and answer to conversation history
        st.session_state.conversation_history.append((user_question, answer))
    else:
        st.error("Please enter both username and question.")

# Display conversation history
if st.session_state.conversation_history:
    st.subheader("Conversation History:")
    
    for idx, (question, answer) in enumerate(st.session_state.conversation_history):
        # Display question and answer with better formatting
        st.markdown(f"<div style='border: 1px solid #ddd; padding: 10px; margin: 10px 0; border-radius: 5px;'>", unsafe_allow_html=True)
        st.markdown(f"<strong style='color: blue;'>You:</strong> {question}", unsafe_allow_html=True)
        st.markdown(f"<strong style='color: green;'>Bot:</strong> {answer}", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# Buttons to perform operations
col1, col2 = st.columns(2)

with col1:
    if st.button("Refetch supported currencies"):
        refetch_curr()
        st.success("Currencies updated")

with col2:
    if st.button("Refetch crypto ids"):
        refetch_crypto_ids()
        st.success("Crypto ids updated")

