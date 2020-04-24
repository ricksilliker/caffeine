from maya.api import OpenMaya

from caffeine.logs import getActionLogger


LOG = getActionLogger('createJoint')


def build(ctx):
    obj = OpenMaya.MFnDependencyNode().create('joint', name=ctx['name'])

