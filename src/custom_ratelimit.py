import time

class RateLimiter:
    def __init__(self, calls, period):
        self.calls = calls
        self.period = period
        self.call_times = []

    def is_allowed(self):
        current_time = time.time()
        
        # Remove calls that are outside the rate limit period
        self.call_times = [t for t in self.call_times if current_time - t < self.period]
        
        if len(self.call_times) < self.calls:
            self.call_times.append(current_time)
            return True
        return False

def rate_limit(calls, period):
    def decorator(func):
        rate_limiter = RateLimiter(calls, period)
        
        def wrapper(*args, **kwargs):
            if rate_limiter.is_allowed():
                return func(*args, **kwargs)
            else:
                raise Exception(f"Rate limit exceeded for {func.__name__}")
        
        return wrapper
    return decorator
