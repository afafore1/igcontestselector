import streamlit as st
import random
import sqlite3
import time
from contextlib import contextmanager

# Database management
@contextmanager
def get_db_connection():
    conn = sqlite3.connect('contest.db')
    try:
        yield conn.cursor()
    finally:
        conn.commit()
        conn.close()

def add_entrant(entrant):
    with get_db_connection() as c:
        try:
            c.execute('INSERT INTO entrants (username) VALUES (?)', (entrant,))
            st.success(f"You have successfully entered the contest, @{entrant}!")
        except sqlite3.IntegrityError:
            st.warning(f"You have already entered the contest, @{entrant}.")

def get_all_entrants():
    with get_db_connection() as c:
        c.execute('SELECT username FROM entrants')
        return [row[0] for row in c.fetchall()]

def choose_winner():
    entrants = get_all_entrants()
    if entrants:
        placeholder = st.empty()
        sampled_entrants = random.sample(entrants, min(100, len(entrants)))
        for _ in range(3):
            for username in sampled_entrants:
                placeholder.text(f"Now drawing: @{username}")
                time.sleep(0.05)
        winner = random.choice(entrants)
        placeholder.success(f"The winner is: @{winner}")
        st.session_state.winner = winner
    else:
        st.error("No entrants yet.")

# Streamlit app layout
st.title("Instagram Contest for a Loud City Ticket")
if 'winner' not in st.session_state:
    st.session_state.winner = None

if st.session_state.winner is None:
    st.subheader("Win a free ticket by entering your Instagram username below and following afafore1 on Instagram!")
    username_input = st.text_input("Enter your Instagram username", key='username')
    if st.button("Enter Contest"):
        add_entrant(username_input)

# Admin area for choosing the winner and managing entrants
with st.expander("Admin Area"):
    admin_password = st.text_input("Enter Admin Password", type="password")
    if admin_password == st.secrets['secrets']['admin_password']:
        if st.button("Choose Winner"):
            choose_winner()
        if st.checkbox('Show current entrants'):
            st.write(get_all_entrants())
        if st.button("Clear entrants"):
            if st.button("Confirm Clear All Entrants"):
                with get_db_connection() as c:
                    c.execute('DELETE FROM entrants')
                st.session_state.winner = None
                st.success("All entrants have been cleared.")
    else:
        if admin_password:
            st.error("Incorrect password.")
