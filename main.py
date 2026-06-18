import time
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger

@register("astrbot_plugin_shutup", "DecisionTree", "让机器人在指定聊天环境暂时闭嘴", "1.0.0")
class ShutUpPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.muted = {}

    @filter.command("s")
    async def shutup(self, event: AstrMessageEvent):
        msg = event.message_str.strip()
        parts = msg.split()
        seconds = 30
        if len(parts) > 1:
            try:
                seconds = int(parts[1])
            except ValueError:
                yield event.plain_result("用法: /s <秒数>，默认 30 秒")
                event.stop_event()
                return

        session_key = event.unified_msg_origin

        if seconds <= 0:
            self.muted.pop(session_key, None)
            yield event.plain_result("已取消闭嘴")
            event.stop_event()
            return

        self.muted[session_key] = time.time() + seconds
        yield event.plain_result(f"已闭嘴 {seconds} 秒")
        event.stop_event()

    @filter.on_waiting_llm_request()
    async def on_waiting_llm(self, event: AstrMessageEvent):
        session_key = event.unified_msg_origin
        if session_key in self.muted:
            if time.time() < self.muted[session_key]:
                event.stop_event()
            else:
                del self.muted[session_key]
