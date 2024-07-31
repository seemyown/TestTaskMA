from uuid import UUID


class FileNotFoundLocal(Exception):
    def __init__(self, uid: UUID,  path: str = None):
        if path is None:
            super().__init__(
                f"Путь до файла с {uid=} не найден"
            )
        else:
            super().__init__(
                f"Файл с {uid=} не существует по пути {path}"
            )


class FileNotFound(Exception):
    def __init__(self, uid: UUID):
        super().__init__(f"Файл: {uid} не найден локально")
