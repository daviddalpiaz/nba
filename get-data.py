import os
import numpy as np
import pandas as pd

# inspiration: https://tomaugspurger.net/posts/modern-5-tidy/
# data source: http://www.basketball-reference.com/


def convert_time_format(time_str):
    return time_str.replace("a", "AM").replace("p", "PM")


# path to store raw data
path_data_raw = "data-raw/nba.csv"

if not os.path.exists(path_data_raw):
    tables = pd.read_html("http://www.basketball-reference.com/leagues/NBA_2016_games.html")
    games = tables[0]
    games.to_csv(path_data_raw)
else:
    games = pd.read_csv(path_data_raw)

# current column names from basketball-reference.com mapped to names for df
column_names = {
    "Unnamed: 0": "game_id",
    "Date": "date",
    "Start (ET)": "start",
    "Visitor/Neutral": "away_team",
    "PTS": "away_points",
    "Home/Neutral": "home_team",
    "PTS.1": "home_points",
    "Unnamed: 6": "box_score",
    "Unnamed: 7": "n_ot",
    "Attend.": "attendance",
    "Arena": "arena",
    "Notes": "notes",
}

# process games data
games = games.rename(columns=column_names)
games = games.assign(date=lambda x: pd.to_datetime(x["date"], format="%a, %b %d, %Y"))
games["start"] = pd.to_datetime(games["start"].apply(convert_time_format), format="%I:%M%p").dt.time
games = games.sort_values(["date", "start"], ascending=[True, True])
games.drop(columns=["game_id"], inplace=True)
games.insert(2, "date_game_id", games.groupby("date").cumcount())
games

# create tidy data from home-away rest day analysis
games_tidy_location = pd.melt(
    games,
    id_vars=["date", "date_game_id"],
    value_vars=["away_team", "home_team"],
    value_name="team",
    var_name="location",
)
games_tidy_location["location"] = games_tidy_location["location"].replace(
    {"away_team": "away", "home_team": "home"}
)
games_tidy_location["rest"] = (
    games_tidy_location.sort_values("date").groupby("team").date.diff().dt.days - 1
)
games_tidy_location.dropna()

# working towards obtaining all data
base_url = "http://www.basketball-reference.com/leagues/NBA_2016_games-"
months = ["October", "November", "December", "January", "February", "March", "April", "May", "June"]
urls = [base_url + month.lower() + ".html" for month in months]
