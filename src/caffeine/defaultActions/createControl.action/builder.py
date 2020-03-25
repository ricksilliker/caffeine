import os
import json

from maya import cmds
from maya.api import OpenMaya


DATA_FILE = os.path.join(os.path.dirname(__file__), 'defaultControls.json')


def build(ctx):
    mobject = OpenMaya.MFnDagNode('transform', ctx['name'])
    transform = OpenMaya.MFnDagNode(mobject)

    with open(DATA_FILE, 'r') as fp:
        controlsDict = json.load(fp)

        shapeData = controlsDict.get(ctx['shape'], None)
        if shapeData is None:
            return

        form = OpenMaya.MFnNurbsCurve.kPeriodic
        if not shapeData.get('periodic', False):
            form = OpenMaya.MFnNurbsCurve.kOpen

        points = []
        for pt in shapeData.get('controlPoints', []):
            mpoint = OpenMaya.MPoint(pt[0], pt[1], pt[2], 1.0)
            points.append(mpoint)

        addShape(transform, points, knots, degree, form)
        

def addShape(dagTransform, controlPoints, knots, degree, form):
    newCurve = OpenMaya.MFnNurbsCurve()
    newCurve.degree = degree
    newCurve.form = form
    newCurve.setCVPositions(space=OpenMaya.MSpace.kObject)
    newCurve.setKnots(knots, knots[0], len(knots)-1)

    dagTransform.addChild(
        node=newCurve,
        index=OpenMaya.MFnDagNode.kNextPos,
        keepExistingParents=False
    )