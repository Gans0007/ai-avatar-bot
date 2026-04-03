import asyncio
import subprocess

async def start():
    # запускаем FastAPI
    subprocess.Popen(
        ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
    )

    await asyncio.sleep(2)

    # запускаем бота
    from main import main
    await main()

asyncio.run(start())