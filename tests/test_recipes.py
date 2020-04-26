import os

import pytest
from maya import cmds
from maya.api import OpenMaya

from caffeine import recipes


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
    print cmds.ls()
    assert len(nurbs) == 1
    assert len(cmds.ls('fk_0')) == 1

    assert recipe._currentStep == 2
    recipe.build()
    assert len(cmds.ls(type='constraint')) == 2
