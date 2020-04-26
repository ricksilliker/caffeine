from maya.api import OpenMaya

from caffeine.logs import getActionLogger
from caffeine import steps


LOG = getActionLogger('createJoint')


def build(ctx):
    obj = OpenMaya.MFnDependencyNode().create('joint', name=ctx['name'])


    return steps.StepResponse.fromDict({
        'status': 200,
        'node': obj,
        'name': OpenMaya.MFnDependencyNode(obj).name()
    })