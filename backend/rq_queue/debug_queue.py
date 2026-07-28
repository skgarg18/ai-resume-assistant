from rq import Queue
from rq.job import Job
from rq.registry import (
    DeferredJobRegistry,
    FailedJobRegistry,
    FinishedJobRegistry,
    ScheduledJobRegistry,
    StartedJobRegistry,
)

from redis_connection import redis_conn
from utils.log_utils import bind_logger


logger = bind_logger(component="queue_monitor")

QUEUE_NAME = "resume_queue"

queue = Queue(QUEUE_NAME, connection=redis_conn)


def log_jobs(title, job_ids):
    """
    Log details of jobs present in a registry.
    """

    logger.info("===== {} ({}) =====", title, len(job_ids))

    if not job_ids:
        logger.info("No jobs")
        return

    for job_id in job_ids:
        try:
            job = Job.fetch(job_id, connection=redis_conn)

            logger.info(
                "\n"
                "Job ID      : {}\n"
                "Status      : {}\n"
                "Function    : {}\n"
                "Created At  : {}\n"
                "Started At  : {}\n"
                "Ended At    : {}\n"
                "Args        : {}\n"
                "Kwargs      : {}\n",
                job.id,
                job.get_status(),
                job.func_name,
                job.created_at,
                job.started_at,
                job.ended_at,
                job.args,
                job.kwargs,
            )

        except Exception:
            logger.exception(
                "Failed to fetch job details | job_id={}",
                job_id,
            )


logger.info("=" * 70)
logger.info("Queue Name : {}", QUEUE_NAME)
logger.info("Queue Size : {}", queue.count)
logger.info("=" * 70)

# Jobs currently waiting
queued_jobs = [job.id for job in queue.jobs]
log_jobs("Queued Jobs", queued_jobs)

# Started
started_registry = StartedJobRegistry(
    QUEUE_NAME,
    connection=redis_conn,
)
log_jobs("Started Jobs", started_registry.get_job_ids())

# Failed
failed_registry = FailedJobRegistry(
    QUEUE_NAME,
    connection=redis_conn,
)
log_jobs("Failed Jobs", failed_registry.get_job_ids())

# Finished
finished_registry = FinishedJobRegistry(
    QUEUE_NAME,
    connection=redis_conn,
)
log_jobs("Finished Jobs", finished_registry.get_job_ids())

# Deferred
deferred_registry = DeferredJobRegistry(
    QUEUE_NAME,
    connection=redis_conn,
)
log_jobs("Deferred Jobs", deferred_registry.get_job_ids())

# Scheduled
scheduled_registry = ScheduledJobRegistry(
    QUEUE_NAME,
    connection=redis_conn,
)
log_jobs("Scheduled Jobs", scheduled_registry.get_job_ids())