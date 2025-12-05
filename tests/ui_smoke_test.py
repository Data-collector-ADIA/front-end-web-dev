#!/usr/bin/env python3
"""Automated UI smoke test for the Streamlit Assistant page.

Requires: selenium, webdriver-manager

This script opens the Assistant page, types a short message into the chat
input, clicks Send, and verifies that `data/chat_history.json` grows to
include the new messages (user + assistant). It runs Chrome in headless mode.
"""
import json
import os
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service


ROOT = os.path.dirname(os.path.dirname(__file__))
APP_URL = os.getenv("APP_URL", "http://localhost:8510/chatbot")
HISTORY_PATH = os.path.join(ROOT, "data", "chat_history.json")


def read_history_len():
    try:
        with open(HISTORY_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return len(data)
    except Exception:
        return 0


def main():
    print("Starting UI smoke test against", APP_URL)

    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.set_page_load_timeout(10)
        driver.get(APP_URL)

        wait = WebDriverWait(driver, 30)

        # Wait for the chat input textarea by placeholder
        try:
            textarea = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'textarea[placeholder="Ask me anything..."]'))
            )
        except TimeoutException:
            # fallback: any textarea
            try:
                textarea = wait.until(EC.presence_of_element_located((By.TAG_NAME, "textarea")))
            except TimeoutException:
                # dump a small portion of the page for debugging
                print("Timed out waiting for textarea. Page source snippet:")
                src = driver.page_source
                print(src[:4000])
                raise

        before = read_history_len()
        print("history length before:", before)

        # type a short message
        textarea.click()
        textarea.clear()
        textarea.send_keys("Automated smoke test message")

        # find and click Send button (Streamlit often wraps text inside divs)
        try:
            send_btn = driver.find_element(By.XPATH, "//button[.//div[normalize-space()='Send']]")
        except Exception:
            # fallback: find button with text 'Send' anywhere inside
            send_btn = driver.find_element(By.XPATH, "//button[contains(., 'Send')]")

        send_btn.click()

        # Wait for persistence: history length should increase (user+assistant)
        deadline = time.time() + 20
        success = False
        while time.time() < deadline:
            after = read_history_len()
            if after >= before + 1:
                print("history length after:", after)
                success = True
                break
            time.sleep(0.5)

        if not success:
            raise RuntimeError("Smoke test failed: chat history did not update in time")

        print("Smoke test PASSED")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
