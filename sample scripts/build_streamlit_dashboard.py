import os
import pandas as pd
import pathlib
import streamlit as st
from trino import dbapi
from trino import constants
from trino.auth import BasicAuthentication
import matplotlib.pyplot as plt
import seaborn as sns


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
    f"SELECT * FROM covid_cases_deaths_europe_daily", conn
)
df['date'] = pd.to_datetime(df['obs_date'], format='%Y-%m-%d')

# Page title and description
st.title('Tracking Covid Cases and Deaths')
st.header('In a Randomly Selected Set of European Countries')
st.subheader("Please Select a Country From the Drop-Down Menu on the Left")

# Allow user to pick country
ctry = st.sidebar.selectbox(
     'Please select a country from the drop-down menu below:',
     ('Greece',
      'Italy',
      'Norway',
      'Romania',
      'Austria',
      'Portugal',
      'Poland'))

st.metric('You selected:', ctry)

# Sub-header: Current Daily Values
st.header('Most Recent Daily Number of Cases and Deaths')

todays_nums = df[df['country'] == ctry]
todays_nums = todays_nums[todays_nums['date'] == todays_nums['date'].max()]
todays_date = todays_nums[['date']].astype('string').iloc[0][0]
todays_cases = todays_nums[['number_of_covid_cases_daily']].iloc[0][0]
todays_deaths = todays_nums[['number_of_covid_deaths_daily']].iloc[0][0]

st.metric('Last Available Date', todays_date)
st.metric('Number of Daily Cases', todays_cases)
st.metric('Number of Daily Deaths', todays_deaths)

# Sub-header: Monthly Table
st.header('Number of Monthly Covid Cases and Deaths')

# Transform Into Monthly Data
df['yearmo'] = df['date'].dt.strftime('%Y-%m')
df_ctry = df[df['country'] == ctry]
df_ctry = df_ctry[['yearmo', 'country', 'number_of_covid_cases_daily', 'number_of_covid_deaths_daily']].groupby(['yearmo', 'country']).sum().reset_index()
df_ctry.sort_values(by = 'yearmo', ascending=False, inplace=True)
df_ctry.rename(columns={"number_of_covid_cases_daily": "number_of_covid_cases_monthly", "number_of_covid_deaths_daily": "number_of_covid_deaths_monthly"}, inplace=True)
st.dataframe(df_ctry)

# Sub-header: Monthly Chart
st.header('Number of Monthly Covid Cases and Deaths - Chart')
sns.set_theme(style="darkgrid")

fig, ax = plt.subplots(figsize=(12, 6))
ax2 = ax.twinx()
ax.set_title('Covid Cases and Deaths')
ax.plot(df_ctry['yearmo'], df_ctry['number_of_covid_cases_monthly'], color='green')
ax2.plot(df_ctry['yearmo'], df_ctry['number_of_covid_deaths_monthly'], color='red')
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

st.line_chart(df_ctry)