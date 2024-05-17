import pandas as pd
import streamlit as st

from supabase import create_client, Client

table_name = 'ticket_giveaway'

url: str = st.secrets['secrets']['url']
key: str = st.secrets['secrets']['db_key']
supabase: Client = create_client(url, key)


if 'winners' not in st.session_state:
    st.session_state.winners = None


def refresh_team_and_opponent():
    if 'current_team' not in st.session_state or 'current_opponent' not in st.session_state or st.session_state.current_team is None:
        response = supabase.table('team_to_opponent').select('team, opponent, date_playing').order('date_playing', desc=True).execute()
        latest_entry = pd.DataFrame(response.data).iloc[0]
        st.session_state.current_team = latest_entry['team']
        st.session_state.current_opponent = latest_entry['opponent']
        st.session_state.date_playing = latest_entry['date_playing']


def add_entrant(entrant):
    refresh_team_and_opponent()
    current_team, current_opponent = st.session_state.current_team, st.session_state.current_opponent
    try:
        supabase.table(table_name).insert(
            {'entrant': entrant, 'team_ticket': current_team, 'opponent': current_opponent, 'date_playing': st.session_state.date_playing}).execute()
        st.success(f"You have successfully entered the contest, @{entrant}!")
    except Exception as e:
        if 'duplicate key value violates unique constraint' in str(e):
            st.error('You are already entered into the contest')
        else:
            st.error(str(e))


def contest_started():
    if 'is_started' is not st.session_state:
        response = supabase.table('contest').select('*').execute()
        data = response.data[0]
        is_started = data['is_started']
        if is_started:
            st.session_state.is_started = True
            return True
        st.session_state.is_started = False
        return False


st.title("Win A Free Loud City Ticket To OKC Thunder Playoff Game!!!")
if contest_started():
    st.subheader("Follow afafore1 on Instagram and TikTok!")

    # User input for Instagram username
    username_input = st.text_input("Enter your Instagram username", key='username')
    # Button to submit the username
    if st.button("Enter Contest"):
        add_entrant(username_input)
else:
    if st.session_state.winners is None:
        st.subheader('Contest will start before the next game!')
    else:
        winners = st.session_state.winners
        st.subheader(f"The winners are: @{winners[0]['entrant']} and @{winners[1]['entrant']}")
