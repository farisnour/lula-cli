import os
import subprocess
from typing import List, Dict, Any

import click
from gitlab import Gitlab
from gitlab.exceptions import GitlabAuthenticationError, GitlabGetError


def get_gitlab_url_from_git() -> str:
    """Extract GitLab URL from git remote origin configuration."""
    try:
        # Get the remote origin URL
        result = subprocess.run(
            ['git', 'config', '--get', 'remote.origin.url'],
            capture_output=True,
            text=True,
            check=True,
        )
        origin_url = result.stdout.strip()

        # Check if this is a GitHub repository
        if 'github.com' in origin_url:
            raise click.ClickException("Github projects are not yet supported")

        # Parse the URL to extract the GitLab instance URL
        if origin_url.startswith('git@'):
            # SSH format: git@gitlab.example.com:user/repo.git
            # Extract the hostname part
            host_part = origin_url.split('@')[1].split(':')[0]
            return f"https://{host_part}"
        elif origin_url.startswith('https://'):
            # HTTPS format: https://gitlab.example.com/user/repo.git
            # Extract the base URL
            parts = origin_url.split('/')
            if len(parts) >= 3:
                return f"{parts[0]}//{parts[2]}"

        # If we can't parse the URL, return the default
        return 'https://gitlab.com'

    except (subprocess.CalledProcessError, FileNotFoundError, IndexError):
        # If git command fails or URL can't be parsed, return default
        return 'https://gitlab.com'


def get_gitlab_client() -> Gitlab:
    """Initialize and return a GitLab client."""
    gitlab_url = os.getenv('GITLAB_URL')
    if not gitlab_url:
        gitlab_url = get_gitlab_url_from_git()

    gitlab_token = os.getenv('GITLAB_TOKEN')

    if not gitlab_token:
        raise click.ClickException(
            f"GitLab token not found. Please set the GITLAB_TOKEN environment variable.\n"
            f"You can get a token from: {gitlab_url}/-/profile/personal_access_tokens"
        )

    return Gitlab(gitlab_url, private_token=gitlab_token)


def get_project_name_from_mr(gl: Gitlab, mr) -> str:
    """Get project name from merge request object using multiple approaches."""
    attributes = getattr(mr, 'attributes', {}) or {}

    # Get project name - try multiple approaches
    project_name = ''

    # Try to get from attributes first
    project_info = attributes.get('project', {}) or {}
    if project_info:
        project_name = project_info.get('name', '')

    # If not found, try to get from the mr object directly
    if not project_name and hasattr(mr, 'project'):
        project_obj = getattr(mr, 'project', {})
        if isinstance(project_obj, dict):
            project_name = project_obj.get('name', '')
        elif hasattr(project_obj, 'name'):
            project_name = project_obj.name

    # If still not found, try to get project info from GitLab API
    if not project_name and hasattr(mr, 'project_id'):
        try:
            project_id = getattr(mr, 'project_id', None)
            if project_id:
                project = gl.projects.get(project_id)
                project_name = project.name
        except:
            pass

    return project_name


def get_user_open_mrs(desc: bool = False) -> List[Dict[str, Any]]:
    """Fetch open merge requests assigned to or authored by the current user."""
    try:
        gl = get_gitlab_client()
        # Ensure authentication is performed so that gl.user is populated
        gl.auth()

        # Get current user
        user = gl.user
        if user is None:
            raise click.ClickException("Unable to determine current user from GitLab. Please verify your token scopes.")
        user_id = user.id

        # Get open merge requests assigned to the user or authored by the user
        assigned_mrs = gl.mergerequests.list(
            state='opened',
            scope='assigned_to_me',
            per_page=50,
            order_by='created_at',
            with_labels_details=True,
        )

        authored_mrs = gl.mergerequests.list(
            state='opened',
            author_id=user_id,
            per_page=50,
            order_by='created_at',
            with_labels_details=True,
        )

        # Combine and deduplicate MRs (in case user is both author and assignee)
        mr_ids = set()
        mrs = []
        for mr in assigned_mrs + authored_mrs:
            if mr.iid not in mr_ids:
                mr_ids.add(mr.iid)
                mrs.append(mr)

        # Sort by creation date
        mrs.sort(key=lambda mr: getattr(mr, 'created_at', ''), reverse=desc)

        # Convert to list of dictionaries for easier handling
        mr_list = []
        for mr in mrs:
            attributes = getattr(mr, 'attributes', {}) or {}
            author_name = (attributes.get('author') or {}).get('name')

            # Get project name either from the merge request object or from the GitLab API
            project_name = get_project_name_from_mr(gl, mr)

            mr_list.append({
                'id': getattr(mr, 'iid', None),
                'title': getattr(mr, 'title', ''),
                'source_branch': getattr(mr, 'source_branch', ''),
                'target_branch': getattr(mr, 'target_branch', ''),
                'web_url': getattr(mr, 'web_url', ''),
                'created_at': getattr(mr, 'created_at', ''),
                'updated_at': getattr(mr, 'updated_at', ''),
                'author': author_name or '',
                'project': project_name or 'Unknown Project'
            })

        return mr_list

    except GitlabAuthenticationError:
        raise click.ClickException("Authentication failed. Please check your GitLab token.")
    except GitlabGetError as e:
        raise click.ClickException(f"Failed to fetch merge requests: {e}")
    except Exception as e:
        raise click.ClickException(f"Unexpected error: {e}")


def get_projects_from_mrs(mrs: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Get projects from merge requests."""
    projects = {}
    for mr in mrs:
        project_name = mr['project']
        if project_name not in projects:
            projects[project_name] = []
        projects[project_name].append(mr)

    # Sort projects alphabetically
    return sorted(projects.items())


@click.group()
@click.version_option(version="0.1.0", prog_name="lula")
def cli():
    """Lula - A CLI tool to manage pull requests from the terminal"""
    pass


@cli.command()
@click.option('--desc', is_flag=True, help='Sort merge requests in descending order (newest first)')
def list(desc):
    """List your open pull/merge requests"""
    try:
        mrs = get_user_open_mrs(desc=desc)

        if not mrs:
            click.echo("No open merge requests found.")
            return

        projects = get_projects_from_mrs(mrs)

        mr_counter = 1
        for project_name, project_mrs in projects:
            click.echo(f"{project_name} ({len(project_mrs)} MR{'s' if len(project_mrs) != 1 else ''})")
            click.echo("─" * (len(project_name) + 20))

            for mr in project_mrs:
                click.echo(f"{mr_counter}. {mr['title']}")
                click.echo(f"   Branch: {mr['source_branch']} → {mr['target_branch']}")
                click.echo(f"   Author: {mr['author']}")
                click.echo(f"   Updated: {mr['updated_at']}")
                click.echo(f"   URL: {mr['web_url']}")
                click.echo()
                mr_counter += 1

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
