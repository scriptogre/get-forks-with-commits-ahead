import json
import requests
from operator import itemgetter
import os
from dotenv import load_dotenv

load_dotenv()

owner = os.environ["GITHUB_OWNER"]
repo = os.environ["GITHUB_REPO"]
token = os.environ["GITHUB_TOKEN"]
progress_filename = os.environ["PROGRESS_FILENAME"]


def get_forks_with_commits_ahead(owner, repo, progress_filename="progress.json"):
    def save_progress(filename, progress):
        with open(filename, 'w') as f:
            json.dump(progress, f, indent=2)

    base_url = f"https://api.github.com/repos/{owner}/{repo}"
    headers = {'Authorization': f'token {token}'}

    # Get the base repository's commit SHA for the default branch using token auth
    base_repo = requests.get(base_url, headers=headers).json()
    default_branch = base_repo["default_branch"]
    base_commit_url = f"{base_url}/git/refs/heads/{default_branch}"
    base_commit = requests.get(base_commit_url, headers=headers).json()
    base_commit_sha = base_commit["object"]["sha"]

    # Get the total number of forks
    total_forks = base_repo["forks_count"]
    print(f"Found {total_forks} forks.")

    # Load existing progress
    progress = load_progress(progress_filename)

    # Get the next unprocessed page
    start_page = max(progress["searched_pages"]) + 1 if progress["searched_pages"] else 1
    page = start_page

    while True:
        print(f"\nProcessing page {page}...")
        forks = []

        forks_url = f"{base_url}/forks?page={page}&per_page=100&sort=oldest"
        current_page_forks = requests.get(forks_url, headers=headers).json()
        if not current_page_forks:
            break
        forks.extend(current_page_forks)

        # Get the commit count ahead for each fork
        for i, fork in enumerate(forks, start=1):
            progress["total_forks_processed"] += 1

            # Fetches the commit SHA for the fork's default branch
            fork_commit_url = f"https://api.github.com/repos/{fork['full_name']}/git/refs/heads/{fork['default_branch']}"
            fork_commit = requests.get(fork_commit_url, headers=headers).json()
            fork_commit_sha = fork_commit["object"]["sha"]

            # Construct the comparison URL using base_commit_sha and fork_commit_sha
            comparison_url = f"{base_url}/compare/{base_commit_sha}...{fork_commit_sha}"
            comparison = requests.get(comparison_url, headers=headers).json()
            print("Comparison:", comparison)

            commits_ahead = comparison.get("ahead_by", 0)
            commits_behind = comparison.get("behind_by", 0)

            if commits_ahead > 0 and commits_behind == 0:
                print(f"{fork['full_name']} is ahead of {owner}/{repo} by {commits_ahead} commits but not behind ({progress['total_forks_processed']}/{total_forks})")
                fork_data = {"fork": fork["full_name"], "commits_ahead": commits_ahead}
                progress["forks_with_commits_ahead_but_not_behind"].append(fork_data)

            elif commits_ahead > 0 and commits_behind > 0:
                print(f"{fork['full_name']} is ahead of {owner}/{repo} by {commits_ahead} commits and behind by {commits_behind} commits ({progress['total_forks_processed']}/{total_forks})")
                fork_data = {"fork": fork["full_name"], "commits_ahead": commits_ahead}
                progress["forks_with_commits_ahead"].append(fork_data)

            elif commits_ahead == 0 and (commits_behind == 0 or commits_behind > 0):
                print(f"{fork['full_name']} is identical or behind {owner}/{repo} ({progress['total_forks_processed']}/{total_forks})")
                progress["forks_identical_or_behind"].append(fork["full_name"])

            else:
                progress["errors"] += 1
                print("Something went wrong.")

            # Save progress to file after each page
            save_progress(progress_filename, progress)

        # Add the page to searched pages after all forks on the page have been processed
        progress["searched_pages"].append(page)
        save_progress(progress_filename, progress)

        page += 1

    return progress["forks_with_commits_ahead"]


def load_progress(filename):
    try:
        with open(filename, 'r') as f:
            progress = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        progress = {
            "searched_pages": [],
            "forks_with_commits_ahead": [],
            "forks_with_commits_ahead_but_not_behind": [],
            "forks_identical_or_behind": [],
            "total_forks_processed": 0,
            "errors": 0,
            # We don't need to track forks that are behind but not ahead
        }
    return progress


forks_with_commits_ahead = get_forks_with_commits_ahead(owner, repo, progress_filename)

# Sort forks by commit count ahead
sorted_forks = sorted(forks_with_commits_ahead, key=itemgetter("commits_ahead"), reverse=True)

for fork in sorted_forks:
    print(f"{fork['fork']} is {fork['commits_ahead']} commits ahead.")
