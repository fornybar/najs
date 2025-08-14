import asyncio
import http.client
import os
import shutil
import signal
import subprocess
import tempfile
import time
import unittest
from pathlib import Path

import pytest

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
SERVER_BIN_DIR_NAME = "nats-server"


def get_config_file(file_path):
    return os.path.join(THIS_DIR, file_path)


class NATSD:
    def __init__(
        self,
        port=4222,
        user="",
        password="",
        token="",
        timeout=0,
        http_port=8222,
        debug=False,
        tls=False,
        cluster_listen=None,
        routes=None,
        config_file=None,
        with_jetstream=None,
    ):
        self.port = port
        self.user = user
        self.password = password
        self.timeout = timeout
        self.http_port = http_port
        self.proc = None
        self.tls = tls
        self.token = token
        self.cluster_listen = cluster_listen
        self.routes = routes or []
        self.bin_name = "nats-server"
        self.config_file = config_file
        self.debug = debug or os.environ.get("DEBUG_NATS_TEST") == "true"
        self.with_jetstream = with_jetstream
        self.store_dir = None

        if with_jetstream:
            self.store_dir = tempfile.mkdtemp()

    def start(self):
        # Default path
        if Path(self.bin_name).is_file():
            self.bin_name = Path(self.bin_name).absolute()
        # Path in `../scripts/install_nats.sh`
        elif Path.home().joinpath(SERVER_BIN_DIR_NAME, self.bin_name).is_file():
            self.bin_name = str(
                Path.home().joinpath(SERVER_BIN_DIR_NAME, self.bin_name),
            )
        # This directory contains binary
        elif Path(THIS_DIR).joinpath(self.bin_name).is_file():
            self.bin_name = str(Path(THIS_DIR).joinpath(self.bin_name))

        cmd = [
            self.bin_name,
            "-p",
            "%d" % self.port,
            "-m",
            "%d" % self.http_port,
            "-a",
            "127.0.0.1",
        ]
        if self.user:
            cmd.append("--user")
            cmd.append(self.user)
        if self.password:
            cmd.append("--pass")
            cmd.append(self.password)

        if self.token:
            cmd.append("--auth")
            cmd.append(self.token)

        if self.debug:
            cmd.append("-DV")

        if self.with_jetstream:
            cmd.append("-js")
            cmd.append(f"-sd={self.store_dir}")

        if self.tls:
            cmd.append("--tls")
            cmd.append("--tlscert")
            cmd.append(get_config_file("certs/server-cert.pem"))
            cmd.append("--tlskey")
            cmd.append(get_config_file("certs/server-key.pem"))
            cmd.append("--tlsverify")
            cmd.append("--tlscacert")
            cmd.append(get_config_file("certs/ca.pem"))

        if self.cluster_listen is not None:
            cmd.append("--cluster_listen")
            cmd.append(self.cluster_listen)

        if len(self.routes) > 0:
            cmd.append("--routes")
            cmd.append(",".join(self.routes))
            cmd.append("--cluster_name")
            cmd.append("CLUSTER")

        if self.config_file is not None:
            cmd.append("--config")
            cmd.append(self.config_file)

        if self.debug:
            self.proc = subprocess.Popen(cmd)
        else:
            self.proc = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

        if self.debug:
            if self.proc is None:
                print(
                    "[\031[0;33mDEBUG\033[0;0m] Failed to start server listening on port %d started."
                    % self.port,
                )
            else:
                print(
                    "[\033[0;33mDEBUG\033[0;0m] Server listening on port %d started."
                    % self.port,
                )
        return self.proc

    def stop(self):
        if self.debug:
            print(
                "[\033[0;33mDEBUG\033[0;0m] Server listening on %d will stop."
                % self.port,
            )

        if self.debug:
            if self.proc is None:
                print(
                    "[\033[0;31mDEBUG\033[0;0m] Failed terminating server listening on port %d"
                    % self.port,
                )

        if self.proc.returncode is not None:
            if self.debug:
                print(
                    f"[\033[0;31mDEBUG\033[0;0m] Server listening on port {self.port} finished running already with exit {self.proc.returncode}",
                )
        else:
            os.kill(self.proc.pid, signal.SIGKILL)
            self.proc.wait()
            if self.debug:
                print(
                    "[\033[0;33mDEBUG\033[0;0m] Server listening on %d was stopped."
                    % self.port,
                )


def start_natsd(natsd: NATSD):
    natsd.start()

    endpoint = f"127.0.0.1:{natsd.http_port}"
    retries = 0
    while True:
        if retries > 100:
            break

        try:
            httpclient = http.client.HTTPConnection(endpoint, timeout=5)
            httpclient.request("GET", "/varz")
            response = httpclient.getresponse()
            if response.status == 200:
                break
        except:
            retries += 1
            time.sleep(0.1)


# class SingleServerTestCase(unittest.TestCase):
@pytest.fixture
def single_server():
    server_pool = []
    loop = asyncio.new_event_loop()

    server = NATSD(port=4222, with_jetstream=True)
    server_pool.append(server)
    for natsd in server_pool:
        start_natsd(natsd)

    print("NATSD", natsd.store_dir)
    yield server

    for natsd in server_pool:
        natsd.stop()
        shutil.rmtree(natsd.store_dir)

    loop.close()
