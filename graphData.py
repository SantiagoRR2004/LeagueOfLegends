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
    dataframesGitHub = {}
    weeksDF = src.getWorkWeeks()

    # Create dataframe for GitHub profiles
    for githubID, usernameGH in profilesGitHub.items():
        dfsLoL = []

        for usernameLoL, githubIDLoL in profilesLoL.items():
            if githubIDLoL == githubID:
                dfsLoL.append(src.getLoLTimeData(usernameLoL))

        mergedDf = pd.concat(dfsLoL, ignore_index=True) if dfsLoL else pd.DataFrame()
        dataframesGitHub[githubID] = buildWeeklyTimeData(mergedDf, weeksDF)

    # The total time playing LoL
    mainMarkdown.append(premade["totalTime"])
    totalTime = {
        githubID: int(df["time"].sum()) for githubID, df in dataframesGitHub.items()
    }
    totalTime = dict(sorted(totalTime.items(), key=lambda item: item[1], reverse=True))
    totalTimeTable = {"User": [], "Time": []}

    for githubID, time in totalTime.items():
        profilePicture = f'<span><a href="https://github.com/{profilesGitHub[githubID]}"><img src="https://avatars.githubusercontent.com/u/{githubID}" style="width:1ch;" alt=""></span>'

        # White space that can't be touched by the neighboring urls
        whiteSpace = "<a>&ensp;</a>"

        totalTimeTable["User"].append(
            f"{profilePicture}{whiteSpace}[{profilesGitHub[githubID]}](https://github.com/{profilesGitHub[githubID]}){whiteSpace}{profilePicture}"
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
                for df in dataframesGitHub.values()
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

    # Save the Markdown to a file
    with open(os.path.join(graphsPath, "README.md"), "w") as f:
        f.write("\n".join(mainMarkdown))
