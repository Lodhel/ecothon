from fastapi import Header


class GeneralHeadersModel:
    def __init__(
        self,
        authorization: str | None = Header(None)
    ):
        self.authorization = authorization
