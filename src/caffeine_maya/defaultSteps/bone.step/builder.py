from maya.api import OpenMaya

from caffeine.logs import getActionLogger
from caffeine_maya.core import addRigComponentAttr


LOG = getActionLogger('bone')


def build(ctx):
    pass


def save(ctx, response):
    pass


def addCallback():
    modifier = OpenMaya.MDagModifier()
    mobject = modifier.createNode('joint')
    modifier.doIt()
    dependNode = OpenMaya.MFnDependencyNode(mobject)
    dependNode.setName('NewBone#')
    addRigComponentAttr(mobject)
