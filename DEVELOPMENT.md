# Development

## Building the project

Download uv if not already installed:

```shell
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Install the local project and its dependencies into a local virtual environment:

```shell
uv pip install -e . && source .venv/bin/activate

lula --help
```

## Adding dependencies

To add a new library as a dependency:

```shell
uv add "newlibrary~=1.2.3"
```

## Testing changes

Since project was installed in editable mode with `-e` local changes take effect right away:

```shell
lula --help
```

<!--
To run the unit tests:

```shell
pytest .
```
-->
