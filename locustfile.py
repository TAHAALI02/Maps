from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def home(self):
        self.client.get("/")

    @task
    def dashboard(self):
        self.client.get("/dashboard/")