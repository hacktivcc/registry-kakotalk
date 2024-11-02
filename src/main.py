from playwright.async_api import async_playwright
from asyncio import sleep
from tm import TempMailService
from utils import CaptchaSolver, trim_image
from httpx import AsyncClient
from random import randint
from faker import Faker
import logging
logging.basicConfig(level=logging.INFO)

class KakaoRegistration:

    def __init__(self):
        self.registry_api = "https://accounts.kakao.com/weblogin/create_account/"
        self.browser = None
        self.page = None
        self.email = None
        self.nickname = None
        self.client = AsyncClient(http2=True)
        self.temp_mail = TempMailService(self.client)
        self.password = f"{Faker().password(length=16, special_chars=True, digits=True, upper_case=True, lower_case=True)}" 

    async def launch_browser(self):
        async with async_playwright() as p:
            self.browser = await p.firefox.launch(headless=True) # if u want to see all steps of the process, set headless=False
            self.page = await self.browser.new_page()
            await self.register()

    async def register(self):
        try:
            self.email = await self.temp_mail.get_email()
            self.page.on("response", lambda response: self.handler_response(response , self.page.frame_locator("iframe")))
            print(f"Trying to register with: {self.email}")

            await self.page.goto(self.registry_api, wait_until="load")

            await self.page.click("button.btn_g.highlight.submit:has-text('I have an email account.')")
            await self.page.wait_for_selector(".ico_comm.ico_check", state="visible")
            await self.page.click(".ico_comm.ico_check")
            await self.page.click(".submit")
            await self.page.fill("input[name=email]", self.email)
            await self.page.click("button.btn_round")

            await self.handle_verification()
            self.nickname = Faker().name()
            await self.page.fill("input[name=profile_nickname]", f"{self.nickname}")
            await self.select_birthdate(f"{randint(1980, 2005)}", f"{randint(1, 12)}", f"{randint(1, 29)}")
            await self.select_gender("male")
            await self.page.click(".submit")
            with open("accounts_registred\\accounts_registred.txt", "a") as file:
                file.write(f"Email: {self.email}\nNickname: {self.nickname}\nPassword: {self.password}\n")
                file.close()
            logging.info(f"Account registered successfully: {self.email}, {self.nickname}, {self.password}")

        except Exception as e:
            logging.error(f"Registration error: {e}")
        finally:
            await self.close_browser()

    async def handle_verification(self):
        code_verify = None
        while not code_verify:
            await sleep(10)
            logging.info("Waiting for verification code...")
            code_verify = await self.temp_mail.get_messages()

        logging.info(f"Verification code received: {code_verify}")
        await self.page.wait_for_selector("input[name=email_passcode]", state="visible")
        await self.page.fill("input[name=email_passcode]", code_verify)
        await self.page.click(".submit")

        await self.page.fill('input[name="new_password"]', self.password)
        await self.page.fill('input[name="password_confirm"]', self.password)
        await self.page.click(".submit")

    async def handle_captcha(self, cframe):
        try:
            await sleep(10)
            await self.page.screenshot(path="images\\registry_captcha.png")
            trim_image()
            captcha_solver = CaptchaSolver()
            await captcha_solver.solve_captcha()
            print(f"Captcha solved: {captcha_solver.answer}")
            await cframe.locator("#inpDkaptcha").fill(captcha_solver.answer)
            await cframe.locator("#btn_dkaptcha_submit").click()
            logging.info("Captcha solved and submitted.")
        except Exception as e:
            logging.error(f"Captcha error: {e}")
        except:
            return "We Done"


    async def handler_response(self, response, cframe):
        if self.page.is_closed():
            return
        try:
            response_text = await response.text()
        except UnicodeDecodeError:
            response_text = (await response.body()).decode("latin1")
        except:
            return "We Done"

        if "/dkaptcha/quiz/" in response.url or "/dkaptcha/quiz" in response.url:
            if 'Enter the name of <em class="emph_txt">the place</em>' in response_text:
                await self.handle_captcha(cframe)
            else:
                await cframe.locator("#btn_dkaptcha_reset").click()
        elif "Bad Request" in response_text:
            logging.warning("Bad Request encountered. Resetting captcha.")
            try:
                await cframe.locator("#btn_dkaptcha_reset").click()
            except Exception as e:
                logging.error(f"Failed to reset captcha: {e}")


    async def select_birthdate(self, year, month, day):
        try:
            year_button = await self.page.query_selector('.select_year .link_selected')
            await year_button.click()
            await self.page.click(f'.select_year .list_select li:has-text("{year}")')
            logging.info(f"Selected year: {year}")

            month_button = await self.page.query_selector('.select_tf:nth-child(2) .link_selected')
            await month_button.click()
            await self.page.click(f'.select_tf:nth-child(2) .list_select li:has-text("{month}")')
            logging.info(f"Selected month: {month}")

            day_button = await self.page.query_selector('.select_tf:nth-child(3) .link_selected')
            await day_button.click()
            await self.page.click(f'.select_tf:nth-child(3) .list_select li:has-text("{day}")')
            logging.info(f"Selected day: {day}")

        except Exception as e:
            logging.error(f"Error selecting birthdate: {e}")

    async def select_gender(self, gender):
        try:
            await self.page.click(f'label[for="radio-gender-{gender.lower()}"]')
            logging.info(f"Selected gender: {gender}")
        except Exception as e:
            logging.error(f"Failed to select gender: {e}")

    async def close_browser(self):
        if self.page:
            await self.page.close()
        if self.browser:
            await self.browser.close()
        if self.client:
            await self.client.aclose()
        