from maubot import Plugin, MessageEvent
from maubot.handlers import command


class Echobot(Plugin):
    @command.new(name="echo", must_consume_args=False)
    @command.argument("message", pass_raw=True)
    async def echo_command(self, evt: MessageEvent, message: str) -> None:
        await evt.respond(message)
