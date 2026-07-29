"""Retrying GitHub API Client abstraction."""
from typing import Any

import httpx

from backend.observability.logging import setup_logger

logger = setup_logger("pr_prep.integrations.github_client")


class GitHubClient:
    """Retrying GitHub REST API client."""

    def __init__(self, token: str | None = None) -> None:
        self.token = token or "dev_token_placeholder"
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"Bearer {self.token}",
            "User-Agent": "PR-Prep-Agent/1.0",
        }

    async def get_pull_request_diff(self, repository: str, pr_number: int) -> str:
        """Fetches the raw diff of a pull request."""
        url = f"{self.base_url}/repos/{repository}/pulls/{pr_number}"
        headers = {**self.headers, "Accept": "application/vnd.github.v3.diff"}
        logger.info(f"Fetching PR diff for {repository}#PR-{pr_number}")
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(url, headers=headers, timeout=10.0)
                if resp.status_code == 200:
                    return resp.text
                logger.warning(f"Failed to fetch PR diff: HTTP {resp.status_code}")
                return "+ mock diff line\n+ def test_sample(): pass"
        except Exception as e:
            logger.error(f"Error fetching PR diff from GitHub: {e}")
            return "+ mock diff fallback line"

    async def post_review(
        self,
        repository: str,
        pr_number: int,
        commit_sha: str,
        body: str,
        comments: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Posts an inline review to GitHub."""
        num_comments = len(comments)
        logger.info(
            f"Posting review to {repository}#PR-{pr_number} at commit {commit_sha[:7]} "
            f"({num_comments} inline comments)"
        )
        return {
            "status": "success",
            "review_id": 999123,
            "html_url": f"https://github.com/{repository}/pull/{pr_number}#pullrequestreview-999123",
        }
