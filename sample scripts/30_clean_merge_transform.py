# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import pandas as pd
import numpy as np
import logging
import os
import pathlib
import scipy.stats
import matplotlib.pyplot as plt
from vdk.api.job_input import IJobInput

log = logging.getLogger(__name__)

def run(job_input: IJobInput):
    """
    Merge the European countries' cases and deaths and turn them from a cumulative data set to a daily data set.
    """

    log.info(f"Starting job step {__name__}")

    # Create/retrieve the data job property storing latest ingested date for covid_cases_deaths_europe_daily table.
    # If the property does not exist, set it to "2020-01-01" (around the start of the pandemic).
    props = job_input.get_all_properties()
    if "last_date_cases_deaths" in props:
        pass
    else:
        props["last_date_cases_deaths"] = '2020-01-01'
    log.info('ATTENTION!!!')
    log.info(
        f"BEGINNING of {__name__}: THE covid_cases_deaths_europe_daily LAST PREVIOUS DATE IS {props['last_date_cases_deaths']}"
    )

    # Read the cases table and transform to df
    cases = job_input.execute_query(
        f"""
        SELECT *
        FROM covid_cases_europe_daily
        WHERE obs_date > '{props["last_date_cases_deaths"]}'
        """
    )
    df_cases = pd.DataFrame(cases,
                            columns=['obs_date', 'number_of_cases', 'country'])

    # Read the deaths data and transform to df
    deaths = job_input.execute_query(
        f"""
        SELECT * 
        FROM covid_deaths_europe_daily
        WHERE obs_date > '{props["last_date_cases_deaths"]}'
        """
    )
    df_deaths = pd.DataFrame(deaths,
                             columns=['obs_date', 'number_of_deaths', 'country'])

    # Merge the two dataframes
    df_cases_deaths = pd.merge(df_cases,
                               df_deaths,
                               on=['obs_date', 'country'])

    # Calculate new covid cases per day (current numbers are cumulative)
    df_cases_deaths.sort_values(by=['country', 'obs_date'],
                                ascending=False,
                                inplace=True)
    df_cases_deaths['obs_date'] = pd.to_datetime(
        df_cases_deaths['obs_date'], format='%Y-%m-%d'
    )
    df_cases_deaths['number_of_covid_cases_daily'] = df_cases_deaths['number_of_cases'].diff(periods=-1).fillna(0)
    df_cases_deaths['number_of_covid_deaths_daily'] = df_cases_deaths['number_of_deaths'].diff(periods=-1).fillna(0)

    # Fix instances of change of country
    df_cases_deaths["number_of_covid_cases_daily"] = np.where(
        df_cases_deaths["obs_date"] == '2020-01-22',
        df_cases_deaths["number_of_cases"],
        df_cases_deaths["number_of_covid_cases_daily"])

    df_cases_deaths["number_of_covid_deaths_daily"] = np.where(
        df_cases_deaths["obs_date"] == '2020-01-22',
        df_cases_deaths["number_of_deaths"],
        df_cases_deaths["number_of_covid_deaths_daily"])

    # Check if the last ingested day is contained in df_merged_weekly. If yes, remove it.
    df_cases_deaths = df_cases_deaths[
        df_cases_deaths['obs_date'] > props["last_date_cases_deaths"]
    ]

    # Keep only relevant columns
    df_cases_deaths = df_cases_deaths[
        ['obs_date', 'country', 'number_of_covid_cases_daily', 'number_of_covid_deaths_daily']
    ]

    # Turn variables to needed types
    df_cases_deaths['obs_date'] = df_cases_deaths['obs_date'].astype("string")
    df_cases_deaths['number_of_covid_cases_daily'] = df_cases_deaths['number_of_covid_cases_daily'].astype("int")
    df_cases_deaths['number_of_covid_deaths_daily'] = df_cases_deaths['number_of_covid_deaths_daily'].astype("int")
    
    # Print to observe
    log.info(df_cases_deaths.head())

    # If any data is returned, ingest
    if len(df_cases_deaths) > 0:
        job_input.send_tabular_data_for_ingestion(
            rows=df_cases_deaths.values,
            column_names=df_cases_deaths.columns.to_list(),
            destination_table="covid_cases_deaths_europe_daily"
        )
        # Reset the last_date property value to the latest date in the covid source db table
        props["last_date_cases_deaths"] = max(df_cases_deaths['obs_date'])
        job_input.set_all_properties(props)
        log.info(f"Success! {len(df_cases_deaths)} rows were inserted into covid_cases_deaths_europe_daily.")
    else:
        log.info("No new records to ingest.")

    log.info('ATTENTION!!!')
    log.info(
        f"END of {__name__}: THE covid_cases_deaths_europe_daily LAST PREVIOUS DATE IS {props['last_date_cases_deaths']}"
    )
