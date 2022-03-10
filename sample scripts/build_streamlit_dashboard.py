import os
import pandas as pd
import pathlib
import streamlit as st
from trino import dbapi
from trino import constants
from trino.auth import BasicAuthentication
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime

# Definitions
os.chdir(pathlib.Path(__file__).parent.absolute())

# Create a connection to the db
auth = None
conn = dbapi.connect(
    host=os.environ.get("VDK_TRINO_HOST"),
    port=int(os.environ.get("VDK_TRINO_PORT")),
    user="user",
    auth=auth,
    catalog=os.environ.get("VDK_TRINO_CATALOG", 'mysql'),
    schema=os.environ.get("VDK_TRINO_SCHEMA", "default"),
    http_scheme=constants.HTTP,
    verify=False,
    request_timeout=600,
)

# Fetch data and format date variable
df = pd.read_sql_query(
    f"SELECT * FROM covid_cases_deaths_europe_daily",
    conn
)
df['date'] = pd.to_datetime(
    df['obs_date'],
    format='%Y-%m-%d'
)

# Page title and description
st.title('Tracking COVID19 Cases and Deaths by Country')
st.write("This Dashboard Contains Three Sections:")
st.write("    - Most Recent Daily Metrics;")
st.write("    - Selected Month Metrics;")
st.write("    - Selected Time Range Metrics")
st.write("Please Make Your Choices Accordingly Using the SideBar.")
st.write("---------------------------------")

# CURRENT DAILY VALUES BY COUNTRY ---------------------------------

# Allow user to pick country
ctry = st.sidebar.selectbox(
     'Please Select a Country From the Drop-Down Menu For the Entire Dashboard:',
     (
         'Greece',
         'Italy',
         'Norway',
         'Romania',
         'Austria',
         'Portugal',
         'Poland'
     )
)

# Header
st.write("")
st.header('Most Recently Updated Daily Metrics For ' + ctry)

# Metrics
todays_nums = df[
    df['country'] == ctry
]
todays_nums = todays_nums[
    todays_nums['date'] == todays_nums['date'].max()
]
todays_date = todays_nums[['date']].astype('string').iloc[0][0]
todays_cases = todays_nums[['number_of_covid_cases_daily']].iloc[0][0]
todays_deaths = todays_nums[['number_of_covid_deaths_daily']].iloc[0][0]

st.metric('Last Available Date:', todays_date)
st.metric('Number of Daily Cases:', todays_cases)
st.metric('Number of Daily Deaths:', todays_deaths)
st.write("")
st.write("---------------------------------")

# SELECTED MONTH VALUES BY COUNTRY ---------------------------------

# Allow user to pick year and month
yr = st.sidebar.selectbox(
     'Please Select a Year From the Drop-Down Menu For the Monthly Metrics Section:',
     ('2020',
      '2021',
      '2022')
)

mo = st.sidebar.selectbox(
     'Please Select a Month From the Drop-Down Menu For the Monthly Metrics Section:',
     ('Jan',
      'Feb',
      'Mar',
      'Apr',
      'May',
      'Jun',
      'Jul',
      'Aug',
      'Sep',
      'Oct',
      'Nov',
      'Dec')
)

# Header
st.header(
    mo +
    '-' +
    yr +
    ' Monthly Metrics: Covid Cases and Deaths For ' +
    ctry
)

if len(str(datetime.datetime.strptime(mo, "%b").month)) == 1:
    yrmo = str(yr+'-0'+str(datetime.datetime.strptime(mo, "%b").month))
else:
    yrmo = str(yr+'-'+str(datetime.datetime.strptime(mo, "%b").month))

# Transform Into Monthly Data
df['yearmo'] = df['date'].dt.strftime('%Y-%m').astype('string')
df_ctry_mo = df[
    (df['country'] == ctry) & (df['yearmo'] == yrmo)
]
df_ctry_mo = df_ctry_mo[
    [
        'yearmo',
        'country',
        'number_of_covid_cases_daily',
        'number_of_covid_deaths_daily'
    ]
].groupby(
    [
        'yearmo',
        'country'
    ]
).sum().reset_index()

df_ctry_mo.rename(
    columns={
        "number_of_covid_cases_daily": "number_of_covid_cases_monthly",
        "number_of_covid_deaths_daily": "number_of_covid_deaths_monthly"
    },
    inplace=True
)
month_cases = df_ctry_mo[['number_of_covid_cases_monthly']].iloc[0][0]
month_deaths = df_ctry_mo[['number_of_covid_deaths_monthly']].iloc[0][0]

st.metric('Number of Monthly Cases:', month_cases)
st.metric('Number of Monthly Deaths:', month_deaths)
st.write("")
st.write("---------------------------------")

# SELECTED TIME RANGE VALUES BY COUNTRY ---------------------------------

# Allow user to pick
start_period = st.sidebar.slider(
    "Please Select a Start Date For the Custom Time Range Section:",
    value=datetime.datetime(2020, 1, 1),
    min_value=datetime.datetime(2020, 1, 1),
    max_value=datetime.datetime(2023, 1, 1),
    format="MM/DD/YY")

end_period = st.sidebar.slider(
    "Please Select a End Date For the Custom Time Range Section:",
    value=datetime.datetime(2022, 1, 1),
    min_value=datetime.datetime(2020, 1, 1),
    max_value=datetime.datetime(2023, 1, 1),
    format="MM/DD/YY")

# Header
st.header(
    'Custom Time Range: Number of Covid Cases and Deaths For ' +
    ctry +
    ' Between ' +
    str(start_period)[:-9] +
    ' And ' +
    str(end_period)[:-9]
)

# Data Transformation
df_custom_range = df[
    (df['country'] == ctry) & (df['date'] >= start_period) & (df['date'] <= end_period)
]
df_custom_range_grp = df_custom_range[
    [
        'country',
        'number_of_covid_cases_daily',
        'number_of_covid_deaths_daily'
    ]
].groupby(
    ['country']
).sum().reset_index()

df_custom_range_grp.rename(
    columns={
        "number_of_covid_cases_daily": "number_of_covid_cases_custom",
        "number_of_covid_deaths_daily": "number_of_covid_deaths_custom"
    },
    inplace=True
)
custom_cases = df_custom_range_grp[['number_of_covid_cases_custom']].iloc[0][0]
custom_deaths = df_custom_range_grp[['number_of_covid_deaths_custom']].iloc[0][0]

st.metric('Number of Cases:', custom_cases)
st.metric('Number of Deaths:', custom_deaths)
st.write("")

# Breakdown
st.header(
    'Custom Time Range: Detailed Breakdown of Number of Covid Cases and Deaths For ' +
    ctry +
    " Between " +
    str(start_period)[:-9] +
    " and " +
    str(end_period)[:-9]
)

st.dataframe(
    df_custom_range[
        [
            'date',
            'number_of_covid_cases_daily',
            'number_of_covid_deaths_daily'
        ]
    ].reset_index(drop=True)
)
