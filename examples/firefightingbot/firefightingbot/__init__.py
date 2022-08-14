from maubot import Plugin, MessageEvent
from maubot.handlers import command

class FireFightingBot(Plugin):
  @command.passive("fire")
  async def command(self, evt: MessageEvent, match: tuple[str]) -> None:
    await evt.react("🔥")
