from redis import Redis
from rq import Queue

redis_conn = Redis(
    host="localhost",
    port=6379,
)

resume_queue = Queue(
    "resume_queue",
    connection=redis_conn,
)