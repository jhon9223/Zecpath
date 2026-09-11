import os

from locust import HttpUser, task, between


class ZecpathUser(HttpUser):

    wait_time = between(1, 2)

    def on_start(self):
        self.token = os.getenv("ACCESS_TOKEN")

    @task
    def job_list(self):
        self.client.get(
            "/api/jobs/",
            headers={
                "Authorization": f"Bearer {self.token}"
            },
            name="GET /api/jobs/",
        )
