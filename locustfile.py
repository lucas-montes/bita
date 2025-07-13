import random

from locust import HttpUser, constant_pacing, env, events, tag, task
from locust_helpers import TestSetUp, add_args_to_parser



@events.init_command_line_parser.add_listener
def _(parser):
    add_args_to_parser(parser)


@events.init.add_listener
def _(environment: env.Environment, **_):
    # Currently we receive a LocalRunner because we aren't doing distributed tests
    TestSetUp(environment)


class User(HttpUser):
    wait_time = constant_pacing(1)
    host = "http://0.0.0.0:8080"

    def on_start(self):
        self.urls = URLS

    @tag("good_requests")
    @task
    def good_requests(self):
        self.client.get(url=random.choice(self.urls))

    @tag("bad_requests")
    @task
    def bad_requests(self):
        self.client.get(url=random.choice(self.urls))
