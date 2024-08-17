import requests
import time

NUM_REQS = 1000

if __name__ == "__main__":
    start = time.perf_counter()
    for _ in range(NUM_REQS):
        requests.get("http://localhost:8000")

    print("Time taken:", time.perf_counter() - start)
    
