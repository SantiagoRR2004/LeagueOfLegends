from .githubIssues import reportMissingProfile
from selenium.webdriver.common.by import By
from datetime import datetime, timezone
from bs4 import BeautifulSoup
from zoneinfo import ZoneInfo
from modules import Internet
import pandas as pd
import atexit
import time

from selenium import webdriver
import chromedriver_autoinstaller
from pyvirtualdisplay import Display

driver = None


def getDriver() -> Internet.WebDriver:
    """
    Get the Selenium WebDriver instance, creating it if it doesn't exist.

    Args:
        - None

    Returns:
        - Internet.WebDriver: The Selenium WebDriver instance.
    """
    global driver

    if driver is None:
        display = Display(visible=0, size=(800, 800))
        display.start()

        chromedriver_autoinstaller.install()  # Check if the current version of chromedriver exists
        # and if it doesn't exist, download it automatically,
        # then add chromedriver to path

        chrome_options = webdriver.ChromeOptions()
        # Add your options as needed
        options = [
            # Define window size here
            "--window-size=1200,1200",
            "--ignore-certificate-errors"
            # "--headless",
            # "--window-size=1920,1200",
            # "--ignore-certificate-errors",
            # "--disable-extensions",
            # These flags BELOW are recommended for stability when running Chrome in headless or containerized environments (such as GitHub Actions).
            "--disable-gpu",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--remote-debugging-port=9222",
        ]
        for option in options:
            chrome_options.add_argument(option)

        driver = webdriver.Chrome(options=chrome_options)
        atexit.register(driver.quit)

    return driver


def getBattlesFromHTML(soup: BeautifulSoup) -> pd.DataFrame:
    """
    Extracts the battles from the given HTML soup and returns a
    DataFrame with the start time and duration of each battle.

    It is only meant to work with the HTML of OP.GG

    Args:
        - soup (BeautifulSoup): The object containing the HTML of the OP.GG page.

    Returns:
        - pd.DataFrame: A DataFrame with the start time and duration of each battle.
    """
    rows = []

    # Each battle is a div with class="flex min-w-0 flex-1 flex-col bg-[var(--game-item-color-100)]"
    battleDivs = soup.find_all(
        "div", class_="flex min-w-0 flex-1 flex-col bg-[var(--game-item-color-100)]"
    )

    browserTimeZone = driver.execute_script(
        "return Intl.DateTimeFormat().resolvedOptions().timeZone"
    )

    for battleDiv in battleDivs:

        # The duration is in the div with class="flex gap-2 md:flex-col md:gap-0"
        durationDiv = battleDiv.find("div", class_="flex gap-2 md:flex-col md:gap-0")
        if durationDiv is None:
            raise ValueError("Could not find duration div in battle div")

        span = durationDiv.find("span")
        if span is None:
            raise ValueError("Could not find span in duration div")

        durationText = span.get_text(strip=True)
        durationSeconds = 0

        for part in durationText.split():
            if part.endswith("m"):
                durationSeconds += int(part[:-1]) * 60
            elif part.endswith("s"):
                durationSeconds += int(part[:-1])
            else:
                raise ValueError(f"Unknown duration part: {part}")

        # Find the span with data-tooltip-id="opgg-tooltip"
        tooltipSpan = battleDiv.find("span", {"data-tooltip-id": "opgg-tooltip"})
        if tooltipSpan is None:
            raise ValueError("Could not find tooltip span in battle div")

        startTimeText = tooltipSpan["data-tooltip-content"]
        dt = datetime.strptime(startTimeText, "%m/%d/%Y, %I:%M %p")
        dt = (
            dt.replace(tzinfo=ZoneInfo(browserTimeZone))
            .astimezone(timezone.utc)
            .replace(tzinfo=None)
        )

        rows.append({"start": dt, "time": durationSeconds})

    df = pd.DataFrame(rows, columns=["start", "time"])

    # Make start a datetime column and time an integer column
    df["start"] = pd.to_datetime(df["start"])
    df["time"] = df["time"].astype(int)

    # Sort the DataFrame by start time
    df = df.sort_values(by="start").reset_index(drop=True)

    return df


def getHTML(username: str, githubUsername: str) -> BeautifulSoup:
    """
    Retrieves the HTML of the OP.GG page for the given username and returns it as a BeautifulSoup object.

    It tries to load the max number of battles possible.

    Args:
        - username (str): The username of the player whose OP.GG page we want to scrape.
        - githubUsername (str): The GitHub username of the player, used for reporting missing profiles.

    Returns:
        - BeautifulSoup: The BeautifulSoup object containing the HTML of the OP.GG page.
    """
    driver = getDriver()
    name, tag = username.split("#")

    # TODO: Make this work for other regions
    url = f"https://www.op.gg/summoners/euw/{name}-{tag}"
    driver.get(url)

    # Wait 5 seconds
    time.sleep(5)

    elements = driver.find_elements(
        By.XPATH, "//*[contains(text(), 'No search results for')]"
    )

    if any(e.is_displayed() for e in elements):
        print(f"\nCheck username: {username} because it might not exist.")
        reportMissingProfile(username, githubUsername)

    # Click the "Show More" button until it is no longer present
    while True:
        try:
            Internet.clickButton(driver, "Show more")
        except Exception:
            break

    # Wait 5 seconds
    time.sleep(5)

    return BeautifulSoup(driver.page_source, "html.parser")
