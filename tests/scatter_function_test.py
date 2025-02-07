import scatter
from scatter.utils import ASYNC_SLEEP_TIME
import requests
import time
import pytest


def test_basic_push_pull_delete():
    # assumed that a redis instance is running at port 6379

    scatter.init()

    oath = [
        "In the brightest day, ",
        "in the blackest night, ",
        "no evil shal escape my sight, ",
        "for those who worship evil's might, ",
        "beware my power Green Lantern's light."
    ]

    for o in oath:
        @scatter.track
        def super_func():
            return o

        super_func.push()
        
        # Wait for it to update, waiting for 0.01s
        time.sleep(ASYNC_SLEEP_TIME * 10)

        resp = requests.get("http://localhost:8000")
        content = resp.json()["res"]
        assert content == o

    # completely delete this function
    super_func.delete()

    # raise key error on a deleted function
    with pytest.raises(KeyError):
        scatter.get("super_func")
