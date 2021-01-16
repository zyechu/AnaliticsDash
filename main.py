import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import matplotlib.pyplot as plt
# importing glob for getting all *.csv files in data folder
import glob

from math import pi
from bokeh.plotting import figure
from bokeh.palettes import Category20c
from bokeh.transform import cumsum
from bokeh.plotting import figure
from bokeh.io import output_file, show
import altair as alt


def find_paths_for_data():
    woj_list = []
    for files in glob.glob("data/*.csv"):
        # splitter = "data\\"
        base = f'data'+'/'
        splited_files = base + files.split("data\\")[1]
        woj_list.append(splited_files)
    return woj_list
paths_for_data = find_paths_for_data()
# print(paths_for_data)
#
# DATA_URL = 'data\woj_DOLNOŚLĄSKIE.csv'

# st.subheader('Weekly Demand Data')
# st.write(weekly_data)
#Bar Chart


@st.cache(persist=False)
def load_data(paths_list):
    # wczytanie pierwszej ścieżki z listy
    # data = pd.read_csv(paths_list[0],index_col=0)
    # print(paths_list[1:])
    frames = []
    for path in paths_list:
        data_current = pd.read_csv(path, index_col=0)
        frames.append(data_current)
        # data = pd.concat(data, data_current, ignore_index=True)
        # print(data)
    data = pd.concat(frames)

    # add new column moc-do-masy
    data['moc-do-masy'] = data['moc-netto-silnika'] / data['masa-wlasna']
    return data


# Create a text element and let the reader know the data is loading.
data_load_state = st.text('Loading data...')
# Loading the data
data = load_data(paths_for_data)
# data['']
# Notify the reader that the data was successfully loaded.
data_load_state.text('Loading data...done!')

st.title("Registered cars analitics dashboard")
st.markdown("Dashboard")
st.sidebar.title("Registered cars data")
st.sidebar.markdown("Select the options to filter data")

# voivedeship filter
voivodeship_checkbox = st.sidebar.checkbox("Filter by voivodeship", False, key=2)
if voivodeship_checkbox:
    voivodeship_unique = data['rejestracja-wojewodztwo'].sort_values(ascending=True).unique()
    select = st.sidebar.selectbox("Select a voivodeship", voivodeship_unique)
    data = data[data['rejestracja-wojewodztwo'] == select]
# brand filter
brand_checkbox = st.sidebar.checkbox("Filter by Brand", False, key=1)

if brand_checkbox:
    brands_unique = data['marka'].sort_values(ascending=True).unique()
    select = st.sidebar.selectbox("Select a brand", brands_unique)
    data = data[data['marka'] == select]
    model_checkbox = st.sidebar.checkbox("Filter by model", False, key=1)
    if model_checkbox :
        model_unique = data['model'].sort_values(ascending=True).unique()
        select = st.sidebar.selectbox("Select a model", model_unique)
        data = data[data['model'] == select]

enginge_filter = st.sidebar.slider('engine capacity',
                                    min(data['pojemnosc-skokowa-silnika']),
                                    max(data['pojemnosc-skokowa-silnika'])+10,
                                    (min(data['pojemnosc-skokowa-silnika']),
                                    max(data['pojemnosc-skokowa-silnika'])))

data = data[data['pojemnosc-skokowa-silnika'] > enginge_filter[0]]
data = data[data['pojemnosc-skokowa-silnika'] < enginge_filter[1]]

car_type_list = list(data['podrodzaj-pojazdu'].sort_values(ascending=True).unique())

car_type_list.append('Wszystkie')

#get the state selected in the selectbox
select_status = 'nan'
vehicle_type_checkbox = st.sidebar.checkbox("Filter by Vehicle Type", False, key=1)

if vehicle_type_checkbox:
    select_status = st.sidebar.radio("Vehicle Type", car_type_list)
    if select_status == 'Wszystkie':
        pass
    else:
        data = data[data['podrodzaj-pojazdu'] == select_status]

fuel_type_checkbox = st.sidebar.checkbox("Filter by Fuel Type", False, key=1)

