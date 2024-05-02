import streamlit as st
import sqlite3
import random
import time

# Function to get database connection
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

def add_entrant(entrant):
    conn = get_db_connection()
    c = conn.cursor()
    try:
        c.execute('INSERT INTO entrants (username) VALUES (?)', (entrant,))
        conn.commit()
        st.success(f"You have successfully entered the contest, @{entrant}!")
    except sqlite3.IntegrityError:
        st.warning(f"You have already entered the contest, @{entrant}.")
    finally:
        conn.close()

def choose_winner():
    conn = get_db_connection()
    c = conn.cursor()
    entrants = c.execute('SELECT username FROM entrants').fetchall()
    entrants = [entrant[0] for entrant in entrants]
    conn.close()
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

st.title("Instagram Contest for a Loud City Ticket")
st.write(st.session_state.winner)
if st.session_state.winner is None:
    st.subheader("Win a free ticket by entering your Instagram username below and following afafore1 on Instagram!")

    # User input for Instagram username
    username_input = st.text_input("Enter your Instagram username", key='username')
    if st.button("Enter Contest"):
        if username_input:
            add_entrant(username_input)

# Admin area for choosing the winner
with st.expander("Admin Area"):
    admin_password = st.text_input("Enter Admin Password", type="password")
    if admin_password == st.secrets['secrets']['admin_password']:
        if st.button("Choose Winner"):
            choose_winner()
        if st.checkbox('Show current entrants'):
            conn = get_db_connection()
            c = conn.cursor()
            entrants = c.execute('SELECT username FROM entrants').fetchall()
            conn.close()
            st.write([entrant[0] for entrant in entrants])
        if st.button("Clear entrants"):
            conn = get_db_connection()
            c = conn.cursor()
            c.execute('DELETE FROM entrants')
            conn.commit()
            conn.close()
            st.session_state.winner = None
            st.success("All entrants have been cleared.")
    else:
        if admin_password:
            st.error("Incorrect password.")
