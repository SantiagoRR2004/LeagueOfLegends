from matplotlib.ticker import FuncFormatter
from matplotlib import dates as mdates
from matplotlib import pyplot as plt
from datetime import timedelta
import pandas as pd
import src
import os


def buildWeeklyTimeData(gamesDf: pd.DataFrame, weeksDf: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate game time into the week in which each game finishes.

    Args:
        - gamesDf (pd.DataFrame): Game rows with start and time columns.
        - weeksDf (pd.DataFrame): Week boundaries with start and end columns.

    Returns:
        - pd.DataFrame: One row per week with the summed time in seconds.
    """
    weeklyDf = weeksDf[["start", "end"]].copy()
    weeklyDf["time"] = 0

    if gamesDf.empty:
        return pd.DataFrame(columns=["start", "end", "time"])

    gamesDf["start"] = pd.to_datetime(gamesDf["start"])
    gamesDf["finish"] = gamesDf["start"] + pd.to_timedelta(gamesDf["time"], unit="s")

    # Cut games into weeks based on their finish time
    weekBoundaries = list(weeksDf["start"]) + [weeksDf.iloc[-1]["end"]]
    weekIndex = pd.cut(
        gamesDf["finish"],
        bins=weekBoundaries,
        right=False,
        labels=False,
    )

    timeByWeek = gamesDf.groupby(weekIndex, dropna=True)["time"].sum()

    # Start from the first week that has games
    firstWeekIndex = int(timeByWeek.index.min())
    weeklyDf = weeklyDf.iloc[firstWeekIndex:].copy()

    weeklyDf["time"] = weeklyDf.index.to_series().map(timeByWeek).fillna(0).astype(int)

    return weeklyDf


def createUserString(githubID: int, githubUsername: str) -> str:
    """
    Create a Markdown string for a user with their GitHub profile picture and username.

    Args:
        - githubID (int): The GitHub user ID.
        - githubUsername (str): The GitHub username.

    Returns:
        - str: A Markdown string with the user's profile picture and username.
    """
    profilePicture = f'<span><a href="https://github.com/{githubUsername}"><img src="https://avatars.githubusercontent.com/u/{githubID}" style="width:1ch;" alt=""></span>'

    # White space that can't be touched by the neighboring urls
    whiteSpace = "<a>&ensp;</a>"

    return f"{profilePicture}{whiteSpace}[{profilesGitHub[githubID]}](https://github.com/{profilesGitHub[githubID]}){whiteSpace}{profilePicture}"


if __name__ == "__main__":
    # Load the different premade Markdown parts
    premade = src.loadMarkdownParts()
    mainMarkdown = [premade["beginning"]]

    # Create graphs folder
    currentDirectory = os.path.dirname(os.path.abspath(__file__))
    graphsPath = os.path.join(currentDirectory, "graphs")
    os.makedirs(graphsPath, exist_ok=True)

    profilesLoL = src.getLoLProfiles()
    profilesGitHub = {int(k): v for k, v in src.getGitHubProfiles().items()}
    dataframesGitHubTotal = {}
    dataframesGitHubWeekly = {}
    weeksDF = src.getWorkWeeks()

    # Create dataframe for GitHub profiles
    for githubID in profilesGitHub.keys():
        dfsLoL = []

        for usernameLoL, githubIDLoL in profilesLoL.items():
            if githubIDLoL == githubID:
                dfsLoL.append(src.getLoLTimeData(usernameLoL))

        mergedDf = pd.concat(dfsLoL, ignore_index=True) if dfsLoL else pd.DataFrame()

        # Create the column "end"
        mergedDf["end"] = mergedDf["start"] + pd.to_timedelta(
            mergedDf["time"], unit="s"
        )

        # Sort the merged dataframe by start time
        mergedDf.sort_values(by="start", inplace=True)

        dataframesGitHubTotal[githubID] = mergedDf.copy()
        dataframesGitHubWeekly[githubID] = buildWeeklyTimeData(mergedDf, weeksDF)

    # The total time playing LoL
    mainMarkdown.append(premade["totalTime"])
    totalTime = {
        githubID: int(df["time"].sum())
        for githubID, df in dataframesGitHubWeekly.items()
    }
    totalTime = dict(sorted(totalTime.items(), key=lambda item: item[1], reverse=True))
    profileOrder = list(totalTime)
    totalTimeTable = {"User": [], "Time": []}

    for githubID, time in totalTime.items():
        totalTimeTable["User"].append(
            createUserString(githubID, profilesGitHub[githubID])
        )
        totalTimeTable["Time"].append(str(timedelta(seconds=time)))

    # Add the total time row to the Markdown
    totalTimeTable["User"].append("Total")
    totalTimeTable["Time"].append(str(timedelta(seconds=sum(totalTime.values()))))

    mainMarkdown.append(src.markdownTable(totalTimeTable))

    # Calculate the total hours spent in a given week
    mainMarkdown.append(premade["weekly"])
    timeByWeekRows = []

    for week in weeksDF.itertuples():
        totalTime = int(
            sum(
                df.loc[
                    (df["start"] >= week.start) & (df["start"] < week.end), "time"
                ].sum()
                for df in dataframesGitHubWeekly.values()
            )
        )
        timeByWeekRows.append(
            (
                week.start,
                week.end,
                totalTime,
            )
        )

    # Sort by total time in descending order
    timeByWeekRows.sort(key=lambda row: row[2], reverse=True)
    timeByWeekTable = {
        "Start": [row[0].strftime("%-d %B %Y") for row in timeByWeekRows],
        "End": [row[1].strftime("%-d %B %Y") for row in timeByWeekRows],
        "Time": [str(timedelta(seconds=row[2])) for row in timeByWeekRows],
    }

    mainMarkdown.append(src.markdownTable(timeByWeekTable))

    # Create a graph of the total time by week
    timeByWeekRows = sorted(timeByWeekRows, key=lambda row: row[0])
    plt.figure(figsize=(10, 6))
    plt.plot(
        [row[0] for row in timeByWeekRows],
        [row[2] for row in timeByWeekRows],
        marker="o",
        linestyle="-",
    )
    plt.title("Total Time Spent Playing LoL by Week")
    plt.xlabel("Week")
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%-d %b"))
    plt.ylabel("Time")
    plt.gca().yaxis.set_major_formatter(
        FuncFormatter(lambda value, _: str(timedelta(seconds=int(value))))
    )
    plt.savefig(os.path.join(graphsPath, "totalWeekly.png"), bbox_inches="tight")
    plt.close()
    mainMarkdown.append(premade["weeklyGraph"])

    # Create a table with the time since the latest match
    totalCleanTimeTable = {"User": [], "Maximum": [], "Current": []}

    for githubID in profilesGitHub.keys():
        totalCleanTimeTable["User"].append(
            createUserString(githubID, profilesGitHub[githubID])
        )

        if dataframesGitHubTotal[githubID].empty:
            totalCleanTimeTable["Current"].append(0)
            totalCleanTimeTable["Maximum"].append("0:00:00")

        else:
            lastMatchTime = dataframesGitHubTotal[githubID]["end"].max()
            timeSinceLastMatch = (pd.Timestamp.now() - lastMatchTime).total_seconds()
            totalCleanTimeTable["Current"].append(int(timeSinceLastMatch))

            gaps = (
                dataframesGitHubTotal[githubID]["start"]
                - dataframesGitHubTotal[githubID]["end"].shift()
            ).dt.total_seconds()

            totalCleanTimeTable["Maximum"].append(
                str(timedelta(seconds=int(gaps.max())))
            )

    # Sort by time since last match in descending order
    totalCleanTimeTable = {
        key: [
            val
            for _, val in sorted(
                zip(totalCleanTimeTable["Current"], values), reverse=True
            )
        ]
        for key, values in totalCleanTimeTable.items()
    }

    # Turn time into a string for the Markdown table
    totalCleanTimeTable["Current"] = [
        str(timedelta(seconds=value)) for value in totalCleanTimeTable["Current"]
    ]

    mainMarkdown.append(premade["cleanTime"])
    mainMarkdown.append(src.markdownTable(totalCleanTimeTable))

    # Create a graph of the time by week for each profile
    plt.figure(figsize=(10, 6))
    for githubID in profileOrder:
        df = dataframesGitHubWeekly[githubID]
        plt.plot(
            df["start"],
            df["time"],
            linestyle="-",
            label=profilesGitHub[githubID],
        )
    plt.legend()
    plt.title("Time Spent Playing LoL by Week and Profile")
    plt.xlabel("Week")
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%-d %b"))
    plt.ylabel("Time")
    plt.gca().yaxis.set_major_formatter(
        FuncFormatter(lambda value, _: str(timedelta(seconds=int(value))))
    )
    plt.savefig(os.path.join(graphsPath, "weekly.png"), bbox_inches="tight")
    plt.close()
    mainMarkdown.append(premade["weekUser"])

    # Create the individual graphs by week for each profile
    individualMarkdown = ""
    for githubID in profileOrder:
        df = dataframesGitHubWeekly[githubID]
        individualMarkdown += (
            f"## {createUserString(githubID, profilesGitHub[githubID])}\n\n"
        )

        plt.figure(figsize=(10, 6))
        plt.plot(
            df["start"],
            df["time"],
            linestyle="-",
            label=profilesGitHub[githubID],
        )
        plt.title(f"Time Spent Playing LoL by Week for {profilesGitHub[githubID]}")
        plt.xlabel("Week")
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%-d %b"))
        plt.ylabel("Time")
        plt.gca().yaxis.set_major_formatter(
            FuncFormatter(lambda value, _: str(timedelta(seconds=int(value))))
        )
        plt.savefig(
            os.path.join(graphsPath, f"{profilesGitHub[githubID]}.png"),
            bbox_inches="tight",
        )
        plt.close()

        individualMarkdown += (
            f"![{profilesGitHub[githubID]}](./{profilesGitHub[githubID]}.png)\n\n"
        )

    mainMarkdown.append(individualMarkdown)

    # Save the Markdown to a file
    with open(os.path.join(graphsPath, "README.md"), "w") as f:
        f.write("\n".join(mainMarkdown))
