import os
import subprocess


def reportMissingProfile(lolUsername: str, githubUsername: str) -> None:
    """
    Create and assign a GitHub issue when a League profile cannot be found.

    Args:
        - lolUsername (str): The League of Legends username that could not be found.
        - githubUsername (str): The GitHub username of the player, used for assigning the issue.

    Returns:
        - None
    """
    token = os.getenv("GITHUB_TOKEN")
    repository = os.getenv("GITHUB_REPOSITORY")

    if not token or not repository:
        print("GITHUB_TOKEN and GITHUB_REPOSITORY are required to create an issue.")
        return

    issueTitle = f"Missing League profile: {lolUsername}"
    issueBody = (
        f"@{githubUsername}, the scraper could not find the League of Legends profile "
        f"`{lolUsername}` on OP.GG. Please verify the username and tag."
    )
    environment = {**os.environ, "GH_TOKEN": token}

    try:
        createdIssue = subprocess.run(
            [
                "gh",
                "issue",
                "create",
                "--repo",
                repository,
                "--title",
                issueTitle,
                "--body",
                issueBody,
                "--assignee",
                githubUsername,
            ],
            check=True,
            capture_output=True,
            text=True,
            env=environment,
        )
        print(f"Created issue for {lolUsername}: {createdIssue.stdout.strip()}")
    except (OSError, subprocess.CalledProcessError) as error:
        print(f"Could not create a GitHub issue for {lolUsername}: {error}")
