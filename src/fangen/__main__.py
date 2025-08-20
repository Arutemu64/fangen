import logging
from pathlib import Path
from types import SimpleNamespace
from typing import Annotated

import typer
from rich import print
from rich.logging import RichHandler

from fangen.config import Config, load_config
from fangen.cosplay2.client import Cosplay2Client
from fangen.db.factory import get_session
from fangen.db.update_db import make_db
from fangen.excel.update_data import make_data
from fangen.excel.update_plan import make_plan
from fangen.files.download_files import download_files
from fangen.files.move_files import move_files

app = typer.Typer()


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
    config: Annotated[
        Path,
        typer.Option(
            ...,
            "--config",
            "-c",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            resolve_path=True,
            help="Путь к конфигу",
        ),
    ] = Path("./config.toml"),
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
    filepath: Annotated[Path, typer.Argument(help="Путь к файлу Excel")] = Path(
        "./plan.xlsx"
    ),
):
    config: Config = ctx.obj.config
    session = get_session(db_path=config.db_path)
    make_plan(filepath=filepath, session=session, config=config)


@app.command(name="make_data", help="Экспортирует данные заявок в Excel-файл")
def make_data_command(
    ctx: typer.Context,
    filepath: Annotated[Path, typer.Argument(help="Путь к файлу Excel")] = Path(
        "./excel.xlsx"
    ),
):
    config: Config = ctx.obj.config
    session = get_session(db_path=config.db_path)
    make_data(filepath=filepath, session=session, config=config)


@app.command(name="download_files", help="Скачивает файлы заявок")
def download_files_command(
    ctx: typer.Context,
    output_dir: Annotated[Path, typer.Argument(help="Путь к файлу Excel")] = Path(
        "./files"
    ),
):
    config: Config = ctx.obj.config
    session = get_session(db_path=config.db_path)
    output_dir.mkdir(exist_ok=True, parents=True)
    download_files(output_dir=output_dir, session=session, config=config)


@app.command(name="move_files", help="Переносит файлы заявок")
def move_files_command(
    ctx: typer.Context,
    input_dir: Annotated[Path, typer.Argument(help="Путь к файлу Excel")] = Path(
        "./files"
    ),
    output_dir: Annotated[Path, typer.Argument(help="Путь к файлу Excel")] = Path(
        "./stage"
    ),
):
    config: Config = ctx.obj.config
    session = get_session(db_path=config.db_path)
    output_dir.mkdir(exist_ok=True, parents=True)
    move_files(
        input_dir=input_dir, output_dir=output_dir, session=session, config=config
    )


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, handlers=[RichHandler(rich_tracebacks=True)]
    )
    app()
