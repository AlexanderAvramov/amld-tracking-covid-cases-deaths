# Table of Contents
- [Purpose](#purpose)
- [Background](#background)
  * [Tracking Covid Cases and Deaths](#tracking-covid-cases-and-deaths)
  * [VDK](#vdk)
    * [Create the Data Job Files](#create-the-data-job-files)
    * [Data Job Code](#data-job-code)
    * [Deploy Data Job](#deploy-data-job)
- [Exercises](#exercises)
- [Lessons Learned](#lessons-learned)

<small><i><a href='http://ecotrust-canada.github.io/markdown-toc/'>Table of contents generated with markdown-toc</a></i></small>

## Purpose
The purpose of this scenario is to:
* Build upon what was already covered in scenario 1
* Create a data job on the cloud
* Load extracted data to a configured DB in an incremental fashion
* Read clean data from a cloud database
* Present the results in an interactive Streamlit dashboard
* Schedule data job executions

## Background
### Tracking Covid Cases and Deaths
The example tracks Covid cases and deaths for a set of randomly selected European countries.

The example uses the functionalities of VDK to create and execute on schedule the data job that ingests the
raw data into a database, performs transformations, and loads the clean data into a database. Lastly, we will 
build a Streamlit dashboard to showcase the results.

The daily COVID-19 data for Europe is fetched using an [API](https://github.com/M-Media-Group/Covid-19-API).

### VDK 
The Versatile Data Kit framework allows you to implement automated pull ingestion and batch data processing.

#### Create the Data Job Files
Data Job directory can contain any files, however there are some files that are treated in a specific way:

* SQL files (.sql) - called SQL steps - are directly executed as queries against your configured database;
* Python files (.py) - called Python steps - are Python scripts that define run function that takes as argument the job_input object;
* config.ini is needed in order to configure the Job. This is the only file required to deploy a Data Job;
* requirements.txt is an optional file needed when your Python steps use external python libraries.

Delete all files you do not need and replace them with your own.

#### Data Job Code
VDK supports having many Python and/or SQL steps in a single Data Job. Steps are executed in ascending alphabetical order based on file names.
Prefixing file names with numbers makes it easy to have meaningful file names while maintaining the steps' execution order.

Run the Data Job from a Terminal:
* Make sure you have vdk installed. See Platform documentation on how to install it.
```
vdk run <path to Data Job directory>
```

#### Deploy Data Job
When a Job is ready to be deployed in a Versatile Data Kit runtime (cloud):
Run the command below and follow its instructions (you can see its options with `vdk --help`)
```python
vdk deploy
```

## Exercises
Please open up MyBinder to get started on the exercises!

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/versatile-data-kit-amld/tracking-covid-cases-deaths-example-unsolved/HEAD?labpath=setup.ipynb)

You can find the **solved** MyBinder environment here:

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/versatile-data-kit-amld/tracking-covid-cases-deaths-example-solved/HEAD?labpath=setup.ipynb)

For more information on MyBinder, please visit:

https://mybinder.readthedocs.io 

## Lessons Learned
Through this scenario, you:
* Created a data job on the cloud
* Loaded extracted data to a configured DB in an incremental fashion
* Read clean data from a cloud database
* Presented the results in an interactive Streamlit dashboard
* Scheduled data job executions

Congrats!

## Authored By
Alexander Avramov

Data Analyst at VMware Sofia

[GitHub](https://github.com/AlexanderAvramov) | 
[LinkedIn](https://www.linkedin.com/in/alexander-avramov)
