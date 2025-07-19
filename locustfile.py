import random

from locust import HttpUser, constant_pacing, env, events, task
from locust_helpers import TestSetUp, add_args_to_parser

from datetime import date
from bita.application import SecurityValue

def all_security_values():
    while True:
        for e in SecurityValue:
            yield e.value

def all_weighting_methods(d: str):
    lb = round(random.uniform(0.01, 1.0), 3) if random.choice((True, False)) else None
    ub = round(random.uniform(0.01, 1.0), 3) if random.choice((True, False)) else None
    return {"d": d, "lb": lb, "ub": ub}

def all_filters(d: str):
    if random.choice((True, False)):
        n = random.randint(1, 10)
        return {"n": n, "d": d}
    p = round(random.uniform(0.01, 100.0), 2)
    return {"p": p, "d": d}

def all_calendar_rules(dates: list[str]):
    if random.choice((True, False)):
        return {"dates": random.sample(dates, k=random.randint(1, len(dates)))}
    return {"initial_date": random.choice(dates)}

def generate_all_payload_combinations(dates: list[str]):
    for d in all_security_values():
        yield {
            "calendar_rule":all_calendar_rules(dates),
            "backtest_filter": all_filters(d),
            "weighting_method": all_weighting_methods(d),
        }

@events.init_command_line_parser.add_listener
def _(parser):
    add_args_to_parser(parser)


@events.init.add_listener
def _(environment: env.Environment, **_):
    # Currently we receive a LocalRunner because we aren't doing distributed tests
    TestSetUp(environment)


class User(HttpUser):
    wait_time = constant_pacing(1)
    host = "http://localhost:8000"
    url = "/backtest"

    def on_start(self):
        dates = [str(date(year=year,month=random.randint(1, 12),day=random.randint(1, 28))) for year in range(2020, 2025)]
        self.payload = generate_all_payload_combinations(dates)

    @task
    def random_requests(self):
        self.client.post(url=self.url, json=next(self.payload))
