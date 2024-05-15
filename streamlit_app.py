import pandas as pd
import streamlit as st
import random
import time
import datetime

from supabase import create_client, Client

nba_teams = [
    'Atlanta Hawks', 'Boston Celtics', 'Brooklyn Nets', 'Charlotte Hornets', 'Chicago Bulls',
    'Cleveland Cavaliers', 'Dallas Mavericks', 'Denver Nuggets', 'Detroit Pistons', 'Golden State Warriors',
    'Houston Rockets', 'Indiana Pacers', 'LA Clippers', 'Los Angeles Lakers', 'Memphis Grizzlies',
    'Miami Heat', 'Milwaukee Bucks', 'Minnesota Timberwolves', 'New Orleans Pelicans', 'New York Knicks',
    'Oklahoma City Thunder', 'Orlando Magic', 'Philadelphia 76ers', 'Phoenix Suns', 'Portland Trail Blazers',
    'Sacramento Kings', 'San Antonio Spurs', 'Toronto Raptors', 'Utah Jazz', 'Washington Wizards'
]
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
            {'entrant': entrant, 'team_ticket': current_team, 'opponent': current_opponent, 'date_playing': st.session_state.date_playing.isoformat()}).execute()
        st.success(f"You have successfully entered the contest, @{entrant}!")
    except Exception as e:
        if 'duplicate key value violates unique constraint' in str(e):
            st.error('You are already entered into the contest')
        else:
            st.error('An error occurred, please DM me to fix!')


def choose_winner():
    entrants = get_all_entrants()
    if entrants:
        placeholder = st.empty()
        sampled_entrants = random.sample(entrants, min(100, len(entrants)))
        for _ in range(3):
            for username in sampled_entrants:
                placeholder.text(f"Now drawing: @{username}")
                time.sleep(0.05)
        selections = random.sample(entrants, 2)
        a, b = selections[0], selections[1]
        placeholder.success(f"The winners are: @{a['entrant']} and @{b['entrant']}")
        st.session_state.winners = selections
    else:
        st.error("No entrants yet.")


def get_all_entrants():
    response = supabase.table(table_name).select('*').execute()
    return response.data


st.title("Win A Free Loud City Ticket To OKC Thunder Playoff Game!!!")
if st.session_state.winners is None:
    st.subheader("Follow afafore1 on Instagram and TikTok!")

    # User input for Instagram username
    username_input = st.text_input("Enter your Instagram username", key='username')
    # Button to submit the username
    if st.button("Enter Contest"):
        add_entrant(username_input)
else:
    winners = st.session_state.winners
    st.subheader(f"The winners are: @{winners[0]['entrant']} and @{winners[1]['entrant']}")

# Admin area for choosing the winner
with st.expander("Admin Area"):
    admin_password = st.text_input("Enter Admin Password", type="password")
    if admin_password == st.secrets['secrets']['admin_password']:
        all_entrants = get_all_entrants()
        if st.checkbox('Show current entrants'):
            st.dataframe(all_entrants)
        if st.button("Choose Winner"):
            choose_winner()

        team = st.selectbox('Who is the current team giving away the ticket?', nba_teams)
        opponent = st.selectbox('Who are the opponents today?', nba_teams)
        date_playing = st.date_input('What day are they playing?', min_value=datetime.date.today())
        if st.button('Start new contest'):
            if opponent:
                supabase.table('team_to_opponent').insert({'team': team, 'opponent': opponent, 'date_playing': date_playing.isoformat()}).execute()
                st.session_state.winners = None
                st.success('Inserted team details')
    else:
        if admin_password:
            st.error("Incorrect password.")
