import json

from maya.api import OpenMaya


def build(ctx):

    for shape in get_geometry(ctx['geometry']):
        shapeName = get_name(shape)
        vert_names = '{0}.vtx[:]'.format(shape)

        sel = OpenMaya.MSelectionList()
        sel.add(vert_names)
        p, vertices = sel.getComponent(0)

        