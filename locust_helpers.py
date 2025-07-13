from __future__ import annotations

import csv
import logging
import time
from collections import namedtuple
from datetime import datetime
from pathlib import Path

import docker
import gevent
import locust.stats
import yaml
from docker.models.containers import Container
from locust import env
from locust.argument_parser import LocustArgumentParser
from locust.runners import STATE_CLEANUP, STATE_STOPPED, STATE_STOPPING

logger = logging.getLogger(__name__)

locust.stats.MODERN_UI_PERCENTILES_TO_CHART = (0.75, 0.95, 0.99)

MACHINE_STATS_FIELDS = (
    "memory_stats_cache",
    "memory_usage",
    "memory_limit",
    "cpu_usage",
    "precpu_usage",
    "system_cpu_usage",
    "system_precpu_usage",
    "online_cpus",
    "number_cpus",
    "time",
    "user_count",
)
MachineStat = namedtuple(
    "MachineStat",
    MACHINE_STATS_FIELDS,
    defaults=(None,) * len(MACHINE_STATS_FIELDS),
)

STATE_NOT_RUNNING = {
    STATE_STOPPING,
    STATE_STOPPED,
    STATE_CLEANUP,
}


def get_dockerfile_information() -> dict:
    with open("docker-compose.yml", "r") as file:
        services = yaml.safe_load(file)["services"]
        service_name = next(filter(lambda x: x.startswith("test"), services))
        return services[service_name]


class ServerProvider:
    __slots__ = (
        "locenv",
        "name",
        "results_dir",
        "docker_client",
        "container",
        "_background",
        "_docker_stats_csv_filehandle",
        "_docker_stats_csv_writer",
    )

    def __init__(
        self,
        locenv: env.Environment,
        results_dir: Path,
        name: str,
        memory: str,
    ) -> None:
        self.docker_client = docker.from_env()
        self.locenv = locenv
        self.name = name
        self.results_dir = results_dir
        image = self._clean_image(
            locenv.parsed_options.image,
            locenv.parsed_options.docker_tag,
        )
        self._start_docker(
            memory,
            int(locenv.parsed_options.cpu),
            name,
            image,
        )
        self._set_up_writers()
        self._background = gevent.spawn(self._update_stats)
        locenv.events.quit.add_listener(self._quit)

    def _set_up_writers(self) -> None:
        self._docker_stats_csv_filehandle = open(
            f"{self.results_dir}/{self.name}_docker_stats.csv",
            "a",
        )
        self._docker_stats_csv_writer = csv.writer(self._docker_stats_csv_filehandle)
        self._docker_stats_csv_writer.writerow(MACHINE_STATS_FIELDS)

    def _clean_image(self, image: str, tag: str) -> str:
        return image.replace(r"${TAG}", tag) if image.endswith(r"${TAG}") else image

    def _start_docker(self, memory: str, cpu: int, name: str, image: str) -> None:
        try:
            nano_cpus, cpuset_cpus = self._get_cpu_values(cpu)
            self.container: Container = self.docker_client.containers.run(
                image,
                detach=True,
                environment={
                    "PORT": self.locenv.parsed_options.service_port,
                    "WORKERS": self.locenv.parsed_options.gunicorn_workers,
                    "THREADS": self.locenv.parsed_options.gunicorn_threads,
                },
                nano_cpus=nano_cpus,
                cpuset_cpus=cpuset_cpus,
                mem_limit=memory,
                mem_reservation=memory,
                mem_swappiness=0,
                memswap_limit=memory,
                name=name,
                ports={
                    f"{self.locenv.parsed_options.service_port}/tcp": (
                        "0.0.0.0",
                        self.locenv.parsed_options.service_port,
                    )
                },
            )
            logger.debug("Starting container %s from image %s", name, image)

            self.container.reload()
        except docker.errors.ImageNotFound as e:
            logger.warning("Image not found, well create it. %s", str(e))
            return self._start_docker(memory, cpu, name, image)
        except (docker.errors.ContainerError, docker.errors.APIError) as e:
            logger.error("Error running the docker container %s", str(e))
            exit(1)

    def _get_cpu_values(self, cpu: int) -> tuple[int, str]:
        cpuset_cpus = ",".join(map(str, range(cpu)))
        nano_cpus = cpu * 100000000
        return nano_cpus, cpuset_cpus

    def _quit(self, **_) -> None:
        self._background.join(timeout=10)
        self._docker_stats_csv_filehandle.flush()
        self._docker_stats_csv_filehandle.close()
        try:
            self.container.stop()
            force_remove = False
        except docker.errors.APIError:
            force_remove = True
            self.container.reload()

        try:
            self.container.remove(force=force_remove)
        except docker.errors.APIError as e:
            logger.error("Error removing the docker container %s", str(e))

        logger.info(
            "Docker container %s stopped and removed",
            str(self.container.name),
        )
        self.locenv.runner.quit()

    def _get_machine_stats(self, docker_stats: dict) -> MachineStat:
        try:
            return MachineStat(
                memory_usage=docker_stats["memory_stats"].get("usage"),
                memory_stats_cache=docker_stats["memory_stats"].get("stats", {}).get("cache"),
                memory_limit=docker_stats["memory_stats"].get("limit"),
                cpu_usage=docker_stats["cpu_stats"]["cpu_usage"].get("total_usage"),
                precpu_usage=docker_stats["precpu_stats"]["cpu_usage"].get("total_usage"),
                system_cpu_usage=docker_stats["cpu_stats"].get("system_cpu_usage"),
                system_precpu_usage=docker_stats["precpu_stats"].get("system_cpu_usage"),
                online_cpus=docker_stats["cpu_stats"]["online_cpus"],
                number_cpus=len(docker_stats["cpu_stats"]["cpu_usage"].get("percpu_usage", [])),
                time=time.time(),
                user_count=self.locenv.runner.user_count,
            )
        except Exception as e:
            logger.warning(
                "Error getting the docker container stats %s",
                str(e),
            )
            return MachineStat()

    def _update_stats(self) -> None:
        last_flush_time: float = 0.0
        stats_source = self.container.stats(decode=True, stream=True)
        while self.locenv.runner.state not in STATE_NOT_RUNNING and self.container.status == "running":
            stats = self._get_machine_stats(next(stats_source))
            self._docker_stats_csv_writer.writerow(stats)
            now = time.time()
            if now - last_flush_time > 15:
                self._docker_stats_csv_filehandle.flush()
                last_flush_time = now


