from locust import HttpUser, TaskSet, task

import re, json

class UserBehavior(TaskSet):
    def __init__(self, parent):
       super(UserBehavior, self).__init__(parent)
       self.token = ""
       self.headers = {}
    
    def login(self):
        response = self.client.post("/api/auth", data={"username": "string", "password": "string"})
        return json.loads(response._content)['access_token']

    def on_start(self):
        self.token = self.login()
        self.headers = {'Authorization': 'Bearer ' + self.token}

    def on_stop(self):
        self.logout()

    def logout(self):
        pass

    @task(1)
    def top(self):
        self.client.get("/api/books",headers=self.headers)
    
    @task(2)
    def validate(self):
        self.client.get("/api/auth/validate",headers=self.headers)
  

class RedmineUser(HttpUser):
    tasks = {UserBehavior:1}
    min_wait = 500
    max_wait = 1000