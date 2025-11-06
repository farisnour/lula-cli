from datetime import datetime, timedelta, UTC

import click

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

            for mr in project_mrs:
                # List the date listing using "X minutes/hours/days/months ago"
                now = datetime.now(UTC)
                time_diff = now - datetime.fromisoformat(mr["updated_at"])
                total_seconds = time_diff.total_seconds()
                updated_at = None

                if time_diff < timedelta(0):
                    raise click.ClickException(
                        f"Error in MR updated_at {updated_at} date is invalid."
                    )
                elif time_diff < timedelta(hours=1):
                    updated_at = f"{int(total_seconds // 60)} minute(s) ago"
                elif time_diff < timedelta(days=1):
                    updated_at = f"{int(total_seconds / 60 // 60)} hour(s) ago"
                elif time_diff < timedelta(days=40):
                    updated_at = f"{int(total_seconds / 60 / 60 // 24)} day(s) ago"
                else:
                    updated_at = (
                        f"{int(total_seconds / 60 / 60 / 24 // 30)} month(s) ago"
                    )

                click.echo(f"{mr_counter}. {mr['title']}")
                click.echo(f"   Branch: {mr['source_branch']} → {mr['target_branch']}")
                click.echo(f"   Author: {mr['author']}")
                click.echo(f"   Updated: {updated_at}")
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
