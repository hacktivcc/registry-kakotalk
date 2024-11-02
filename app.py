from src import KakaoRegistration
from asyncio import run as run_async_func
import ctypes
ctypes.windll.kernel32.SetConsoleTitleW("Kakotalk Registration - tg @hacktivc")
async def main():
    browser = KakaoRegistration()
    try:
        await browser.launch_browser()
    finally:
        await browser.close_browser()


run_async_func(main())
