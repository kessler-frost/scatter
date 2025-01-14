<div align="center">

# scatter | ![GitHub License](https://img.shields.io/github/license/kessler-frost/scatter?color=blue)

</div>

Live-reloadable remote function management in Python.

## Installation

```bash
pip install scatter
```

## Fundamentals

Note: The commands below are written as if they are run in a Jupyter notebook

- Usually people don't have a readily available Redis instance, and since `scatter` requires that, you can start one locally using [this guide](https://redis.io/learn/howtos/quick-start) - I would recommend using the Docker method to keep things clean. Once started, you can follow the instruction below, `scatter` should automatically find the instance which by default runs on port 6379.

### 1. Initializing `scatter`

- Since we use Redis as a backend, either we need to provide a Redis url which includes the username/password of the running redis instance, or the assumption is that there is a running redis instance on `localhost:6479`

```python
import scatter
import os

# In case the Redis instance is running locally on localhost:6379
scatter.init()

# In case there is a remote Redis instance running at `$REDIS_URL`
# scatter.init(redis_url=os.getenv("REDIS_URL"))
```

### 2. Tracking a function

- In order to operate on a function we need to register it with `scatter`, we do that using the `scatter.track` decorator

```python
@scatter.track
def sample_task_1(a: int, b: int):
    return "in the brightest day"
    # return "in the brightest day, in the blackest night"
    # return a * b
```

### 3. Push the function

- When we need a tracked function to be accessible by someone that wants it, we will need to "push" the function

```python
sample_task_1.push()
```

### 4. Get the function

- When someone wants to get the function, they can use the `scatter.get` function
- `scatter` allows anyone with access to the Redis instance, to have access to these tracked functions - so make sure to password protect your Redis instance if it is open to the public
- Using the name of the function we can get the callable and run it as if it were that exact same function

```python
my_func = scatter.get("sample_task_1")
print(my_func(2, 3))

# Output:
# in the brightest day
```

### 5. Updating the function

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

### 6. Upgrading/Downgrading the function
  
- The previous case was a scenario where we "upgraded" our `my_func` function to the latest version by doing a "pull", now let's see how can we go to an earlier version of our function which returns text instead
- "downgrading" the function takes the definition to the version just before the currently equipped one, similarly "upgrading" will take it "up" the currently equipped version

```python
my_func.downgrade()
print(my_func(2, 3))

# Output:
# in the brightest day
```

### 7. Deleting the function

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
