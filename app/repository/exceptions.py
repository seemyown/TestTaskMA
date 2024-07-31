from uuid import UUID


class FileAlreadyExistsDB(Exception):
    """Ошибка: Файл уже существует"""
    def __init__(self, uid: UUID):
        super().__init__(f"Файл с {uid} уже существует.")


class PathNotFoundDB(Exception):
    """Ошибка: Локальный путь до файла не найден"""
    def __init__(self, uid: UUID):
        super().__init__(
            f"Путь для файла с {uid=} не существует."
        )


class FileNotFoundDB(Exception):
    """Ошибка: Файл не найден"""
    def __init__(self, uid: UUID):
        super().__init__(
            f"Файл с {uid=} не найден."
        )
