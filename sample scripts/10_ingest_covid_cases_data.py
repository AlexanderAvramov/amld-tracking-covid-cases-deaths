# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import requests
import pandas as pd
import random
import time
from vdk.api.job_input import IJobInput

log = logging.getLogger(__name__)


def run(job_input: IJobInput):
    """
    Collect COVID-19 historical data for the number of cases per day in a randomly selected set of European countries
    since the start of the pandemic through an API call. Ingest this data into a table in a cloud Trino database.
    """

    log.info(f"Starting job step {__name__}")

    # Create/retrieve the data job property storing the latest ingested date for the covid_cases_europe_daily table.
    # If the property does not exist, set it to "2020-01-01" (around the start of the pandemic).
    props = job_input.get_all_properties()
    if "last_date_covid_cases" in props:
        pass
    else:
        props["last_date_covid_cases"] = "2020-01-01"
    log.info("ATTENTION!!!")
    log.info(
        f"BEGINNING OF {__name__}: THE covid_cases_europe_daily LAST INGESTED DATE IS {props['last_date_covid_cases']}")

    # Initialize URL
    url = "https://covid-api.mmediagroup.fr/v1/history?continent=Europe&status=confirmed"

    # Make a GET request to the COVID-19 API
    response = requests.get(url)

    # Check if the request was successful
    response.raise_for_status()

    # Create a list of countries to iterate over
    r = response.json()
    ctry_list = [
        'Greece',
        'Italy',
        'Norway',
        'Romania',
        'Austria',
        'Portugal',
        'Poland'
    ]

    # Create an empty data frame to house data
    df_cases = pd.DataFrame(
        columns=[
            'obs_date',
            'number_of_cases'
        ]
    )

    # Iterate through the country list while populating the empty dataframe
    for i in range(len(ctry_list)):
        dates_cases = r[ctry_list[i]]['All']['dates']

        dates_cases_dict = {
            'obs_date': [],
            'number_of_cases': []
        }

        for k, v in dates_cases.items():
            dates_cases_dict['obs_date'].append(k)
            dates_cases_dict['number_of_cases'].append(v)

        df = pd.DataFrame.from_dict(dates_cases_dict)
        df['country'] = ctry_list[i]

        df_cases = pd.concat(
            [df,
             df_cases],
            axis=0)

    # Keep only the dates which are not present in the table already (based on last_date_covid_cases property)
    df_cases = df_cases[
        df_cases['obs_date'] > props["last_date_covid_cases"]
        ]

    log.info(f"The total number of rows to be ingested to covid_cases_europe_daily is: {len(df_cases)}.")
    log.info(df_cases)

    # Ingest the data to the cloud DB
    if len(df_cases) > !!! ENTER VALUE HERE:
        job_input.send_tabular_data_for_ingestion(
            rows=df_cases.values,
            column_names=df_cases.columns.to_list(),
            destination_table="!!! ENTER NAME HERE" # PLEASE NOTE: THE TABLE NAME NEEDS TO BE WITHIN QUOTATIONS !!!
        )

        # Reset the last_date property value to the latest date in the covid source db table
        props["last_date_covid_cases"] = max(df_cases['obs_date'])
        job_input.set_all_properties(props)

    log.info(f"Success! {len(df_cases)} rows were inserted in table covid_cases_europe_daily.")
    log.info("ATTENTION!!!")
    log.info(f"END OF {__name__}: THE covid_cases_europe_daily LAST INGESTED DATE IS {props['last_date_covid_cases']}")
