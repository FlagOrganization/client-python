from .client import *


def get_client():
    token = ""
    url = ""
    return FlagClient(
        5,
        "http://127.0.0.1:8000/fetch?environment-id=1&project-id=2",
        "5cc3e4b65f37546267bc77964916f2a23d51e3a9"
    )
