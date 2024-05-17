import datetime
import random
import time

import streamlit as st
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


def get_all_entrants():
    response = supabase.table(table_name).select('*').execute()
    return response.data


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


admin_password = st.text_input("Enter Admin Password", type="password")
# Admin area for choosing the winner
with st.expander("Select winner"):
    if admin_password == st.secrets['secrets']['admin_password']:
        all_entrants = get_all_entrants()
        if st.checkbox('Show current entrants'):
            st.dataframe(all_entrants)
        if st.button("Choose Winner"):
            choose_winner()
    else:
        if admin_password:
            st.error("Incorrect password.")

expander = st.expander('Start a new contest')
with expander:
    # admin_password = st.text_input("Enter Admin Password", type="password")
    if admin_password == st.secrets['secrets']['admin_password']:
        team = st.selectbox('Who is the current team giving away the ticket?', nba_teams)
        opponent = st.selectbox('Who are the opponents today?', nba_teams)
        date_playing = st.date_input('What day are they playing?', min_value=datetime.date.today())
        if st.button('Start new contest'):
            if opponent:
                supabase.table('team_to_opponent').insert(
                    {'team': team, 'opponent': opponent, 'date_playing': date_playing.isoformat()}).execute()
                st.session_state.winners = None
                st.session_state.is_started = True
                supabase.table('contest').insert({'is_started': True}).execute()
                st.success('Inserted team details')
    else:
        if admin_password:
            st.error("Incorrect password.")
