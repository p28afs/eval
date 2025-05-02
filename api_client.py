import httpx
import asyncio

class APIClient:
    def __init__(self, base_url: str, calls_per_minute: int = 20):
        self.base_url = base_url
        # throttle concurrent calls to respect TPM limits
        self.semaphore = asyncio.Semaphore(calls_per_minute)
        self.client = httpx.AsyncClient(timeout=30)

    async def call(self, question: str, mode: str) -> dict:
        """
        Calls the API and returns full JSON payload with keys:
        - answer: str
        - interp_jira: list[str]
        - impl_jira: list[str]
        - impl_pr: list[str]
        """
        # Dummy implementation: replace with actual endpoint logic
        # url = f"{self.base_url}/answer"
        # async with self.semaphore:
        #     response = await self.client.post(
        #         url,
        #         json={"question": question, "mode": mode},
        #     )
        #     response.raise_for_status()
        #     data = response.json()
        #     data["interp_jira"] = data.get("interp_jira", []) or []
        #     data["impl_jira"]   = data.get("impl_jira", [])   or []
        #     data["impl_pr"]     = data.get("impl_pr", [])     or []
        #     return data

        # Simulate async response
        await asyncio.sleep(0)
        return {
            "answer": "<DUMMY>",
            "interp_jira": ["INT-000"],
            "impl_jira":   ["IMP-000"],
            "impl_pr":     ["PR-000"],
        }
