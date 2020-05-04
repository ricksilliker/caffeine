from maya import cmds

from caffeine.logs import getActionLogger

from maya_utils import common

LOG = getActionLogger('jointOrientOffset')


def build(ctx):
    mobject = common.get_mobject(ctx['nodePath'])
    for n, attr in enumerate(('jox', 'joy', 'joz')):
        plug = common.get_plug(mobject, attr)
        value = plug.getFloat() + ctx['offset'][n]
        plug.setFloat(value)


def save(ctx, response):
    pass