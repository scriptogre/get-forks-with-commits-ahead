# GitHub Forks Commit Comparison

This script fetches forks of a GitHub repository and checks which forks have commits ahead of the base repository. The results are saved in a JSON file for further analysis.

## Requirements

- Python 3.7 or higher
- `requests` library

To install the `requests` library, run:

```bash
pip install requests
```

## Usage

1. Update the `.env` file with your GITHUB_TOKEN (your GitHub personal access token), GITHUB_OWNER & GITHUB_REPO (username of target repository's owner and repository's name) and PROGRESS_FILENAME (the name of the file to keep track of progress).
2. Run the script:
```bash
python forks_commit_comparison.py
```
3. The script will analyze the forks and save the results in a JSON file named `progress.json`. This file contains forks with commits ahead of the base repository and the number of commits ahead for each fork.

## Note
Please be aware of the GitHub API rate limits. Unauthenticated requests are limited to 60 requests per hour, and authenticated requests are limited to 5000 requests per hour. This script uses authenticated requests. If you reach your rate limit, the script will error out. You will then need to resume after the rate limit reset time.

## License
This project is licensed under the MIT License.