def add_args_to_parser(parser: LocustArgumentParser) -> None:
    docker_info = get_dockerfile_information()
    parser.add_argument(
        "--name",
        type=str,
        default=docker_info["container_name"],
        help="A name for the reports and the container if you are using custom settings. A report's name would look "
        "like: <name>-<cpu>cpu-<memory><memory-unit>memory-<date>",
    )
    parser.add_argument(
        "--gunicorn-threads",
        type=int,
        default=docker_info["environment"]["THREADS"],
        help="The number of threads that gunicorn can use. This will override the value of the .env file.",
    )
    parser.add_argument(
        "--gunicorn-workers",
        type=int,
        default=docker_info["environment"]["WORKERS"],
        help="The number of workers that gunicorn can use. This will override the value of the .env file.",
    )
    parser.add_argument(
        "--service-port",
        type=str,
        default=docker_info["environment"]["PORT"],
        help="The port for the service to use",
    )
    parser.add_argument(
        "--cpu",
        type=int,
        default=docker_info["deploy"]["resources"]["limits"]["cpus"],
        help="The number of cpus availables to the container. 1 CPU probably has 1 core and 2 threads.",
    )
    parser.add_argument(
        "--memory",
        type=int,
        default=docker_info["deploy"]["resources"]["limits"]["memory"][0],
        help="The amount of memory available to the container.",
    )
    parser.add_argument(
        "--memory-unit",
        type=str,
        choices=("gb", "mb", "kb"),
        default=docker_info["deploy"]["resources"]["limits"]["memory"][1:],
        help="The unit for the amount of memory",
    )
    parser.add_argument(
        "--image",
        type=str,
        default=docker_info["image"],
        help="The image for your docker container",
    )
    parser.add_argument(
        "--docker-tag",
        type=str,
        default=docker_info["environment"]["TAG"],
        help="The tag for the docker image",
    )


class TestSetUp:
    __slots__ = "locenv", "server_provider", "set_up_completed"

    def __init__(self, environment: env.Environment) -> None:
        self.locenv = environment
        self.set_up_completed = False
        use_local = "0.0.0.0:" in environment.host if environment.host is not None else True
        if environment.web_ui and use_local:
            environment.events.test_start.add_listener(self.test_start_listener)
        elif not environment.web_ui and use_local:
            self.set_up()

    def test_start_listener(self, environment: env.Environment) -> None:
        # happens only once in headless runs, but can happen multiple times in web ui-runs
        if not self.set_up_completed:
            self.set_up()

    def set_up(self) -> None:
        memory = f"{self.locenv.parsed_options.memory}{self.locenv.parsed_options.memory_unit}"
        name = self.get_name(self.locenv, memory)
        results_dir = self.get_results_dir(name)
        ServerProvider(self.locenv, results_dir, name, memory)
        self.set_up_completed = True

    def get_results_dir(self, name: str) -> Path:
        results_dir = Path.cwd() / f"load-results/{name}"
        results_dir.mkdir(parents=True, exist_ok=True)
        return results_dir

    def get_name(self, environment: env.Environment, memory: str) -> str:
        now = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"{environment.parsed_options.name}-{environment.parsed_options.cpu}cpu-{memory}-{environment.parsed_options.gunicorn_threads}threads-{environment.parsed_options.gunicorn_workers}workers-{now}"
