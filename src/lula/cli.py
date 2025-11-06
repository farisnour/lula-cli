from datetime import datetime, UTC

import click

from lula import utils
from lula import gitlab_utils


@click.group()
def cli():
    """Lula - A CLI tool to manage pull requests from the terminal"""
    pass


@cli.group()
def mr():
    """MR subcommands"""
    pass


@mr.command()
@click.option(
    "--asc", is_flag=True, help="Sort merge requests in ascending order (oldest first)"
)
def list(asc):
    """List your open pull/merge requests"""
    try:
        mrs = gitlab_utils.get_user_open_mrs(asc=asc)

        if not mrs:
            click.echo("No open merge requests found.")
            return

        projects = gitlab_utils.get_projects_from_mrs(mrs)

        mr_counter = 1
        for project_name, project_mrs in projects:
            click.echo(
                f"{project_name} ({len(project_mrs)} MR{'s' if len(project_mrs) != 1 else ''})"
            )
            click.echo("─" * (len(project_name) + 20))

            now = datetime.now(UTC)
            for mr in project_mrs:
                updated_at_str = utils.get_relative_time(mr["updated_at"], now)

                click.echo(f"{mr_counter}. {mr['title']}")
                click.echo(f"   Branch: {mr['source_branch']} → {mr['target_branch']}")
                click.echo(f"   Author: {mr['author']}")
                click.echo(f"   Updated: {updated_at_str}")
                click.echo(f"   URL: {mr['web_url']}")
                click.echo()
                mr_counter += 1

    except click.ClickException:
        raise
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()


@mr.command()
def comments():
    """List PR comments"""
    click.echo("Listing PR comments...")
    click.echo("not yet implemented")


def main():
    cli.add_command(list)
    cli()
