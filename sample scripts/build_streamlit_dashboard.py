import os
import pandas as pd
import pathlib
import streamlit as st
from trino import dbapi
from trino import constants
from trino.auth import BasicAuthentication
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import scipy.stats

# Page title and description
st.title('Tracking Covid Cases and Deaths in a Randomly Selected Set of European Countries')
st.write('The dashboard allows the user to specify the time series that they would like to see, with a drop down menu'
         ' for the country and type of metrics. It also allows the user to specify the time range they would like to see'
         'the time series chart for.')

# Sub-header
st.header('Number of Monthly Covid Cases and Deaths')

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

# Fetch data
df = pd.read_sql_query(
    f"SELECT * FROM covid_cases_deaths_europe_daily", conn
)

# Transform into datetime Series
df['date'] = pd.to_datetime(df['obs_date'], format='%Y-%m-%d')

# Transform into monthly data
df['yearmo'] = df['date'].dt.strftime('%Y-%m')
df = df.copy()[['yearmo', 'country', 'number_of_cases_daily', 'number_of_deaths_daily']].groupby(['yearmo', 'country']).max()

# Allow user to pick country
ctry = st.selectbox(
     'Please select a country from the drop-down menu below:',
     ('Greece',
      'Italy',
      'Norway',
      'Romania',
      'Austria',
      'Portugal',
      'Poland'))

st.write('You selected:', ctry)
st.dataframe(df)

# Plot # COVID cases vs no-scent complaints over time
fig, ax = plt.subplots(figsize=(12, 6))
ax2 = ax.twinx()
ax.set_title('Covid Cases and Deaths')
ax.plot(df['yearmo'], df['number_of_cases_daily'], color='green')
ax2.plot(df['yearmo'], df['number_of_deaths_daily'], color='red')
ax.set_ylabel('Number of Cases')
ax2.set_ylabel('Number of Deaths')
ax.legend(['Covid Cases'])
ax2.legend(['Covid Deaths'], loc='upper center')
ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=range(1, 13)))
ax.xaxis.set_minor_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(
    mdates.ConciseDateFormatter(ax.xaxis.get_major_locator()))
plt.tight_layout()
st.pyplot(fig=plt)
