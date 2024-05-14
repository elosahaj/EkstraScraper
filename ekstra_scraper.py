### please check out read_me for the program description ###

import requests
import pandas as pd
from bs4 import BeautifulSoup
import numpy as np
import io
import os
import datetime

### Set the clear() function

### Set default season as current season
def is_before_july():
    """Check if new data is available."""
    today = datetime.datetime.now()
    july = datetime.datetime(today.year, 7, 1)
    return today < july

cur_season = int(datetime.datetime.now().year)
if is_before_july():
    cur_season -= 1
cur_season = str(cur_season)[-2:]
cur_season = f"20{cur_season}-20{int(cur_season) + 1}"
season = cur_season

# ### Import stats from url into a soup ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
# request_url = str(f"https://fbref.com/en/comps/36/{season}/{season}-Ekstraklasa-Stats")
# table_data = requests.get(request_url)
# soup = BeautifulSoup(table_data.text, 'html.parser')

### Functions ###
def create_table(ssn=season):
    """Put the table data into a DataFrame, use ranking as an index, remove last column, add a new column with ranking-based notes instead"""

    # Import stats from url into a soup
    global request_url, table_data, soup
    request_url = f"https://fbref.com/en/comps/36/{season}/{season}-Ekstraklasa-Stats"
    table_data = requests.get(request_url)
    soup = BeautifulSoup(table_data.text, 'html.parser')

    table = pd.read_html(io.StringIO(table_data.text), match="Regular season Table")
    df_table = table[0]
    df_table.set_index(df_table.columns[0], inplace=True)
    df_table = df_table.iloc[:, :-1]

    # Change 'Attendance' to 'Avg Attend.'
    df_table.rename(columns={'Attendance': 'Avg Attend.'}, inplace=True)

    # Add a new column "Notes" based on the index values
    df_table["Notes"] = ""
    notes_mapping = {
        "CL Qual.": [df_table.index[0]],
        "Conf Qual.": df_table.index[1:3].tolist(),
        "Relegation": df_table.index[15:18].tolist()
    }

    for note, index_list in notes_mapping.items():
        df_table.loc[index_list, "Notes"] = note

    mp = df_table['MP'].max()
    print()
    print(f"Ekstraklasa, season: {season}. Games played: {mp} out of 34.")
    print()
    print(df_table)
    print()
    print("To see team data - type t")
    print("To change year - type y")
    print()

    exit_table_options = False
    while not exit_table_options:
        table_options = str(input("Choose from above: \n")).lower()
        if table_options == "t":
            show_team_results()
            exit_table_options = True
        elif table_options == "y":
            choose_season()
            exit_table_options = True
        else:
            print("Wrong input")
            exit_table_options = False



def choose_season():
    print("Choose from available seasons:")
    print("Season 2021-2022 - type 1")
    print("Season 2022-2023 - type 2")
    print("Season 2023-2024 - type 3")
    print("Current season - type x")
    print()
    global season
    exit_season_choice = False
    while not exit_season_choice:
        season_choice = str(input("Choose from above: \n")).lower()
        if season_choice == "1":
            season = "2021-2022"
            exit_season_choice = True
        elif season_choice == "2":
            season = "2022-2023"
            exit_season_choice = True
        elif season_choice == "3":
            season = "2023-2024"
            exit_season_choice = True
        elif season_choice == "x":
            season = cur_season
            exit_season_choice = True
        else:
            print("Wrong input")
            exit_season_choice = False
    create_table(season)


def show_team_results():
    """Displays all fixtures of a chosen team along with stats."""
    
    rk = int(input("Select the Rk of the team to see their results: \n"))
    main_table = soup.find('table', class_='stats_table')

    # Get links to each team's data page
    links = main_table.find_all('a')
    links = [l.get("href") for l in links]
    links = [f"https://fbref.com{l}" for l in links if '/squads/' in l]

    # Extract match data of a team and insert into a DataFrame. 
    team_link = links[rk - 1]  # links[n] is the n team from the main table 
    games_data = requests.get(team_link)

    games = pd.read_html(io.StringIO(games_data.text), match="Scores & Fixtures", index_col=0)
    df_games = games[0]

    ## Formatting
    # Filter for Ekstraklasa games only
    df_games = df_games[df_games['Comp'] == 'Ekstraklasa']
    # Remove unnecessary columns
    columns_to_drop = ['Comp', 'Poss', 'xG', 'xGA', 'Match Report', 'Notes']
    df_games = df_games.drop(columns=[col for col in columns_to_drop if col in df_games.columns])
    # Convert columns GF, GA, and Attendance to integers
    df_games[['GF', 'GA', 'Attendance']] = df_games[['GF', 'GA', 'Attendance']].apply(pd.to_numeric, errors='coerce').fillna(0).astype(int)

    # Change Round "Matchweek 1" to Round "1"
    df_games['Round'] = df_games['Round'].str.replace("Matchweek ", "")
    # Add Status if Moved or Not Played Yet
    df_games['Status'] = np.where((df_games['Round'].astype(int) < df_games['Round'].astype(int).shift(1)) & (df_games['Round'] != '1'), 'Moved', '')
    df_games['Status'] = np.where(df_games['Result'].isna(), 'TBC', df_games['Status'])

    print()
    print(f"Ekstraklasa, season: {season}")
    print()
    print(df_games)
    print()
    print("Go back - type 0")
    exit_team_results = False
    while not exit_team_results:
        go_back = str(input("Choose from above: \n")).lower()
        if go_back == "0":
            create_table()
            exit_team_results = True
        else:
            print("Wrong input")
            exit_team_results = False


create_table()