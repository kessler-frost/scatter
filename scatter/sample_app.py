from fastapi import FastAPI
import scatter

app = FastAPI()


@app.get("/")
def read_root():
    sample_task = scatter.assemble("sample_task")
    return {
        "source": sample_task.source,
        "res": sample_task()
    }
