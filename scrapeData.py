import tqdm
import src

if __name__ == "__main__":

    profilesLoL = src.getLoLProfiles()

    for username in tqdm.tqdm(profilesLoL.keys(), desc="Processing profiles"):
        soup = src.getHTML(username)
        df = src.getBattlesFromHTML(soup)
        src.combineData(df, username)
