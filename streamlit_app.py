import streamlit as st
import random


def add_entrant(entrant):
    if 'entrants' not in st.session_state:
        st.session_state.entrants = []
    # Checks if the username is already in the list or if it's empty
    if entrant:
        if entrant not in st.session_state.entrants:
            st.session_state.entrants.append(entrant)
            st.success(f"You have successfully entered the contest, @{entrant}!")
        else:
            st.warning(f"You have already entered the contest, @{entrant}.")
    else:
        st.error("Please enter a valid Instagram username to enter the contest.")


def choose_winner():
    # Randomly picks a winner from the list of entrants
    if 'entrants' not in st.session_state:
        st.session_state.entrants = []
    if st.session_state.entrants:
        winner = random.choice(st.session_state.entrants)
        st.success(f"The winner is: @{winner}")
    else:
        st.error("No entrants yet to select a winner.")


st.title("Instagram Contest for a Loud City Ticket")
st.subheader("Win a free ticket by entering your Instagram username below and following afafore1 on Instagram and "
             "TikTok!")

# User input for Instagram username
username_input = st.text_input("Enter your Instagram username", key='username')

# Button to submit the username
if st.button("Enter Contest"):
    add_entrant(username_input)

# Optionally, display the list of current entrants
if st.checkbox('Show current entrants'):
    st.write("Current entrants:", st.session_state.entrants)

# Admin area for choosing the winner
with st.expander("Admin Area"):
    admin_password = st.text_input("Enter Admin Password", type="password")
    if admin_password == st.secrets['secrets']['admin_password']:
        if st.button("Choose Winner"):
            choose_winner()
    else:
        if admin_password:
            st.error("Incorrect password.")
