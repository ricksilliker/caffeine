from maya.api import OpenMaya
from maya import cmds

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


def save(ctx, response):
    n = response['node']
    nodeName = OpenMaya.MFnDagNode(n).fullPathName()
    ctx['name'] = nodeName.split('|')[-1]
    
    pos = cmds.xform(nodeName, q=True, ws=True, t=True)
    ctx['position'] = pos

    rot = cmds.xform(nodeName, q=True, ws=True, ro=True)
    ctx['orient'] = rot

    ctx['ssc'] = cmds.getAttr('{0}.ssc'.format(nodeName))
    