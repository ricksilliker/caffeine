# built-in imports
import logging

# maya imports
from maya.api import OpenMaya
from maya import cmds

import common

# constants
LOG = logging.getLogger(__name__)


def getUParam(mobject, point, tolerance=0.001):
    m_point = OpenMaya.MPoint(point)
    curveFn = OpenMaya.MFnNurbsCurve(mobject)

    isOnCurve = curveFn.isPointOnCurve(m_point, OpenMaya.MFnNurbsCurve.kPointTolerance, OpenMaya.MSpace.kWorld)
    if isOnCurve:
        param = curveFn.getParamAtPoint(m_point, tolerance=tolerance, space=OpenMaya.MSpace.kWorld)
    else:
        point = curveFn.closestPoint(m_point, space=OpenMaya.MSpace.kWorld)
        param = curveFn.getParamAtPoint(m_point, space=OpenMaya.MSpace.kWorld)

    return param