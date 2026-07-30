import tqdm
import src

if __name__ == "__main__":

    profilesLoL = src.getLoLProfiles()
    foundNewBattles = False

    for username in tqdm.tqdm(profilesLoL.keys(), desc="Processing profiles"):
        soup = src.getHTML(username)
        df = src.getBattlesFromHTML(soup)

        if not df.empty:
            foundNewBattles = True

        src.combineData(df, username)

    assert foundNewBattles, "No new battles were found for any profile."
