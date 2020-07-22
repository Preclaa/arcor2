# -*- coding: utf-8 -*-

import os
import subprocess
import time
from typing import Iterator

import pytest  # type: ignore

from arcor2.clients import scene_service
from arcor2.data.common import Pose
from arcor2.data.object_type import Box
from arcor2.nodes.scene_mock import PORT as SCENE_MOCK_PORT
from arcor2.object_types.abstract import GenericWithPose


def finish_processes(processes) -> None:

    for proc in processes:
        proc.terminate()
        proc.wait()
        print(proc.communicate())


@pytest.fixture()
def start_processes() -> Iterator[None]:

    my_env = os.environ.copy()
    my_env["ARCOR2_SCENE_SERVICE_URL"] = f"http://0.0.0.0:{SCENE_MOCK_PORT}"
    scene_service.URL = my_env["ARCOR2_SCENE_SERVICE_URL"]

    processes = []

    for cmd in ("arcor2_scene_mock",):
        processes.append(subprocess.Popen(cmd, env=my_env, stdout=subprocess.PIPE))

    time.sleep(2)

    yield None

    finish_processes(processes)


def test_generic_with_pose(start_processes: None) -> None:

    obj = GenericWithPose("id", "name", Pose(), Box("boxId", 0.1, 0.1, 0.1))

    ids = scene_service.collision_ids()
    assert len(ids) == 1
    assert obj.id in ids

    obj.pose = Pose()

    obj.cleanup()
    assert not scene_service.collision_ids()
