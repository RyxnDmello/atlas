import os


class Constants:
    def __init__(self) -> None:
        self.app = _App()
        self.logger = _Logger()
        self.qdrant = _Qdrant()


class _App:
    def __init__(self) -> None:
        self.APP_NAME = os.getenv("APP_NAME", "DocuMind")


class _Logger:
    def __init__(self) -> None:
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


class _Qdrant:
    def __init__(self) -> None:
        self.QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333")


constants = Constants()
