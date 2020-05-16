from maya import cmds

from caffeine import steps
from caffeine.logs import getActionLogger


LOG = getActionLogger('jointOrientOffset')
SUPPORTED_TYPES = {
    '.obj': 'OBJ',
    '.fbx': 'FBX',
    '.ma': 'mayaAscii',
    '.mb': 'mayaBinary'
}


def build(ctx):
    cmds.namespace(set=':')
    ns_list = cmds.namespaceInfo(listOnlyNamespaces=True)
    if ctx['namespace'] and ctx['namespace'] not in ns_list:
        cmds.namespace(add=ctx['namespace'])
    
    cmds.namespace(set=ctx['namespace'])
    filetype = get_filetype(ctx['path'])
    cmds.file(ctx['path'], i=True, typ=filetype)
    cmds.namespace(setNamespace=':')

    return steps.StepResponse.fromDict({
        'status': 200
    })


def save(ctx, response):
    pass


def get_filetype(path):
    for ext in SUPPORTED_TYPES:
        if path.endswith(ext):
            return SUPPORTED_TYPES[ext]