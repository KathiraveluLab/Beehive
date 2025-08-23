from locust import HttpUser, task, between
import random
import os

class AdminUser(HttpUser):
    wait_time = between(1, 3)  


    def on_start(self):
        self.token = os.getenv("CLERK_SECRET_KEY")  
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    @task
    def get_dashboard(self):
        self.client.get("/api/admin/dashboard", headers=self.headers)

    @task
    def get_user_uploads(self):
        # You should replace this with actual test user IDs or mock IDs
        test_user_ids = ["user_2y0cvoJHLXtDQsjgPOkngx5bcsj", "user_xyz789"]
        user_id = random.choice(test_user_ids)
        self.client.get(f"/api/admin/user_uploads/{user_id}", headers=self.headers)

    @task
    def get_notifications_endpoint(self):
        # Test with and without mark_seen
        mark_seen = random.choice(["true", "false"])
        with self.client.get(
            "/api/admin/notifications",
            params={"mark_seen": mark_seen},
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Notifications failed with status {response.status_code}")

    


