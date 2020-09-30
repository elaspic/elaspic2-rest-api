from ev2web.types import JobRequest, JobResult, JobState, JobStatus


def create_job(job_id: str, request: JobRequest) -> None:
    return None


def delete_job(job_id: str) -> None:
    pass


def get_job_state(job_id: str) -> JobState:
    return JobState(status=JobStatus.running)


def get_job_result(job_id: str) -> JobResult:
    pass
