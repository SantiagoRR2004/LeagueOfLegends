from datetime import datetime
from bs4 import BeautifulSoup
import pandas as pd


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

        rows.append({"start": dt, "time": durationSeconds})

    df = pd.DataFrame(rows, columns=["start", "time"])

    # Make start a datetime column and time an integer column
    df["start"] = pd.to_datetime(df["start"])
    df["time"] = df["time"].astype(int)

    # Sort the DataFrame by start time
    df = df.sort_values(by="start").reset_index(drop=True)

    return df
