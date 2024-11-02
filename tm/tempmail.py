import re
import asyncio
from httpx import ReadTimeout

API_GET_EMAIL = "https://api.internal.temp-mail.io/api/v3/email/new"
API_GET_MESSAGE = "https://api.internal.temp-mail.io/api/v3/email/{email}/messages"

class TempMailService:
    def __init__(self, client):
        self.client = client
        self.email = None
        self.token = None
        self.code_for_auth = None
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) "
                "Gecko/20100101 Firefox/130.0"
            ),
            "Content-Type": "application/json; charset=UTF-8"
        }
        self.code_loop = False

    async def get_email(self) -> tuple[str | None, str | None]:
        try:
            response = await self.client.post(
                url=API_GET_EMAIL,
                headers=self.headers
            )
            response.raise_for_status()
        except ReadTimeout:
            return await self.retry_get_email()
        except:
            return None, None

        data = response.json()
        self.email = data.get('email')
        self.token = data.get('token')
        return self.email

    async def retry_get_email(self) -> tuple[str | None, str | None]:
        return await self.get_email()

    async def get_messages(self) -> str | None:
        if not self.email:
            return None

        url = API_GET_MESSAGE.format(email=self.email)

        while self.code_loop == False:
            try:
                response = await self.fetch_get(url)
                messages = response.json()

                if messages:
                    latest_message = messages[0]
                    code = self.extract_verification_code(latest_message.get("body_text", ""))

                    if code:
                        print(f"Verification Code: {code}")
                        self.code_loop = True
                        return code

            except:
                return None

            await asyncio.sleep(5)

    async def fetch_get(self, url: str):
        return await self.client.get(url, headers=self.headers)

    def extract_verification_code(self, body_text: str) -> str | None:
        match = re.search(r"Verification Code (\d+)", body_text)
        return match.group(1) if match else None

    async def run(self) -> tuple[str | None, str | None, str | None]:
        email, token = await self.get_email()
        return email
