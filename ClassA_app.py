# Importing the necessary libraries
import pandas as pd
import base64
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import streamlit as st
from bs4 import BeautifulSoup
import requests
from highlight_text import fig_text
from mplsoccer import Bumpy, FontManager, add_image
import json
import urllib.request
from urllib.request import urlopen

st.set_page_config(layout='wide')

st.title('Class A Krakow Group 3 season 2023/2024')

st.markdown("""
The application shows the current football table MZPN Class A Group 3.

The chart shows each team's current position in the table after a round of matches.
* **Python libraries:** base64, pandas, streamlit, request, BeautifulSoup, highlight_text, mplsoccer
* **Data source:** [https://www.mzpnkrakow.pl/terminarze/2023-2024/seniorzy/a_krakow_3/](https://www.mzpnkrakow.pl/terminarze/2023-2024/seniorzy/a_krakow_3/)
""")

c1, c2 = st.columns((55,45))

with c1:
    
    st.markdown("""Table""")
    
    # MZPN url website
    url = 'https://www.mzpnkrakow.pl/terminarze/2023-2024/seniorzy/a_krakow_3/'

    response = requests.get(url)

    # parse text
    soup = BeautifulSoup(response.text, 'html.parser')

    table = soup.find('table', {'id' : 'tabela', 'class' : 'table'})

    # append header and rows lists from table object
    header = []
    rows = []
    for i, row in enumerate(table.find_all('tr')):
        if i == 1:
            header = [el.text.strip() for el in row.find_all('th')]
        else:
            rows.append([el.text.strip() for el in row.find_all('td')])

    # Remowe empty list from start of rows list
    rows.remove([])

    # create dataframe from rows and header list
    df = pd.DataFrame([row for row in rows], columns=header)

    # slice dataframe for desired columns
    df_slice = df.iloc[:, 0:8]

    # Rename each column
    df_slice.rename(columns={'Drużyna' : 'Team', 'M' : 'Match', 
                            'Pkt' : 'Points', 'Z' : 'Wins', 
                            'R' : "Draws", 'P' : "Losses", 
                            'Bramki' : 'Goals', 'Poz' : 'Position'}, inplace=True)

    # Display dataframe in stremlit
    st.dataframe(df_slice, hide_index=True, width=615, height=528)

with c2:
    
    st.markdown("""Players with the most goals""")
    
    df_players = pd.read_csv(r'https://raw.githubusercontent.com/MSI17819/Streamlit-Football-Table-App/main/ClassA_goals.csv',
                         encoding='utf-8', delimiter=';')

    df_players = df_players.rename(columns={'Sum' : 'Goals'})

    df_players_slice = df_players.loc[:, ['Player', 'Team', 'Goals']]

    st.sidebar.header('Choose a team for the player with the most goals')

    sorted_unique_team = sorted(df_players_slice['Team'].unique())

    select_team = st.sidebar.multiselect('Team', sorted_unique_team, sorted_unique_team)

    df_selected_team = df_players_slice[(df_players_slice['Team'].isin(select_team))]

    st.dataframe(df_selected_team, hide_index=True, width=490, height=388)

# Open json file from github url
with urllib.request.urlopen(r'https://raw.githubusercontent.com/MSI17819/Streamlit-Football-Table-App/main/Data/ClassA_result_after_13.json') as url:
    data_after_12 = json.load(url)

team_list = ['BOREK KRAKÓW',
             'PŁOMIEŃ KOSTRZE',
             'ZWIERZYNIECKI KRAKÓW',
             'TRAMWAJ KRAKÓW',
             'PODGÓRZE KRAKÓW',
             'NADWIŚLAN KRAKÓW',
             'RADZISZOWIANKA II RADZISZÓW',
             'ISKRA KRZĘCIN',
             'DĄBSKI KRAKÓW',
             'FAIRANT KRAKÓW',
             'GAJOWIANKA GAJ',
             'TRZEBOL WIELKIE DROGI',
             'CEDRONKA WOLA RADZISZOWSKA',
             'STRZELCY KRAKÓW'
            ]
             

# Display of notes to the chart
st.markdown("""The chart shows the position and number of matches played for each team.""")

