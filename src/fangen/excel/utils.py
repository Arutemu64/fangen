from pathlib import Path


def check_excel_file(filepath: Path) -> None:
    try:
        with filepath.open("a"):
            pass
    except PermissionError as e:
        msg = "Закройте Excel-файл для обновления"
        raise PermissionError(msg) from e
