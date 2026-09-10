import os
import time
import requests
from playwright.sync_api import sync_playwright

CALENDAR_URL = "https://embjpcol.rsvsys.jp/reservations/calendar"
TELEGRAM_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = "5785936967"


def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    response = requests.post(
        url,
        data={
            "chat_id": CHAT_ID,
            "text": message
        },
        timeout=20
    )

    response.raise_for_status()


def check_november_11(page):

    page.goto(
        CALENDAR_URL,
        wait_until="domcontentloaded",
        timeout=60000
    )

    # Esperar a que el calendario realmente aparezca
    page.wait_for_selector(
        ".sc_cal_title",
        state="visible",
        timeout=60000
    )

    time.sleep(3)

    # Buscar la vista mensual
    month_button = page.locator(
        '.js_change[data-value="month"]'
    )

    month_button.wait_for(
        state="visible",
        timeout=60000
    )

    # Click REAL
    month_button.click()

    # Esperar a que la vista mensual cargue
    page.wait_for_selector(
        ".sc_cal_month_itemlist",
        state="visible",
        timeout=60000
    )

    time.sleep(2)

    # Ir avanzando hasta noviembre 2026
    for _ in range(3):

        month = page.locator(
            ".sc_cal_title"
        ).inner_text()

        print(
            f"Calendario actual: {month}",
            flush=True
        )

        if "2026年11月" in month:
            break

        next_button = page.locator(
            "a.js_change_date.next01"
        )

        next_button.wait_for(
            state="visible",
            timeout=30000
        )

        next_button.click()

        time.sleep(3)

    # Buscar el día 11
    days = page.locator(
        ".sc_cal_month_itemlist"
    )

    for i in range(days.count()):

        day = days.nth(i)

        date = day.locator(
            ".sc_cal_date"
        )

        if date.count() == 0:
            continue

        if date.inner_text().strip() == "11":

            available = (
                day.locator(
                    ".c_cal_time_cell"
                ).count() > 0
            )

            return available

    return False


with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=True
    )

    page = browser.new_page()

    last_state = False

    while True:

        try:

            available = check_november_11(page)

            print(
                f"11/11/2026 disponible: {available}",
                flush=True
            )

            if available and not last_state:

                send_telegram(
                    "🚨🚨 ¡CITA DE VISA JAPÓN DISPONIBLE! 🚨🚨\n\n"
                    "📅 11 de noviembre de 2026\n\n"
                    "La fecha acaba de habilitarse. "
                    "Entra al sistema de la Embajada y revisa los horarios."
                )

                print(
                    "🚨 TELEGRAM ENVIADO",
                    flush=True
                )

            last_state = available

        except Exception as e:

            print(
                f"Error durante la revisión: {e}",
                flush=True
            )

        time.sleep(30)