# Start button
if st.button('Chart autumn'):
    
    # Use bumpy chart from mplsoccer library
    
    # match-week
    match_day = [str(num) for num in range(1, 14)]

    # highlight dict --> team to highlight and their corresponding colors
    highlight_dict = {'FAIRANT KRAKÓW' : "#fe0000",
                    'NADWIŚLAN KRAKÓW' : "#800001",
                    'TRZEBOL WIELKIE DROGI' : "#d65b02",
                    'BOREK KRAKÓW' : "#9c5d63",
                    'RADZISZOWIANKA II RADZISZÓW' : "#ffd800",
                    'PŁOMIEŃ KOSTRZE' : "#806b00",
                    'TRAMWAJ KRAKÓW' : "#0026ff",
                    'GAJOWIANKA GAJ' : "#029615",
                    'STRZELCY KRAKÓW' : "#005909",
                    'CEDRONKA WOLA RADZISZOWSKA' : "#012742",
                    'PODGÓRZE KRAKÓW' : "#00497e",
                    'ZWIERZYNIECKI KRAKÓW' : "#001280",
                    'DĄBSKI KRAKÓW' : "#b100fe",
                    'ISKRA KRZĘCIN' : "#7f2b0a"
                    }
     
    # instantiate object
    bumpy = Bumpy(
        background_color="#9a9a9a", scatter_color="#a6a6a6",
        label_color="#000000", line_color="#C0C0C0",
        rotate_xticks=None,  # rotate x-ticks by 90 degrees
        ticklabel_size=20, label_size=22,  # ticklable and label font-size
        scatter_points='D',   # other markers
        scatter_primary='o',  # marker to be used for teams
        scatter_size=150,   # size of the marker
        show_right=True,  # show position on the rightside
        plot_labels=True,  # plot the labels
        alignment_yvalue=0.1,  # y label alignment
        alignment_xvalue=0.065  # x label alignment
        )

    # plot bumpy chart
    fig, ax = bumpy.plot(
        x_list=match_day,  # match-day or match-week
        y_list=np.linspace(1, 14, 14).astype(int),  # position value from 1 to 20
        values=data_after_12,  # values having positions for each team
        secondary_alpha=0.4,   # alpha value for non-shaded lines/markers
        highlight_dict=highlight_dict,  # team to be highlighted with their colors
        figsize=(18, 8),  # size of the figure
        x_label='Match no.', y_label='Table position',  # label name
        ylim=(-0.1, 15),  # y-axis limit
        lw=2.0 # linewidth of the connecting lines
        )

    # title
    TITLE = "Class A Group 3 season 2023/2024 autumn"
    
    # add title
    fig.text(0.5, 0.99, TITLE, size=30, color="#222222", ha="center")
    
    # add color from highlite_dict to assigned team
    for idx, val in enumerate(team_list):
        # Using only the first word of the team name
        team_name = val.split()[0]
        for key, value in highlight_dict.items():
            if val == key:
                if idx == 0:
                    fig.text(0.92, 0.820, team_name, size=20, ha="left", color=value)
                elif idx == 1:
                    fig.text(0.92, 0.765, team_name, fontsize=20, ha="left", color=value)
                elif idx == 2:
                    fig.text(0.92, 0.710, team_name, fontsize=20, ha="left", color=value)
                elif idx == 3:
                    fig.text(0.92, 0.660, team_name, fontsize=20, ha="left", color=value)
                elif idx == 4:
                    fig.text(0.92, 0.610, team_name, fontsize=20, ha="left", color=value)
                elif idx == 5:
                    fig.text(0.92, 0.560, team_name, fontsize=20, ha="left", color=value)
                elif idx == 6:
                    fig.text(0.92, 0.510, team_name, fontsize=20, ha="left", color=value)
                elif idx == 7:
                    fig.text(0.92, 0.458, team_name, fontsize=20, ha="left", color=value)
                elif idx == 8:
                    fig.text(0.92, 0.408, team_name, fontsize=20, ha="left", color=value)
                elif idx == 9:
                    fig.text(0.925, 0.355, team_name, fontsize=20, ha="left", color=value)
                elif idx == 10:
                    fig.text(0.925, 0.305, team_name, fontsize=20, ha="left", color=value)
                elif idx == 11:
                    fig.text(0.925, 0.255, team_name, fontsize=20, ha="left", color=value)
                elif idx == 12:
                    fig.text(0.925, 0.205, team_name, fontsize=20, ha="left", color=value)
                else:
                    fig.text(0.925, 0.150, team_name, fontsize=20, ha="left", color=value)
    
    st.pyplot(fig)

# Open json file from github url
with urllib.request.urlopen(r'https://raw.githubusercontent.com/MSI17819/Streamlit-Football-Table-App/main/Data/ClassA_result_after_13_spring.json') as url_spring:
    data_spring = json.load(url_spring)

