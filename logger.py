import json
from logging import basicConfig, getLogger, DEBUG, INFO, Formatter, root
from logging.handlers import RotatingFileHandler
from logging import StreamHandler
from logging.config import dictConfig
from io import StringIO
from prompt_toolkit.formatted_text import ANSI, to_formatted_text
from rich.logging import RichHandler

#console = Console(file=StringIO(), force_terminal=True, color_system="truecolor")

logger = getLogger('bot')

interact_logger = getLogger("interactions")

with open('conf/logging.json', 'r') as f:
    log_conf = json.load(f)

dictConfig(log_conf)

logger.addHandler(RichHandler(rich_tracebacks=True))
getLogger("discord").addHandler(RichHandler(level="INFO",rich_tracebacks=True))
getLogger("stuff").addHandler(RichHandler(level="DEBUG",rich_tracebacks=True))
