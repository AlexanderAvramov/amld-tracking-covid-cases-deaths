# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import requests
import pandas as pd
import random
from vdk.api.job_input import IJobInput

log = logging.getLogger(__name__)


def run(job_input: IJobInput):
    """
    Collect COVID-19 deaths historical data for a random sample of European countries since the start of the pandemic through
    an API call. Ingest this data into a cloud DB table.
    """

    log.info(f"Starting job step {__name__}")

    # If ingesting for the first time, run these cells, otherwise comment them out
    #props = job_input.get_all_properties()
    #props = {}
    #job_input.set_all_properties(props)

    # Create/retrieve the data job property storing latest ingested date for covid_cases_usa_daily table.
    # If the property does not exist, set it to "2020-01-01" (around the start of the pandemic).
    props = job_input.get_all_properties()
    if "last_date_covid" in props:
        pass
    else:
        props["last_date_covid"] = "2020-01-01"
    log.info(f"The data job date is {props}")

    # Initialize URL
    url = "https://covid-api.mmediagroup.fr/v1/history?continent=Europe&status=deaths"

    # Make a GET request to the COVID-19 API
    response = requests.get(url)

    # Check if the request was successful
    response.raise_for_status()
    r = response.json()

    # Get the random sample of countries from cases data set
    ctry_list = ['Greece','Italy','Norway','Romania','Austria','Portugal','Poland']
    log.info(ctry_list)

    # Create an empty Data Frame to be populated
    df_deaths = pd.DataFrame(
        columns = [
            'obs_date', 'number_of_deaths'
        ]
    )

    # Populate the empty Data Frame
    for i in range(len(ctry_list)):    
        dates_deaths = r[ctry_list[i]]['All']['dates']
        
        dates_deaths_dict = {
        'obs_date': [],
        'number_of_deaths':[]
        }
        
        for k,v in dates_deaths.items():
            dates_deaths_dict['obs_date'].append(k)
            dates_deaths_dict['number_of_deaths'].append(v)
        
        df = pd.DataFrame.from_dict(dates_deaths_dict)
        df['country'] = ctry_list[i]
        
        df_deaths = pd.concat(
            [df, df_deaths],
            axis = 0)

    # Keep only the dates which are not present in the table already (based on last_date_covid property)
    df_deaths = df_deaths[df_deaths['obs_date'] > props["last_date_covid"]]

    log.info(df_deaths.head())

    # Ingest the data to the cloud DB
    if len(df_deaths) > 0:
        job_input.send_tabular_data_for_ingestion(
            rows=df_deaths.itertuples(index=False),
            column_names=df_deaths.columns.to_list(),
            destination_table="covid_deaths_europe_daily"
        )

        # Reset the last_date property value to the latest date in the covid source db table
        props["last_date_covid"] = max(df_deaths['obs_date'])
        job_input.set_all_properties(props)

    log.info(f"Success! {len(df_deaths)} rows were inserted in table covid_deaths_europe_daily.")
