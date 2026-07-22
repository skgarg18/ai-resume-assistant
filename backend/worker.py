from rq import SimpleWorker
from rq_queue.redis_connection import redis_conn

# Import your jobs
import jobs.resume_job

worker = SimpleWorker(
    ["resume_queue"],
    connection=redis_conn,
)

worker.work()

