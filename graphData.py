from datetime import timedelta
import pandas as pd
import src
import os

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

    # Create dataframe for GitHub profiles
    for githubID, usernameGH in profilesGitHub.items():
        dfsLoL = []

        for usernameLoL, githubIDLoL in profilesLoL.items():
            if githubIDLoL == githubID:
                dfsLoL.append(src.getLoLTimeData(usernameLoL))

        if dfsLoL:
            # Merge all profile rows and keep a single time column per start/end interval.
            mergedDf = (
                pd.concat(dfsLoL, ignore_index=True)
                .groupby(["start", "end"], as_index=False)["time"]
                .sum()
                .sort_values("start")
                .reset_index(drop=True)
            )
        else:
            mergedDf = pd.DataFrame(columns=["start", "end", "time"])

        dataframesGitHub[githubID] = mergedDf

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

    mainMarkdown.append(src.markdownTable(totalTimeTable))

    # Save the Markdown to a file
    with open(os.path.join(graphsPath, "README.md"), "w") as f:
        f.write("\n".join(mainMarkdown))
