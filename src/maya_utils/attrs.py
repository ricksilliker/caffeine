# built-in imports
import logging

# maya imports
from maya.api import OpenMaya
from maya import cmds


# constants
LOG = logging.getLogger(__name__)


def hasAttr(mobject, attrName):
    depNode = OpenMaya.MFnDependencyNode(mobject)
    a = depNode.attribute(attrName)

    if not a.isNull():
        return True

    return False