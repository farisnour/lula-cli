# Lula - A CLI tool to manage pull requests from the terminal

Lula is a CLI tool to help developers manage their pull requests from the terminal.

## Installation

```bash
pip install lula
```

## Usage

List your open pull/merge requests:

```bash
lula list
```

List PR comments on the current checked-out branch
```bash
lula comments
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
