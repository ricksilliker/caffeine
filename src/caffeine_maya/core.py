import os

from maya.api import OpenMaya

from caffeine import steps, blueprints


def addRigComponentAttr(mobject):
    modifier = OpenMaya.MDagModifier()
    attr = OpenMaya.MFnGenericAttribute().create('rigComponent', 'rigComponent')
    modifier.addAttribute(mobject, attr)
    modifier.doIt()


def hasRigComponentAttr(obj):
    if isinstance(obj, OpenMaya.MObject):
        return OpenMaya.MFnDependencyNode(obj).hasAttribute('rigComponent')
    if isinstance(obj, (OpenMaya.MFnDagNode, OpenMaya.MFnDependencyNode)):
        return obj.hasAttribute('rigComponent')
    return False


def getAvailableBlueprints():
    d = os.path.join(os.path.dirname(__file__), 'defaultBlueprints')
    return blueprints.loadAvailableByTitle(d)


def getBlueprintFromNode(node):
    if node.hasFn(OpenMaya.MFn.kJoint):
        bp = getAvailableBlueprints()['Bone']
        inst = bp.getInstance()
        inst.updateFromContext(node=node.node())
        return inst


def getActiveBlueprints(hierarchy):
    def _addToHierarchy(h, node, parentIndex=None):
        bp = getBlueprintFromNode(node)
        if parentIndex is None:
            index = hierarchy.addBlueprint(bp)
        else:
            index = hierarchy.addChild(parentIndex, bp)
        for i in range(node.childCount()):
            dagNode = OpenMaya.MFnDagNode(node.child(i))
            _addToHierarchy(h, dagNode, index)

    for n in getTopNodes():
        _addToHierarchy(hierarchy, n)

    return hierarchy


def getTopNodes():
    iterator = OpenMaya.MItDag()
    topNodes = []
    while not iterator.isDone():
        if iterator.depth() > 1:
            iterator.next()
            continue
        if iterator.currentItem.hasFn(OpenMaya.MFn.kWorld):
            iterator.next()
            continue
        if not hasRigComponentAttr(dagNode):
            iterator.next()
            continue
        dagNode = OpenMaya.MFnDagNode(iterator.getPath())
        topNodes.append(dagNode)
        iterator.next()
    return topNodes
