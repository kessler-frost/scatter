# Notes

- <https://trio.readthedocs.io/en/stable/tutorial.html#tutorial-example-tasks-intro>
- <https://github.com/goodboy/tractor/issues?q=is%3Aissue+is%3Aopen+ray>
- <https://trio.readthedocs.io/en/stable/awesome-trio-libraries.html>
- <https://github.com/richardsheridan/trio-parallel>
- <https://anyio.readthedocs.io/en/stable/basics.html#running-async-programs>
- <https://redis.readthedocs.io/en/stable/index.html>
- <https://github.com/taylorhakes/python-redis-cache>
- <https://jcristharif.com/msgspec/structs.html#structs>

## Techstack (transient)

- msgspec -> for typed serialization of function args/kwargs derived automatically from function's annotations/type hints
- Redis and Diskcache -> to store the function blobs and other things
- Possibly switch the zeroapi workers to MPIRE instead of multiprocessing -> gives support for shared objects without copying/serialization

## References and misc

- Opinionated library
- Took inspiration from ZeroAPI Python
- ⁠⁠I liked trio's philosophy of "no .get()" type of mechanisms - which is extended in 'tractor'
- ⁠⁠Would like to avoid using cli as much as possible - discourages ease of trying - something ray and dask do pretty well
- ⁠⁠Avoid using asyncio as that puts a lot of overhead on the dev - also makes it difficult for them to use non-async aware libraries as they will block the event loop
- Will try to keep things modular so all the parts, such as task queuing, function storage backend, serialization remains abstracted and swappable
- Some libraries:
  - dramatiq and huey
  - ⁠redis and diskcache
  - ⁠msgspec is sure pretty much
- no storage of results or args/kwargs after execution completes and they’re sent back
- target is to manage as many things as possible from within python itself
