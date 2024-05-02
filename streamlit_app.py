import streamlit as st
import random
import sqlite3
import time


def get_db_connection():
    conn = sqlite3.connect('contest.db', check_same_thread=False)
    return conn

# Function to create table if it does not exist
def setup_database():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS entrants(
        username TEXT UNIQUE
        )
    ''')
    conn.commit()
    conn.close()

setup_database()  # Set up the database table if not already set up
if 'winner' not in st.session_state:
    st.session_state.winner = None


def add_entrant(entrant):
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('INSERT INTO entrants (username) VALUES (?)', (entrant,))
        conn.commit()
        conn.close()
        st.success(f"You have successfully entered the contest, @{entrant}!")
    except sqlite3.IntegrityError:
        st.warning(f"You have already entered the contest, @{entrant}.")


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


def get_all_entrants():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT username FROM entrants')
    return [row[0] for row in c.fetchall()]


st.title("Instagram Contest for a Loud City Ticket")
if st.session_state.winner is None:
    st.subheader("Win a free ticket by following afafore1 on Instagram and entering your Instagram username below!")

    # User input for Instagram username
    username_input = st.text_input("Enter your Instagram username", key='username')
    # Button to submit the username
    if st.button("Enter Contest"):
        add_entrant(username_input)
else:
    st.subheader(f"The winner is: @{st.session_state.winner}")

# Admin area for choosing the winner
with st.expander("Admin Area"):
    admin_password = st.text_input("Enter Admin Password", type="password")
    if admin_password == st.secrets['secrets']['admin_password']:
        if st.button("Choose Winner"):
            choose_winner()
        if st.checkbox('Show current entrants'):
           st.write(get_all_entrants())
        if st.button("Clear entrants"):
            conn = get_db_connection()
            c = conn.cursor()
            c.execute('DELETE FROM entrants')
            conn.commit()
            conn.close()
            st.session_state.winner = None
    else:
        if admin_password:
            st.error("Incorrect password.")
