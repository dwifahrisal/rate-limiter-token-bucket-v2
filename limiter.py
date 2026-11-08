import time
import redis

r = redis.Redis(decode_responses=True)


class TokenBucket:
    def __init__(self, key, capacity=10, refill_rate=1.0):
        self.key = 'tb:' + key
        self.capacity = capacity
        self.refill_rate = refill_rate

    def allow(self):
        now = time.time()
        data = r.hgetall(self.key)
        tokens = float(data.get('tokens', self.capacity))
        last = float(data.get('last', now))
        elapsed = now - last
        tokens = min(self.capacity, tokens + elapsed * self.refill_rate)
        if tokens >= 1:
            tokens -= 1
            r.hset(self.key, mapping={'tokens': tokens, 'last': now})
            r.expire(self.key, int(self.capacity / self.refill_rate) + 10)
            return True
        return False
