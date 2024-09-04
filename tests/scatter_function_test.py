from scatter import scatter, init
from scatter.utils import ASYNC_SLEEP_TIME
import requests
import time


def test_basic_push_pull_delete():
    # Remember to start the redis container at 6379

    init()

    oath = [
        "In the brightest day, ",
        "in the blackest night, ",
        "no evil shal escape my sight, ",
        "for those who worship evil's might, ",
        "beware my power Green Lantern's light."
    ]

    for o in oath:
        @scatter
        def super_func():
            return o

        super_func.push()
        
        # Wait for it to update, waiting for 0.01s
        time.sleep(ASYNC_SLEEP_TIME * 10)

        resp = requests.get("http://localhost:8000")
        content = resp.json()["res"]

        try:
            assert content == o
        except AssertionError:
            # super_func.delete()
            raise

    # super_func.delete()
