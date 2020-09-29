def run_job(data: dict) -> None:
    # 1. Run `sbatch` to submit job and get job id.
    # 2. Monitor using `squeue` until the job with the obtained job id stops running.
    # 3. If results are in the database: success. Else: failure.
    pass
