<div align="center">

# scatter | ![GitHub License](https://img.shields.io/github/license/kessler-frost/scatter?color=blue)

</div>

NOTE: This project is currently under heavy development and should be considered pre-alpha

Live-reloadable remote function management in Python.
Edit remote functions with no downtime.

## Features

1. Function level version control
2. Update function definitions for already deployed apps without redeploying
3. Lightweight with very few dependencies
4. Minimal network bandwidth usage

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

## FastAPI integration

[NOTE] The assumption in this example is that there is either an env variable `REDIS_URL` already set which contains the location of a running Redis or a Redis compatible key/value store, or the same is already running at localhost:6379.

`scatter` can now be integrated with your FastAPI app by using the function `scatter.integrate_app` on the `app` object that you create when defining a FastAPI app. For a sample use case, look at the `sample_app/sample_app.py` file:

Let's define some FastAPI routes - `sample_router.py`:

```python
from fastapi.routing import APIRouter

router = APIRouter()


@router.get("/phased/route_1")
async def phased_route_1():
    return {"route_1": "response"}


@router.get("/phased/{route_name}")
async def phased_route_2(route_name: str):
    return {route_name: "my name is!"}


async def not_an_endpoint():
    return "I'm not an endpoint!"
```

In a separate file, let's define our FastAPI application with endpoints `read_root` and `fastapi_integration` - `sample_app.py`:

```python
from fastapi import FastAPI
import scatter
from sample_router import router

app = FastAPI()

@app.get("/")
def read_root():
    return {"Arthur": "Dent"}


@app.get("/integration")
async def fastapi_integration():
    return {"Dirk Gently": 42}

app.include_router(router)

app = scatter.integrate_app(app)
```

As you can see, we are combining everything into a `FastAPI()` object named `app` in this case. Now look at the last line which calls `scatter.integrate_app`, it essentially takes in that `app` object and registers all of the endpoint functions in the app to `scatter` and then returns the app.

Now you can run the app as you normally would, let's say we use FastAPI's own cli command `fastapi run` in a terminal:

```bash
fastapi run .
```

Now if you go to localhost:8000 you'll get a response:

```json
{
    "Arthur": "Dent"
}
```

Now, in a separate terminal in the same directory of `sample_app` if we do:

```bash
scatter sync . sample_app.py
```

And we update the `read_root` function in `sample_app.py` and save the file:

```python
...
@app.get("/")
def read_root():
    return {"Clark": "Kent"}
...
```

And go to localhost:8000 again, we'll see that the response has changed to:

```json
{
    "Clark": "Kent"
}
```

This is a very simple use case of what you can do. Also, let's say you had deplpoyed your app across multiple containers/machines, all of those would be updated as soon as you save your `sample_app.py`. This gives you a lot of power over deploying your apps and making changes to it afterwards without having to redo the entire deployment again and again.

## How is it different than doing [`fastapi dev`](https://fastapi.tiangolo.com/#run-it)?

`fastapi dev` can only update 1 locally running instance of the app, even then it has to shut down and reload the entire app if you change anything in the files that it's watching, for example, say you update the `sample_router.py` file as:

```python
from fastapi.routing import APIRouter

router = APIRouter()


@router.get("/phased/route_1")
async def phased_route_1():
    return {"route_1": "response"}


@router.get("/phased/{route_name}")
async def phased_route_2(route_name: str):
    return {route_name: "my name is!"}


async def not_an_endpoint():
    # return "I'm not an endpoint!"
    # ^^^^^^ previously ^^^^^^^^^^
    return "yellow! I'm a changed function!"
    # ^^^^^^ updated ^^^^^^^^^^^^^

```

In the above case `fastapi dev` will still restart the app even though nothing related to any of the endpoints has changed. Whereas `scatter sync` will not perform the updates - and it never restarts the app as well as updates all of the running instances of the app simultaneously instead of just 1 local instance.

### Caveat

The current caveat of that would be let's say `not_an_endpoint` function was being called inside `phased_route_1`, the updates to the former will not propagate to the app instances since it is not a registered endpoint - hence indirectly failing to update the actual workings of the `phased_route_1` function. I know about this and am figuring out a way to fix it.

## License

This project is licensed under [MIT](https://github.com/kessler-frost/scatter?tab=MIT-1-ov-file#readme)
