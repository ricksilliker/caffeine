from maya import cmds

from caffeine.logs import getActionLogger


LOG = getActionLogger('constrain')


def build(ctx):
    LOG.info('Building task.')
    cmds.parentConstraint(ctx['target'], ctx['followers'], mo=ctx['maintainOffset'])
    cmds.scaleConstraint(ctx['target'], ctx['followers'], mo=ctx['maintainOffset'])