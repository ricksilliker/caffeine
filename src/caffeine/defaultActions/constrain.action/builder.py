from maya import cmds

from caffeine.logs import getActionLogger


LOG = getActionLogger('constrain')


def build(ctx):
    LOG.info('Building task.')