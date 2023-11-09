import typing
from fastapi import Response, status
from starlette.background import BackgroundTask



class BadRequest(Response):
    def __init__(self, content=''):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, content=content)


class NotFound(Response):
    def __init__(self, content=''):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, content=content)


class Unauthorized(Response):
    def __init__(self, content=''):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, content=content)

class OK(Response):
    def __init__(self, content=''):
        super().__init__(status_code=status.HTTP_200_OK, content=content)

class NoContent(Response):
    def __init__(self):
        super().__init__(status_code=status.HTTP_204_NO_CONTENT)


class InternalServerError(Response):
    def __init__(self):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


class Locked(Response):
    def __init__(self, content=''):
        super().__init__(status_code=status.HTTP_406_NOT_ACCEPTABLE, content=content)


class BestReplyExists(Response):
    def __init__(self, content=''):
        super().__init__(status_code=status.HTTP_406_NOT_ACCEPTABLE, content=content)

class CONFLICT(Response):
    def __init__(self, content= ''):
        super().__init__(content=content, status_code=status.HTTP_409_CONFLICT)