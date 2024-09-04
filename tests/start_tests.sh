# start the redis instance
hap run -n redis-stack docker run -p 8001:8001 -p 6379:6379 --rm redis/redis-stack

# start the app
hap run -n test-app fastapi run

# sleep for letting the app start
sleep 1

# run tests
pytest -v .

# close the haps by sending SIGINT
hap signal redis-stack 2
hap signal test-app 2
hap kill --all
hap clean --all
