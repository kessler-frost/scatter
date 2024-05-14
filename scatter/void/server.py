from zero import ZeroServer


app = ZeroServer(port=4242)


@app.register_rpc
def echo(msg: str) -> str:
    return msg


@app.register_rpc
async def hello_world() -> str:
    return "hello world"


if __name__ == "__main__":
    app.run()
