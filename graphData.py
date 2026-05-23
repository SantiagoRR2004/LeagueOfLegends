from datetime import timedelta
import src

if __name__ == "__main__":
    profiles = src.getLoLProfiles()
    times = {}

    for username, githubID in profiles.items():
        df = src.getLoLTimeData(username)

        # Add the entire time of all rows
        times[username] = df["time"].sum()

    # Sort them by time
    times = dict(sorted(times.items(), key=lambda item: item[1], reverse=True))

    for username, time in times.items():
        print(f"{username}: {timedelta(seconds=int(time))}")
