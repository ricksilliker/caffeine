import os
import json

from maya import cmds
from maya.api import OpenMaya

from caffeine.logs import getActionLogger
from caffeine import steps


DATA_FILE = os.path.join(os.path.dirname(__file__), 'defaultControls.json')
LOG = getActionLogger('createControl')


def build(ctx):
    mobject = OpenMaya.MFnDagNode().create('transform', name=ctx['name'])
    LOG.info(mobject)

    with open(DATA_FILE, 'r') as fp:
        controlsDict = json.load(fp)
        shapeData = controlsDict.get(ctx['shape'], None)
        if shapeData is None:
            return steps.StepResponse.fromDict({
                'status': 400,
                'node': mobject
            })

        form = OpenMaya.MFnNurbsCurve.kPeriodic
        if not shapeData.get('periodic', False):
            form = OpenMaya.MFnNurbsCurve.kOpen

        points = []
        for pt in shapeData.get('controlPoints', []):
            mpoint = OpenMaya.MPoint(pt[0], pt[1], pt[2], 1.0)
            points.append(mpoint)

        degree = shapeData.get('degree', 3)
        
        knots = shapeData.get('knots', [])

        LOG.info('Getting shape data.', degree=degree, knots=knots, CVs=points)

        addShape(mobject, points, knots, degree, form)

    return steps.StepResponse.fromDict({
        'status': 200,
        'node': mobject,
        'name': OpenMaya.MFnDependencyNode(mobject).name()
    })


def save(ctx, response):
    pass


def addShape(dagTransform, controlPoints, knots, degree, form):
    newCurve = OpenMaya.MFnNurbsCurve().create(
        controlPoints,
        knots,
        degree,
        form,
        False,
        True,
        dagTransform
    )
    return newCurve