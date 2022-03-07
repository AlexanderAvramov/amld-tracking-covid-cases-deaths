from vdk.api.job_input import IJobInput


def run(job_input: IJobInput):
    """
    This helper script could be used to reset the job properties in case one wants to reingest
    the full data from the sources.
    """

    props = job_input.get_all_properties()
    props = {}
    job_input.set_all_properties(props)