if fuel_type_checkbox:
    fuel_unique = data['rodzaj-paliwa'].sort_values(ascending=True).unique()
    select = st.sidebar.selectbox("Select a Fuel Type", fuel_unique)
    data = data[data['rodzaj-paliwa'] == select]

seats_checkbox = st.sidebar.checkbox("Filter by number of seats", False, key=1)

if seats_checkbox:
    fuel_unique = data['liczba-miejsc-ogolem'].sort_values(ascending=True).unique()
    select = st.sidebar.selectbox("Select a number of seats", fuel_unique)
    data = data[data['liczba-miejsc-ogolem'] == select]

st.subheader('Look into 10 rows of raw data')
st.write(data.head(10))

def count_per_day(df):
    pd.to_datetime(df['data-pierwszej-rejestracji-w-kraju'], format='%Y-%m-%d', errors='raise')
    dates = df['data-pierwszej-rejestracji-w-kraju']
    dates = dates.value_counts(sort = False)
    dates = dates.sort_index()
    return dates


def count_per_col(df, column):
    data_col = df[column]
    data_col = data_col.value_counts(sort = True)
    return data_col


def draw_pie_chart(df, column):
    data_col = df.fillna('brak_danych')
    data_col = count_per_col(data_col, column)
    data_pie = pd.Series(data_col).reset_index(name='value').rename(columns={'index': column})
    # print(data_col)
    # print(data_pie)
    data_pie = data_pie.rename(columns={column: 'column'})
    data_pie['angle'] = data_pie['value'] / data_pie['value'].sum() * 2 * pi
    data_pie['color'] = Category20c[len(data_pie)]
    p = figure(plot_height=350, title="Pie Chart", toolbar_location=None,
               tools="hover", tooltips=f"@column: @value", x_range=(-0.5, 1.0))
    p.wedge(x=0, y=1, radius=0.4,
            start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
            line_color="white", fill_color='color', legend_field='column', source=data_pie)
    p.axis.axis_label = None
    p.axis.visible = False
    p.grid.grid_line_color = None
    return p


column_to_pie_chart = ['podrodzaj-pojazdu', 'pochodzenie-pojazdu', 'rodzaj-paliwa']
if select_status != 'Wszystkie':
    column_to_pie_chart.remove('podrodzaj-pojazdu')

    select_to_pie = st.selectbox("Select a column to make a pie chart", column_to_pie_chart)


# draw_pie_chart(data, select_to_pie)
try:
    st.bokeh_chart(draw_pie_chart(data, select_to_pie), use_container_width=False)
except:
    print("PIE CHART ERROR")
    st.text("Pie chart can't be loaded")

count_per_vehicle_type = count_per_col(data,'podrodzaj-pojazdu')
# count_per_vehicle_type = pd.DataFrame(count_per_vehicle_type)
count_per_vehicle_type = count_per_vehicle_type.reset_index()


# bar chart presenting the number of registration per body style
chart = alt.Chart(count_per_vehicle_type).mark_bar().encode(
            x=alt.X('podrodzaj-pojazdu', title='Number of registration'),
            y=alt.Y('index', title='Type of body style', sort='-x')
        )
st.altair_chart(chart, use_container_width=True)

# draw_pie_chart(data, 'rodzaj-paliwa')
df_count_per_day = count_per_day(data)
df_count_per_day = pd.DataFrame(df_count_per_day)
df_count_per_day = df_count_per_day.reset_index()
df_count_per_day.columns = ['data', 'liczba']
df_count_per_day['data'] = pd.to_datetime(df_count_per_day['data'])
df_count_per_day = df_count_per_day.reset_index()

# Bar Chart presenting the number of registration per day
chart = alt.Chart(df_count_per_day).mark_bar().encode(
            x=alt.X('data:T', title='Data'),
            y=alt.Y('liczba:Q', title='Daily number of registration')
        )
st.altair_chart(chart, use_container_width=True)

# Line Chart presenting the number of registration per day
chart = alt.Chart(df_count_per_day).mark_line().encode(
            x=alt.X('data:T', title='Data'),
            y=alt.Y('liczba:Q', title='Daily number of registration')
        )
chart = chart + chart.transform_regression('index', 'y').mark_line()
st.altair_chart(chart, use_container_width=True)


# st.bokeh_chart(p, use_container_width=False)


