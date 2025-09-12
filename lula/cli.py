import click


@click.group()
@click.version_option(version="0.1.0", prog_name="lula")
def cli():
    """Lula - A CLI tool to manage pull requests from the terminal"""
    pass


@cli.command()
def list():
    """List your open pull requests"""
    click.echo("Listing open pull requests...")
    click.echo("No pull requests found (not yet implemented)")


@cli.command()
def comments():
    """List PR comments"""
    click.echo("Listing PR comments...")
    click.echo("No comments found (not yet implemented)")


def main():
    cli()


if __name__ == "__main__":
    main()
