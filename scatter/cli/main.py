import typer
from scatter.cli.sync import sync_directory, get_module
import scatter
import os
from rich.progress import Progress, SpinnerColumn, TextColumn

app = typer.Typer(add_completion=False)


@app.callback(no_args_is_help=True)
def callback():
    """
    Scatter CLI
    """
    pass

@app.command(no_args_is_help=True)
def sync(dir: str, app_file_path: str, app_name: str = "app"):
    """
    Sync local changes to function definitions with an already deployed FastAPI app
    """
    scatter.init(redis_url=os.getenv("REDIS_URL"))


    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
    ) as progress:
        task_id = progress.add_task(description="Loading valid endpoint names", total=None)

        # Load the app module
        app_module = get_module(app_name, app_file_path)
        fastapi_app = getattr(app_module, app_name)

        valid_functions = [route.name for route in fastapi_app.routes]

        progress.update(task_id, description="Loading valid endpoint names ✅")

    sync_directory(dir, valid_functions)
    
