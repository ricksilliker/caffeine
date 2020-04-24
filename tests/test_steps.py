import pytest

from maya import cmds
from maya.api import OpenMaya

from caffeine import steps


def test_load_default_steps_valid():
    defaultSteps = steps.loadDefaultSteps()
    assert len(defaultSteps) > 0

def test_load_empty_step_invalid(tmpdir):
    p = tmpdir.mkdir("bad.step")
    step, err = steps.loadStepFromPath(str(p))
    assert step is None