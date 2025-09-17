import click
import os
import gitlab
from typing import List, Dict, Any


def get_gitlab_client() -> gitlab.Gitlab:
    """Initialize and return a GitLab client."""
    gitlab_url = os.getenv('GITLAB_URL', 'https://gitlab.com')
    gitlab_token = os.getenv('GITLAB_TOKEN')

    if not gitlab_token:
        raise click.ClickException(
            "GitLab token not found. Please set the GITLAB_TOKEN environment variable.\n"
            "You can get a token from: https://gitlab.com/-/profile/personal_access_tokens"
        )

    return gitlab.Gitlab(gitlab_url, private_token=gitlab_token)


def get_user_open_mrs() -> List[Dict[str, Any]]:
    """Fetch open merge requests for the current user."""
    try:
        gl = get_gitlab_client()

        # Get current user
        user = gl.user
        user_id = user.id

        # Get open merge requests assigned to the user
        mrs = gl.mergerequests.list(
            state='opened',
            assignee_id=user_id,
            per_page=50,
            order_by='updated_at',
            sort='desc'
        )

        # Convert to list of dictionaries for easier handling
        mr_list = []
        for mr in mrs:
            mr_list.append({
                'id': mr.iid,
                'title': mr.title,
                'source_branch': mr.source_branch,
                'target_branch': mr.target_branch,
                'web_url': mr.web_url,
                'created_at': mr.created_at,
                'updated_at': mr.updated_at,
                'author': mr.author['name'],
                'project': mr.project['name']
            })

        return mr_list

    except gitlab.exceptions.GitlabAuthenticationError:
        raise click.ClickException("Authentication failed. Please check your GitLab token.")
    except gitlab.exceptions.GitlabGetError as e:
        raise click.ClickException(f"Failed to fetch merge requests: {e}")
    except Exception as e:
        raise click.ClickException(f"Unexpected error: {e}")


@click.group()
@click.version_option(version="0.1.0", prog_name="lula")
def cli():
    """Lula - A CLI tool to manage pull requests from the terminal"""
    pass


@cli.command()
def list():
    """List your open pull/merge requests"""
    try:
        mrs = get_user_open_mrs()

        if not mrs:
            click.echo("No open merge requests found.")
            return

        click.echo(f"Found {len(mrs)} open merge request(s):\n")

        for i, mr in enumerate(mrs, 1):
            click.echo(f"{i}. {mr['title']}")
            click.echo(f"   Project: {mr['project']}")
            click.echo(f"   Branch: {mr['source_branch']} → {mr['target_branch']}")
            click.echo(f"   Author: {mr['author']}")
            click.echo(f"   Updated: {mr['updated_at']}")
            click.echo(f"   URL: {mr['web_url']}")
            click.echo()

    except click.ClickException:
        raise
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()


@cli.command()
def comments():
    """List PR comments"""
    click.echo("Listing PR comments...")
    click.echo("No comments found (not yet implemented)")


def main():
    cli()


if __name__ == "__main__":
    main()
