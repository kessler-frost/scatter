import typer
from scatter.cli.sync import sync_directory, get_module
import scatter
import os
from rich.progress import Progress, SpinnerColumn, TextColumn

app = typer.Typer(add_completion=False)


@app.callback()
def callback():
    """
    Awesome Portal Gun
    """


@app.command()
def shoot():
    """
    Shoot the portal gun
    """
    typer.echo("Shooting portal gun")


@app.command()
def load():
    """
    Load the portal gun
    """
    typer.echo("Loading portal gun")

@app.command()
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
        app = getattr(app_module, app_name)

        valid_functions = [route.name for route in app.routes]

        progress.update(task_id, description="Loading valid endpoint names ✅")

    sync_directory(dir, valid_functions)
    
