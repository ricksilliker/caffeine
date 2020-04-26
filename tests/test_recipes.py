import os

import pytest
import yaml

from maya import cmds
from maya.api import OpenMaya


from caffeine import recipes


@pytest.fixture(autouse=True)
def start_new_scene():
    cmds.file(new=True, force=True)


def test_load_default_recipes_valid():
    defaultRecipes = recipes.loadDefaultRecipes()
    assert len(defaultRecipes) > 0


def test_default_fk_chain():
    path = os.path.join(recipes.DEFAULT_RECIPES, 'fk_chain.yaml')
    recipe = recipes.Recipe.fromPath(path)

    assert recipe._currentStep == 0
    recipe.build()
    joints = cmds.ls(type='joint')
    assert len(joints) == 1

    assert recipe._currentStep == 1
    recipe.build()
    nurbs = cmds.ls(type='nurbsCurve')
    assert len(nurbs) == 1
    assert len(cmds.ls('fk_0')) == 1

    assert recipe._currentStep == 2
    recipe.build()
    assert len(cmds.ls(type='constraint')) == 2


def test_save_recipe(tmpdir):
    buildPath = str(tmpdir.join('validSave.yaml'))
    path = os.path.join(recipes.DEFAULT_RECIPES, 'fk_chain.yaml')
    recipe = recipes.Recipe.fromPath(path)
    recipe.setBuildPath(buildPath)

    recipe.build()
    cmds.xform('fk_0', ws=True, t=[5, 3, 1], ro=[90, 0, -90])
    recipe.save()

    with open(buildPath, 'r') as fp:
        data = yaml.safe_load(fp)
        assert data['stages'][0]['steps'][0]['com.caffeine.createJoint']['position'] == [5, 3, 1]
        assert data['stages'][0]['steps'][0]['com.caffeine.createJoint']['orient'] == pytest.approx([90, 0, -90])
        assert data['stages'][0]['steps'][0]['com.caffeine.createJoint']['ssc'] == True
        assert data['stages'][0]['steps'][0]['com.caffeine.createJoint']['name'] == 'fk_0'
