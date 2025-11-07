import random
from typing import TypedDict, Union

from discord import Member, Message, User

class HistoryData(TypedDict):
    timestamp: float
    user: Union[Member, User]
    message: str
    response: str

history: list[HistoryData] = []

def response(message: Message):
    author = message.author
    content = message.content
    if author.bot: return