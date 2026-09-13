"""Buyruqlar: `python manage.py sync-sections` va hokazo."""

import asyncio
import sys


async def _sync_sections() -> None:
    from app import db as database
    from app.services.sections import sync_sections

    database.init_engines()
    async for session in database.get_db():
        result = await sync_sections(session)
        print(f"Tayyor: {result['created']} ta yangi bo'lim, {result['updated']} ta yangilandi.")
    await database.dispose_engines()


COMMANDS = {"sync-sections": _sync_sections}

if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else ""
    if name not in COMMANDS:
        print("Buyruqlar:", ", ".join(COMMANDS))
        sys.exit(2)
    asyncio.run(COMMANDS[name]())
