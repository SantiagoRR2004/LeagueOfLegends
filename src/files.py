import pandas as pd
import json
import os


def getWorkWeeks() -> pd.DataFrame:
    """
    Reads the work weeks from the CSV file and
    checks that it has the expected format.

    Args:
        - None

    Returns:
        - pd.DataFrame: The work weeks data.
    """
    currentDirectory = os.path.dirname(os.path.abspath(__file__))
    filePath = os.path.join(os.path.dirname(currentDirectory), "weeks.csv")

    df = pd.read_csv(filePath)

    # Check that it has the expected columns
    expectedColumns = {"start", "end"}
    if not expectedColumns.issubset(df.columns):
        raise ValueError(f"Expected columns {expectedColumns} not found in {filePath}")

    # start < end for each row
    for i in range(len(df)):
        if df.loc[i, "start"] >= df.loc[i, "end"]:
            raise ValueError(
                f"Start time of row {i} is not less than end time in {filePath}"
            )

    # end == start from next row
    for i in range(len(df) - 1):
        if df.loc[i, "end"] != df.loc[i + 1, "start"]:
            raise ValueError(
                f"End time of row {i} does not match start time of row {i + 1} in {filePath}"
            )

    # start and end are Unix timestamps
    df["start"] = pd.to_datetime(df["start"], unit="s")
    df["end"] = pd.to_datetime(df["end"], unit="s")

    return df


def getLoLTimeData(lolUsername: str) -> pd.DataFrame:
    """
    Reads the LoL time data for the given username
    and checks that it has the expected format.

    Args:
        - lolUsername (str): The LoL username to read the data for.

    Returns:
        - pd.DataFrame: The LoL time data for the given username.
    """
    currentDirectory = os.path.dirname(os.path.abspath(__file__))
    dataPath = os.path.join(os.path.dirname(currentDirectory), "data")
    filePath = os.path.join(dataPath, f"{lolUsername}.csv")

    df = pd.read_csv(filePath, parse_dates=["start"])

    # Check that it has the expected columns
    expectedColumns = {"start", "time"}
    if not expectedColumns.issubset(df.columns):
        raise ValueError(f"Expected columns {expectedColumns} not found in {filePath}")

    return df


def getProfiles(platform: str) -> dict:
    """
    Reads the {platform} profiles from the JSON file.

    It also sorts them in lowercase and saves them back to the file.

    Args:
        - None

    Returns:
        - dict: The {platform} profiles.
    """
    currentDirectory = os.path.dirname(os.path.abspath(__file__))
    profilesPath = os.path.join(
        os.path.dirname(currentDirectory), f"profiles{platform}.json"
    )

    with open(profilesPath, "r") as f:
        profiles = json.load(f)

    def naturalKey(s):
        return int(s) if s.isdigit() else s.lower()

    # Sort them in lowercase
    profiles = dict(sorted(profiles.items(), key=lambda item: naturalKey(item[0])))

    # Save correctly
    with open(profilesPath, "w", encoding="utf-8") as f:
        json.dump(profiles, f, indent=2, ensure_ascii=False)
        f.write("\n")

    return profiles


def getLoLProfiles() -> dict:
    return getProfiles("LoL")


def getGitHubProfiles() -> dict:
    return getProfiles("GitHub")
