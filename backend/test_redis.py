from redis import Redis

try:
    redis_conn = Redis(host="localhost", port=6379)
    print(redis_conn.ping())
except Exception as e:
    print(e)