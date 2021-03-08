import asyncio
import logging

from elaspic2_rest_api.gitlab_monitor import retry_failed_jobs_task

logger = logging.getLogger(__name__)

task_coros = {
    "retry_failed_jobs": retry_failed_jobs_task,
}


async def start_and_monitor_tasks():
    tasks = [
        asyncio.create_task(task_coros[task_name](), name=task_name) for task_name in task_coros
    ]

    try:
        await monitor_tasks(tasks)
    except asyncio.CancelledError:
        for task in tasks:
            task.cancel()


async def monitor_tasks(tasks):
    for task in tasks:
        if task.done():
            error = task.exception()
            if error is not None:
                task.print_stack()
                logger.error("Task %s finished with an error: %s. Restarting", task.name, error)
                tasks[task.name] = asyncio.create_task(task_coros[task.name](), name=task.name)
                task_state = f"error ({type(error)}: {error})"
            else:
                task_state = "done"
        else:
            task_state = "running"
        logger.info("{:40}{:>10}".format(f"Task {task.name}:", task_state))
    await asyncio.sleep(60)
