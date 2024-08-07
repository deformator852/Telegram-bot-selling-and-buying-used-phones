from telethon import TelegramClient, events
from datetime import datetime, timedelta
import asyncio
import aiosqlite
import os

API_ID = ""
API_HASH = ""
DB_PATH = os.path.expanduser("~/bot_database/database.db")

client = TelegramClient("my_bot_session", API_ID, API_HASH)


async def send_message():
    while True:
        advertisements = await get_adv_list()
        for adv in advertisements:
            send_range = int(await get_range(adv))
            last_sent = (
                datetime.strptime(adv[8], "%Y-%m-%d %H:%M:%S")
                if adv[8] is not None
                else None
            )
            groups_range = adv[4]
            groups = await get_groups(groups_range)
            if last_sent is None:
                for group in groups:
                    try:
                        group_id = await get_group_id(group[0])
                        await client.send_file(group_id, adv[3]+"<a href='https://t.me/FlipyMarketBot'>SellYourDevice</a>", caption=adv[1],parse_mode="html")
                        await update_last_sent_time(adv[0])
                    except Exception as e:
                        await client.send_message(
                            "me", f"Error with sending advertisement!Error text: {e}"
                        )

            else:
                current_time = datetime.now()
                if current_time - last_sent >= timedelta(minutes=send_range):
                    groups_range = adv[5]
                    for group in groups:
                        try:
                            group_id = await get_group_id(group[0])
                            await client.send_file(group_id, adv[3], caption=adv[1])
                            await update_last_sent_time(adv[0])
                        except Exception as e:
                            await client.send_message(
                                "me",
                                f"Error with sending advertisement!Error text: {e}",
                            )

        await asyncio.sleep(60)


async def get_groups(groups_range):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            f"SELECT group_link FROM groups WHERE group_range = ?", (groups_range,)
        ) as cursor:
            result = await cursor.fetchall()
            return result


async def update_last_sent_time(task_id):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            f"UPDATE advertisements SET last_sent = ? WHERE id = ?",
            (
                current_time,
                task_id,
            ),
        )
        await db.commit()


async def main():
    async with client:
        await send_message()


async def get_adv_list():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT * FROM advertisements WHERE status = 1"
        ) as cursor:
            rows = await cursor.fetchall()
            return rows


async def day_or_night():
    now = datetime.now().time()
    start_day = datetime.strptime("08:00", "%H:%M").time()
    end_day = datetime.strptime("22:00", "%H:%M").time()
    return start_day <= now < end_day


async def get_range(adv):
    if await day_or_night():
        return adv[5]
    else:
        return adv[6]


async def get_group_id(group_link):
    try:
        if group_link.startswith("https://web.telegram.org/"):
            group_id = group_link.split("/")[-1][1:]
            async for dialog in client.iter_dialogs():
                if (dialog.is_group) and (dialog.id == int(group_id)):
                    return int(dialog.id)
        group = await client.get_entity(group_link)
        return group.id
    except Exception as e:
        print(f"Error getting group ID: {e}")
        return None


if __name__ == "__main__":
    client.start()
    client.loop.run_until_complete(main())
