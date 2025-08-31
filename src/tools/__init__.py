from src.tools.execution_engine import shell_command_executor_raw
from src.tools.multimodal_input import read_audio, read_image, read_video
from src.tools.misc import current_time, calculate
from src.tools.web_tools import web_search, scrape_webpage

all_tools = [
    web_search,
    scrape_webpage,
    shell_command_executor_raw,
    read_audio,
    read_image,
    read_video,
    current_time,
    calculate,
]
