from rq import Queue
from rq.registry import (
    StartedJobRegistry,
    FailedJobRegistry,
    FinishedJobRegistry,
    DeferredJobRegistry,
    ScheduledJobRegistry,
)
from rq.job import Job

from redis_connection import redis_conn


QUEUE_NAME = "resume_queue"

queue = Queue(QUEUE_NAME, connection=redis_conn)


def print_jobs(title, job_ids):
    print(f"\n===== {title} ({len(job_ids)}) =====")

    if not job_ids:
        print("No jobs")
        return

    for job_id in job_ids:
        try:
            job = Job.fetch(job_id, connection=redis_conn)

            print(f"""
Job ID      : {job.id}
Status      : {job.get_status()}
Function    : {job.func_name}
Created At  : {job.created_at}
Started At  : {job.started_at}
Ended At    : {job.ended_at}
Args        : {job.args}
Kwargs      : {job.kwargs}
""")
        except Exception as e:
            print(f"{job_id} -> {e}")


print("=" * 70)
print(f"Queue Name : {QUEUE_NAME}")
print(f"Queue Size : {queue.count}")
print("=" * 70)

# Jobs currently waiting
queued_jobs = [job.id for job in queue.jobs]
print_jobs("Queued Jobs", queued_jobs)

# Started
started_registry = StartedJobRegistry(QUEUE_NAME, connection=redis_conn)
print_jobs("Started Jobs", started_registry.get_job_ids())

# Failed
failed_registry = FailedJobRegistry(QUEUE_NAME, connection=redis_conn)
print_jobs("Failed Jobs", failed_registry.get_job_ids())

# Finished
finished_registry = FinishedJobRegistry(QUEUE_NAME, connection=redis_conn)
print_jobs("Finished Jobs", finished_registry.get_job_ids())

# Deferred
deferred_registry = DeferredJobRegistry(QUEUE_NAME, connection=redis_conn)
print_jobs("Deferred Jobs", deferred_registry.get_job_ids())

# Scheduled
scheduled_registry = ScheduledJobRegistry(QUEUE_NAME, connection=redis_conn)
print_jobs("Scheduled Jobs", scheduled_registry.get_job_ids())