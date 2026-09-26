import tqdm
import src

if __name__ == "__main__":

    profilesLoL = src.getLoLProfiles()
    profilesGitHub = src.getGitHubProfiles()
    foundNewBattles = False

    for username, githubID in tqdm.tqdm(
        profilesLoL.items(), desc="Processing profiles"
    ):
        soup = src.getHTML(username, profilesGitHub[str(githubID)])
        df = src.getBattlesFromHTML(soup)

        if not df.empty:
            foundNewBattles = True

        src.combineData(df, username)

    assert foundNewBattles, "No new battles were found for any profile."
