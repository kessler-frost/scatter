import hapless
import signal
from hapless.utils import kill_proc_tree
import typer
import click
import hapless.utils

# Override hapless.utils.kill_proc_tree to use the new_kill function
# which uses SIGINT instead of SIGKILL
old_kill_proc_tree = kill_proc_tree


def new_kill(pid=1, sig=signal.SIGINT, include_parent=True):
    old_kill_proc_tree(pid, sig, include_parent)


hapless.utils.kill_proc_tree = new_kill


app = typer.Typer(no_args_is_help=True)


@app.callback()
def callback():
    """
    Empty callback in order to add the click
    commands to the typer app.
    """
    pass


@click.command()
@click.pass_context
def up(ctx: click.Context):
    from hapless.cli import run

    command = ("python", "../void/server.py")
    ctx.invoke(run, cmd=command, name="scatter_server", check=True)


@click.command()
@click.pass_context
def down(ctx: click.Context):
    from hapless.cli import kill

    ctx.invoke(kill, killall=True)


@click.command()
@click.pass_context
def status(ctx: click.Context):
    from hapless.cli import status

    ctx.invoke(status)


@click.command()
@click.pass_context
def clean(ctx: click.Context):
    from hapless.cli import clean

    ctx.invoke(clean)


typer_click_object = typer.main.get_command(app)
typer_click_object.add_command(up, "up")
typer_click_object.add_command(down, "down")
typer_click_object.add_command(status, "status")
typer_click_object.add_command(clean, "clean")


if __name__ == "__main__":
    typer_click_object()
