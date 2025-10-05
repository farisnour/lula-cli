# Lula - A CLI tool to manage pull requests from the terminal

Lula is a CLI tool to manage pull requests in git repositories from the terminal. It currently only supports Gitlab repositories.

<!--
## Installation

```bash
pip install lula
```
-->

## Usage

List your open pull/merge requests:

```bash
lula list
```

## Setup

Before using lula, you need to set up your GitLab token:

1. Create a new token with `read_api` scope
2. Set the token as an environment variable:

```bash
export GITLAB_TOKEN="your_token_here"
```

For self-hosted GitLab instances, also set the GitLab URL:

```bash
export GITLAB_URL="https://your-gitlab-instance.com"
```

## Development

### Building the project

Download uv if not already installed:

```shell
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Install the local project and its dependencies into a local virtual environment:

```shell
uv pip install -e . && source .venv/bin/activate

lula --help
```

Since the project was installed in editable mode with `-e` local changes take effect right away.

### Adding dependencies

To update or add a new library as a dependency:

```shell
uv add "newlibrary~=1.2.3"
```

<!--
To run the unit tests:

```shell
pytest .
```
-->
