<div align="center">

# scatter | ![GitHub License](https://img.shields.io/github/license/kessler-frost/scatter?color=blue)

</div>

Redis backed live-reloadable function management in Python.
Edit remote functions in real-time.

## Features

1. Function level version control
2. Live function definition updating for already deployed apps
3. Lightweight with only 2 dependencies: `redis` and `cloudpickle`
4. Minimal network bandwidth usage

## Installation

```bash
pip install scatter
```

## Fundamentals

Note: The commands below are written as if they are run in a Jupyter notebook as an example

- Usually people don't have a readily available Redis instance, and since `scatter` requires that, you can start one locally using [this guide](https://redis.io/learn/howtos/quick-start) - I would recommend using the Docker method to keep things clean. `scatter` should automatically find the instance which by default runs on port 6379.

- Initializing `scatter`
  - Since we use Redis as a backend, either we need to provide a Redis url which includes the username/password of the running redis instance, or the assumption is that there is a running redis instance on `localhost:6479`

```python
import scatter
import os

scatter.init(redis_url=os.getenv("REDIS_URL"))
```

- Tracking a function
  - In order to operate on a function we need to register it with `scatter`, we do that using the `scatter.track` decorator

```python
@scatter.track
def sample_task_1(a: int, b: int):
    return "in the brightest day"
    # return "in the brightest day, in the blackest night"
    # return a * b
```

- Push the function
  - When we need a tracked function to be accessible by someone that wants it, we will need to "push" the function

```python
sample_task_1.push()
```

- Get the function
  - When someone wants to get the function, they can use the `scatter.get` function
  - `scatter` allows anyone with access to the Redis instance, to have access to these tracked functions - so make sure to password protect your Redis instance if it is open to the public
  - Using the name of the function we can get the callable and run it as if it were that exact same function

```python
my_func = scatter.get("sample_task_1")
print(my_func(2, 3))

# Output:
# in the brightest day
```

- Updating the function
  - Now let's say we update the function definition and we want other people to get the updated definition of the function instead, then we will first need to change the definition, "push" the updated definition, and then ask the others to "pull" it.
  - As you might have noticed above, identification of a function is done using the name of the function

```python
@scatter.track
def sample_task_1(a: int, b: int):
    # return "in the brightest day"
    # return "in the brightest day, in the blackest night"
    return a * b

sample_task_1.push()
```

```python
# In the next cell
my_func.pull()
print(my_func(2, 3))

# Output:
# 6
```

- Upgrading/Downgrading the function
  - The previous case was a scenario where we "upgraded" our `my_func` function to the latest version by doing a "pull", now let's see how can we go to an earlier version of our function which returns text instead
  - "downgrading" the function takes the definition to the version just before the currently equipped one, similarly "upgrading" will take it "up" the currently equipped version

```python
my_func.downgrade()
print(my_func(2, 3))

# Output:
# in the brightest day
```

- Deleting the function
  - In case you no longer want to track the function, you can simply call `delete` on it and that will completely remove the function from the Redis instance

```python
my_func.delete()
```

```python
# In a new cell:

# This will error out:
err_func = scatter.get("sample_task_1")

# Error message:
# ...
# KeyError: "Function `sample_task_1` doesn't exist"

```

## License

This project is licensed under [MIT](https://github.com/kessler-frost/scatter?tab=MIT-1-ov-file#readme)
