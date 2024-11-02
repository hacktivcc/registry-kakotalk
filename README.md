# Registry Kakotalk

## Project Structure

The project is organized into the following directories and files:

- `app.py`: The main application file.
- `requirements.txt`: Lists the Python dependencies required for the project.
- `images/`: Contains image files used in the project.
  - `registry_captcha.png`
  - `registry_captcha_after_trim.png`
- `src/`: Contains the source code for the main functionality.
  - `__init__.py`
  - `main.py`
- `tm/`: Contains modules related to temporary email functionality.
  - `__init__.py`
  - `tempmail.py`
- `utils/`: Contains utility modules for image processing and captcha solving.
  - `__init__.py`
  - `captcha_sr.py`
  - `trim_image.py`

## Dependencies

The project requires the following Python packages:

- `playwright`: For web automation and browser control.
- `httpx`: For making HTTP requests.
- `faker`: For generating fake data.

## Installation

1. Clone the repository to your local machine.
2. Navigate to the project directory.
3. Install the required dependencies using pip:

   ```bash
   pip install -r requirements.txt
   ```