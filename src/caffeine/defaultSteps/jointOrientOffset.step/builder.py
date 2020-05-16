from maya import cmds
from maya.api import OpenMaya

from caffeine import steps
from caffeine.logs import getActionLogger

from maya_utils import common

LOG = getActionLogger('jointOrientOffset')


def build(ctx):
    newOrient = []
    mobject = common.get_mobject(ctx['nodePath'])
    for n, attr in enumerate(('jox', 'joy', 'joz')):
        plug = common.get_plug(mobject, attr)
        value = plug.getFloat() + ctx['offset'][n]
        newOrient.append(value)
        plug.setFloat(value)

    return steps.StepResponse.fromDict({
        'status': 200,
        'orientation': OpenMaya.MVector(newOrient)
    })


def save(ctx, response):
    pass