if st.button('Chart spring'):
    
    # Use bumpy chart from mplsoccer library
    
    # match-week
    match_day = [str(num) for num in range(1, 14)]

    # highlight dict --> team to highlight and their corresponding colors
    highlight_dict = {'FAIRANT KRAKÓW' : "#fe0000",
                    'NADWIŚLAN KRAKÓW' : "#800001",
                    'TRZEBOL WIELKIE DROGI' : "#d65b02",
                    'BOREK KRAKÓW' : "#9c5d63",
                    'RADZISZOWIANKA II RADZISZÓW' : "#ffd800",
                    'PŁOMIEŃ KOSTRZE' : "#806b00",
                    'TRAMWAJ KRAKÓW' : "#0026ff",
                    'GAJOWIANKA GAJ' : "#029615",
                    'STRZELCY KRAKÓW' : "#005909",
                    'CEDRONKA WOLA RADZISZOWSKA' : "#012742",
                    'PODGÓRZE KRAKÓW' : "#00497e",
                    'ZWIERZYNIECKI KRAKÓW' : "#001280",
                    'DĄBSKI KRAKÓW' : "#b100fe",
                    'ISKRA KRZĘCIN' : "#7f2b0a"
                    }
     
    # instantiate object
    bumpy = Bumpy(
        background_color="#9a9a9a", scatter_color="#a6a6a6",
        label_color="#000000", line_color="#C0C0C0",
        rotate_xticks=None,  # rotate x-ticks by 90 degrees
        ticklabel_size=20, label_size=22,  # ticklable and label font-size
        scatter_points='D',   # other markers
        scatter_primary='o',  # marker to be used for teams
        scatter_size=150,   # size of the marker
        show_right=True,  # show position on the rightside
        plot_labels=True,  # plot the labels
        alignment_yvalue=0.1,  # y label alignment
        alignment_xvalue=0.065  # x label alignment
        )

    # plot bumpy chart
    fig, ax = bumpy.plot(
        x_list=match_day,  # match-day or match-week
        y_list=np.linspace(1, 14, 14).astype(int),  # position value from 1 to 20
        values=data_spring,  # values having positions for each team
        secondary_alpha=0.4,   # alpha value for non-shaded lines/markers
        highlight_dict=highlight_dict,  # team to be highlighted with their colors
        figsize=(18, 8),  # size of the figure
        x_label='Match no.', y_label='Table position',  # label name
        ylim=(-0.1, 15),  # y-axis limit
        lw=2.0 # linewidth of the connecting lines
        )

    # title
    TITLE = "Class A Group 3 season 2023/2024 spring"
    
    # add title
    fig.text(0.5, 0.99, TITLE, size=30, color="#222222", ha="center")
    
    # add color from highlite_dict to assigned team
    for idx, val in enumerate(df_slice['Team']):
        # Using only the first word of the team name
        team_name = val.split()[0]
        for key, value in highlight_dict.items():
            if val == key:
                if idx == 0:
                    fig.text(0.92, 0.820, team_name, size=20, ha="left", color=value)
                elif idx == 1:
                    fig.text(0.92, 0.765, team_name, fontsize=20, ha="left", color=value)
                elif idx == 2:
                    fig.text(0.92, 0.710, team_name, fontsize=20, ha="left", color=value)
                elif idx == 3:
                    fig.text(0.92, 0.660, team_name, fontsize=20, ha="left", color=value)
                elif idx == 4:
                    fig.text(0.92, 0.610, team_name, fontsize=20, ha="left", color=value)
                elif idx == 5:
                    fig.text(0.92, 0.560, team_name, fontsize=20, ha="left", color=value)
                elif idx == 6:
                    fig.text(0.92, 0.510, team_name, fontsize=20, ha="left", color=value)
                elif idx == 7:
                    fig.text(0.92, 0.458, team_name, fontsize=20, ha="left", color=value)
                elif idx == 8:
                    fig.text(0.92, 0.408, team_name, fontsize=20, ha="left", color=value)
                elif idx == 9:
                    fig.text(0.925, 0.355, team_name, fontsize=20, ha="left", color=value)
                elif idx == 10:
                    fig.text(0.925, 0.305, team_name, fontsize=20, ha="left", color=value)
                elif idx == 11:
                    fig.text(0.925, 0.255, team_name, fontsize=20, ha="left", color=value)
                elif idx == 12:
                    fig.text(0.925, 0.205, team_name, fontsize=20, ha="left", color=value)
                else:
                    fig.text(0.925, 0.150, team_name, fontsize=20, ha="left", color=value)
    
    st.pyplot(fig)
