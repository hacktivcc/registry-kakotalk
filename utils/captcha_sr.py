import google.generativeai as genai
from PIL import Image


class CaptchaSolver:

    def __init__(self):
        self.api_key = "AIzaSyD6u75MX9eTckmbCCVAQHZQVmdmevJLhUg"
        genai.configure(api_key=self.api_key)
        
    async def solve_captcha(self):
        try:
            image = Image.open("images\\registry_captcha_after_trim.png")
            vision_model = genai.GenerativeModel(
                "gemini-1.5-flash",
                system_instruction="You will only look at images that contain captchas. Your job is to carefully read the question or prompt in the captcha, then provide the correct answer. Do not include any extra explanations or information—just give the exact answer to the captcha.",
            )
            response = vision_model.generate_content(
                ["Solve This Captcha Notes! : Send The Answer Only Without Anything", image]
            )

            self.answer = response.text.strip()
            return self.answer
        except:
            self.answer = "Failed to solve captcha"
            return self.answer
