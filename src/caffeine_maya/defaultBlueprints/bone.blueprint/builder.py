from maya.api import OpenMaya

from caffeine.logs import getActionLogger
from caffeine.blueprints import BlueprintResponse
from caffeine_maya.core import addRigComponentAttr
from maya_utils import common, transforms


LOG = getActionLogger('bone')


def create(ctx):
    modifier = OpenMaya.MDagModifier()
    mobject = modifier.createNode('joint')
    modifier.doIt()
    dependNode = OpenMaya.MFnDependencyNode(mobject)
    dependNode.setName('NewBone#')
    addRigComponentAttr(mobject)

    return BlueprintResponse.fromDict({
        'status': 201,
        'node': mobject
    })


def initCallback(**kwargs):
    node = kwargs['node']

    nodeName = common.get_name(node)
    nodeSSC = common.get_plug(node, 'segmentScaleCompensate').asBool()
    nodeTransform = transforms.get_local_matrix(node)

    return {
        'name': nodeName,
        'bone': node,
        'ssc': nodeSSC,
        'initialTransform': nodeTransform
    }
