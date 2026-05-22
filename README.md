# League of Legends

This repository stores the time spent playing League of Legends by all members of Auria Technologies.

## Profiles

We link a GitHub profile to a LoL profile. Each GitHub user can have multiple LoL profiles. The LoL profile is linked to the GitHub ID in [`profilesLoL.json`](./profilesLoL.json). The GitHub username for each ID is stored in [`profilesGitHub.json`](./profilesGitHub.json). The GitHub ID can be found with the GitHub API; for example, for the user `octocat`: <https://api.github.com/users/octocat>.

We use GitHub accounts rather than real names. A new account should be added in a commit whose author is the profile being added.

## [Time data](./data/)

We store time data for each LoL profile in the `data/` directory. Each file is a `.csv` with three columns: `start`, `end`, and `time`. Each row corresponds to a single week between meetings. Meetings are held every Wednesday at 20:00 (Spanish time), so `start` and `end` are Unix timestamps for that Wednesday at 20:00; the `end` of one week is the `start` of the next.

The `time` column is the time spent playing LoL in seconds during that week. It should include games that end before the `end` time. Because it is almost impossible to scrape all profiles at exactly 20:00, some games may be stored in the wrong week.

When adding old data, be careful with daylight saving time.
