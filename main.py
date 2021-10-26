import asyncio
import json
import os
from typing import List

import aiocron
from telethon import TelegramClient
from telethon.tl.custom.file import File
from telethon.tl.functions.messages import GetStickerSetRequest
from telethon.tl.types import InputStickerSetAnimatedEmoji
from telethon.tl.types import InputStickerSetAnimatedEmojiAnimations

from config import api_hash
from config import api_id
from config import bot_token
from config import channel


client = TelegramClient('bot', api_id, api_hash)
client.start(bot_token=bot_token)


def get_stickers() -> List[str]:
    if os.path.exists('stickers.json'):
        with open('stickers.json', 'r+') as f:
            return json.load(f)
    else:
        return []


def save_stickers(stickers: List[str]) -> None:
    unique_stickers = list(set(stickers))
    with open('stickers.json', 'w') as f:
        json.dump(unique_stickers, f, indent=2)


@aiocron.crontab('0 */2 * * *')  # every 2 hours
async def check_stickers() -> None:
    stickers = get_stickers()
    animated_emojis_set = await client(
        GetStickerSetRequest(InputStickerSetAnimatedEmoji()),
    )
    emoji_animations_set = await client(
        GetStickerSetRequest(InputStickerSetAnimatedEmojiAnimations()),
    )

    all_stickers = (
        animated_emojis_set.documents + emoji_animations_set.documents
    )
    for document in all_stickers:
        file = File(document)
        if file.id not in stickers:
            await client.send_message(channel, file.emoji)
            await asyncio.sleep(0.5)
            await client.send_message(channel, file=file.id)
            await asyncio.sleep(2)
            stickers.append(file.id)

    save_stickers(stickers)


loop = asyncio.get_event_loop()
check_stickers.call_func()
try:
    loop.run_forever()
except KeyboardInterrupt:
    print()
