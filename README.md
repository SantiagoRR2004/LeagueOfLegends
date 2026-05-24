# League of Legends

This repository stores the time spent playing League of Legends by all members of Auria Technologies. [Here is the basic extracted data](./graphs/README.md).

## Profiles

We link a GitHub profile to a LoL profile. Each GitHub user can have multiple LoL profiles. The LoL profile is linked to the GitHub ID in [`profilesLoL.json`](./profilesLoL.json). The GitHub username for each ID is stored in [`profilesGitHub.json`](./profilesGitHub.json). The GitHub ID can be found with the GitHub API; for example, for the user `octocat`: <https://api.github.com/users/octocat>.

We use GitHub accounts rather than real names. A new account should be added in a commit whose author is the profile being added.

## [Time data](./data/)

We store time data for each LoL profile in the `data/` directory. Each file is a `.csv` with two columns: `start` and `time`. Each row corresponds to a single game played and they should be ordered from oldest to newest.

To obtain this data the web [op.gg](https://op.gg/) is used. In the future, we may want to scrape the data, but right now it isn't implemented. If you hover over the time ago of each game, you can get the exact beginning time of the game. This is what we use to fill the `start` column. The `time` column is the duration of the game in seconds.

In the future, we should find a way to obtain an API key from [Riot Games](https://developer.riotgames.com/) and use it to obtain the data. For this we would probably need to create an Auria Technologies League of Legends account.
