import logging
from pathlib import Path
from types import SimpleNamespace

import typer

from fangen.config import load_config, Config
from fangen.cosplay2.client import Cosplay2Client
from fangen.db.factory import get_session
from fangen.db.make_db import make_db
from fangen.plan.make_plan import make_plan

from rich import print

app = typer.Typer()
logging.basicConfig(level=logging.INFO)


def print_logo() -> None:
    print("""███████╗ █████╗ ███╗   ██╗ ██████╗ ███████╗███╗   ██╗""")
    print("""██╔════╝██╔══██╗████╗  ██║██╔════╝ ██╔════╝████╗  ██║""")
    print("""█████╗  ███████║██╔██╗ ██║██║  ███╗█████╗  ██╔██╗ ██║""")
    print("""██╔══╝  ██╔══██║██║╚██╗██║██║   ██║██╔══╝  ██║╚██╗██║""")
    print("""██║     ██║  ██║██║ ╚████║╚██████╔╝███████╗██║ ╚████║""")
    print("""╚═╝     ╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝""")


@app.callback()
def main(
    ctx: typer.Context,
    config: Path = typer.Option(
        Path("./config.toml"),
        "--config",
        "-c",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        help="Путь к конфигу",
    ),
):
    print_logo()
    config = load_config(config)
    ctx.obj = SimpleNamespace(config=config)


@app.command(name="make_db", help="Загружает данные из заявок с Cosplay2")
def make_db_command(ctx: typer.Context) -> None:
    config: Config = ctx.obj.config
    c2 = Cosplay2Client(event_name=config.event_name)
    if c2.auth(login=config.email, password=config.password):
        make_db(client=c2, db_path=config.db_path)


@app.command(name="make_plan", help="Заполняет план данными из заявок")
def make_plan_command(
    ctx: typer.Context,
    filepath: Path = typer.Argument(Path("./excel.xlsx"), help="Путь к файлу Excel"),
):
    config: Config = ctx.obj.config
    session = get_session(db_path=config.db_path)
    make_plan(filepath=filepath, session=session, config=config)


if __name__ == "__main__":
    app()
