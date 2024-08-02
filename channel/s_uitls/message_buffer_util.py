# message_buffer.py
import threading
import time
from common.log import logger
import random

from config import conf


class MessageBuffer:
    def __init__(self, max_delay=10):
        self.messages = {}
        if conf().get("delay_msg_time") > 0:
            self.delay = conf().get("delay_msg_time")
        else:
            self.delay = max_delay
        self.lock = threading.Lock()
        self.callbacks = {}
        self.uid_delays = {}  # 存储每个uid对应的延迟时间

    def add_content(self, type, uid, content, cmsg, callback=None):
        key = f"{type}{uid}"
        with self.lock:
            if key not in self.messages:
                self.messages[key] = ""
                self.callbacks[key] = callback
                # 在指定范围内随机选择延迟时间
                self.uid_delays[key] = random.randint(max(0, self.delay - 10), self.delay)
                # self.delay = random.randint(max(0, self.delay - 10), self.delay)
                logger.debug(f"Starting delay for {key} with random delay of {self.uid_delays[key]} seconds.")
                threading.Thread(target=self._process_delay, args=(key, type, uid, cmsg, self.uid_delays[key])).start()
            else:
                logger.debug(f"Content added to existing key {key}.")

            self.messages[key] += content + "\n"

    def _process_delay(self, key, type, uid, cmsg, delay):
        for i in range(delay, 0, -1):
            logger.debug(f"Delay for {key}: {i} seconds remaining...")
            time.sleep(1)
        with self.lock:
            if key in self.messages:
                content = self.messages[key].rstrip("\n")
                logger.debug(f"Delay completed for {key}. Content: {content}")
                if self.callbacks[key]:
                    # 确保在这里传递了 content 参数
                    self.callbacks[key](type, uid, content, cmsg)
                    # logger.debug(f"--------->>>>>>>>>>Content ready: {content}")
                del self.messages[key]
                del self.callbacks[key]
            else:
                logger.debug(f"No content found for {key} after delay.")