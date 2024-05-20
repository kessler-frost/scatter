import hapless
import signal
from hapless.utils import kill_proc_tree
import typer
import click
import hapless.utils
import os

# Override hapless.utils.kill_proc_tree to use the new_kill function
# which uses SIGINT instead of SIGKILL
old_kill_proc_tree = kill_proc_tree


def sigint_kill(pid=1, sig=signal.SIGINT, include_parent=True):
    old_kill_proc_tree(pid, sig, include_parent)


hapless.utils.kill_proc_tree = sigint_kill


app = typer.Typer(rich_markup_mode="rich", add_completion=False)


@app.callback(invoke_without_command=True)
def no_command_show_status(ctx: typer.Context):
    from hapless.cli import _status

    if ctx.invoked_subcommand is None:
        _status()


@click.command()
@click.pass_context
def up(ctx: click.Context):
    """
    [green] Start the scatter server [/green]
    """

    from hapless.cli import run, hapless

    haps = hapless.get_haps()

    if len(haps) >= 1:
        for hap in haps:
            if hap.active and "fastapi_" in hap.name:
                raise typer.Exit("Only one scatter server should be running at a time")

    command = ("fastapi", "run")

    ctx.invoke(run, cmd=command, name=f"fastapi_{os.getpid()}", check=True)


@click.command()
@click.pass_context
def down(ctx: click.Context):
    """
    [red] Stop the scatter server [/red]
    """

    from hapless.cli import kill

    ctx.invoke(kill, killall=True)


@click.command()
@click.pass_context
def status(ctx: click.Context):
    """
    [blue] Show the status of the scatter server [/blue]
    """

    from hapless.cli import status

    ctx.invoke(status)


@click.command()
@click.pass_context
def clean(ctx: click.Context):
    """
    [red] Cleanup all the haps [/red]
    """

    from hapless.cli import clean

    ctx.invoke(clean)


@click.command()
@click.pass_context
def pause(ctx: click.Context):
    """
    [yellow] Pause the scatter server [/yellow]
    """

    from hapless.cli import pause

    ctx.invoke(pause)


@click.command()
@click.pass_context
def resume(ctx: click.Context):
    """
    [green] Resume the scatter server [/green]
    """

    from hapless.cli import resume

    ctx.invoke(resume)


# Adding all the commands
typer_click_object = typer.main.get_command(app)
typer_click_object.add_command(up, "up")
typer_click_object.add_command(down, "down")
typer_click_object.add_command(status, "status")
typer_click_object.add_command(clean, "clean")
typer_click_object.add_command(pause, "pause")
typer_click_object.add_command(resume, "resume")


if __name__ == "__main__":
    typer_click_object()
