from commands.movie import run as movie

from lib.cli import cli

cli.add_command(cmd=movie, name='movie')

if __name__ == "__main__":
    cli()
