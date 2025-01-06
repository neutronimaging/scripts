import os
import requests
import argparse
import pandas as pd

def list_issues(repo, token, closed=False, since=None, until=None):
    """
    List all closed issues for a GitHub repository using the GitHub REST API.

    :param repo: The repository in the format 'owner/repo'.
    :param token: A GitHub Personal Access Token for authentication.
    :return: A list of all closed issues.
    """
    url = f"https://api.github.com/repos/{repo}/issues"
    if not token:
        print("Error: No GitHub token provided.")
        return []

    headers = {"Authorization": f"Bearer {token}"}
    params = {"per_page": 100, "page": 1}
    if closed:
        params["state"] = "closed"

    if since:
        params["since"] = since+"T00:00:00Z"
    if until:
        params["until"] = until+"T23:59:59Z"

    all_issues = []
    
    while True:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            print(f"Error fetching issues: {response.status_code} {response.text}")
            break

        issues = response.json()
        if not issues:  # No more issues to fetch
            break

        all_issues.extend(issues)
        params["page"] += 1  # Increment the page number for the next request

    return all_issues

def print_md(issues) :
    for issue in issues:
        print('- Issue',issue['number'], '- [',issue['title'],'](', issue['html_url'],')')

def print_txt(issues) :
    for issue in issues:
        print('Issue',issue['number'], '-',issue['title'])  

if __name__ == "__main__":
    # Replace with your repository and token
    repo = "neutronimaging/imagingsuite"

    parser = argparse.ArgumentParser(description="Fetches an issue list from GitHub.")
    parser.add_argument('-t','--token', help="Provide a GitHub token.", default = os.getenv("GHTOKEN", default=None))
    parser.add_argument('-r','--repos', help="The reopsitory to fetch issues from. Format: 'owner/repo'.", default=repo)
    parser.add_argument('-c','--closed', help="Fetch closed issues.", action="store_true", default=False) 
    parser.add_argument('-s','--since', help="Start date. Format: YYYY-MM-DD", default=None)
    parser.add_argument('-u','--until', help="End date. Format: YYYY-MM-DD", default=None)  
    parser.add_argument('-f','--format', help="Output format. Options: 'txt' or 'md'.", default='txt')

    args = parser.parse_args()
    # Fetch all closed issues
    issues = list_issues(repo, token=args.token, closed=args.closed, since=args.since, until=args.until)

    # Print the results
    if issues:
        if args.format == 'txt':
            print_txt(issues)
        elif args.format == 'md':
            print_md(issues)
    else:
        print("No closed issues found or an error occurred.")

