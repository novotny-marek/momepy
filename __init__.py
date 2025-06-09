from .momeq.momeQPluginProvider import MomeQPluginProvider

def classFactory(iface):
    return MomeQPluginProvider()