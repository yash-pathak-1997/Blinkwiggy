from redis import Redis
from rq import Worker
from rq import Connection

# Set up the Redis connection
redis_conn = Redis(host='redis', port=6379, db=0)

if __name__ == '__main__':
    # Use Redis connection in the 'default' queue
    with Connection(redis_conn):
        worker = Worker(['default'])
        worker.work(with_scheduler=True)
