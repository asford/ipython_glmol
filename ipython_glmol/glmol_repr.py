from .glmol_embed import EmbedReprModifier

class Clear(EmbedReprModifier):
    clear_types = ("ribbon", "stick", "line", "sphere")
    def __init__(self):
        pass

    def apply_to_embed(self, embed):
        for t in self.clear_types:
            embed.repr_entries[t] = []

class SimpleReprModifier(EmbedReprModifier):
    def __init__(self, repr_type, selector="all"):
        self.repr_type = repr_type
        self.selector = selector

    def apply_to_embed(self, embed):
        if not self.selector:
            embed.repr_entries[self.repr_type] = []
        else:
            embed.add_repr_entry(self.repr_type, self.selector)

class Ribbon(SimpleReprModifier):
    def __init__(self, selector = "all"):
        SimpleReprModifier.__init__(self, "ribbon", selector)

class Stick(SimpleReprModifier):
    def __init__(self, selector = "all"):
        SimpleReprModifier.__init__(self, "stick", selector)

class Line(SimpleReprModifier):
    def __init__(self, selector = "all"):
        SimpleReprModifier.__init__(self, "line", selector)

class Sphere(SimpleReprModifier):
    def __init__(self, selector = "all"):
        SimpleReprModifier.__init__(self, "sphere", selector)

class BackgroundColor(EmbedReprModifier):
    def __init__(self, color):
        self.color = color

    def apply_to_embed(self, embed):
        embed.add_repr_entry("bgcolor", self.color)

class Color(EmbedReprModifier):
    def __init__(self, color, selector = "all"):
        self.color = color
        self.selector = selector

    def apply_to_embed(self, embed):
        color_selector = "%s:%s" % (self.color, self.selector)
        embed.add_repr_entry("color", color_selector)

class ResidueSpectrum(EmbedReprModifier):
    def __init__(self, residue_property, colors = None, sub_selector = None, thresholds = None):
        self.residue_property = residue_property
        self.colors = colors
        self.sub_selector = sub_selector

        if thresholds:
            assert len(thresholds) == 2
        self.thresholds = thresholds

    def apply_to_embed(self, embed):
        import matplotlib.cm
        import matplotlib.colors
        from matplotlib.colors import rgb2hex

        if isinstance( self.colors, matplotlib.colors.Colormap ):
            cmap = self.colors
        elif isinstance( self.colors, basestring ) or self.colors is None:
            cmap = matplotlib.cm.get_cmap(self.colors)
        else:
            cmap = matplotlib.colors.LinearSegmentedColormap.from_list("residue_spectrum", self.colors)

        if self.thresholds:
            vmin, vmax = self.thresholds
            sm = matplotlib.cm.ScalarMappable(matplotlib.colors.Normalize(vmin=vmin, vmax=vmax), cmap=cmap)
        else:
            sm = matplotlib.cm.ScalarMappable(matplotlib.colors.Normalize(), cmap=cmap)

        if not self.residue_property in embed.residue_properties:
            raise ValueError("Unable to load residue property: %s Available properties: %s" % (self.residue_property, embed.residue_properties.keys()))

        color_entries = map(rgb2hex, sm.to_rgba(embed.residue_properties[self.residue_property].values()))
        
        color_selector = ["%s:residue %i" %(color_entry, residue_id) for residue_id, color_entry in zip( embed.residue_properties[self.residue_property].keys(), color_entries )]

        if self.sub_selector:
            color_selector = ["%s; %s" % (c, self.sub_selector) for c in color_selector]

        embed.add_repr_entry("color", color_selector)

class Sheet(SimpleReprModifier):
    def __init__(self, selector):
        SimpleReprModifier.__init__(self, "sheet", selector)

class Helix(SimpleReprModifier):
    def __init__(self, selector):
        SimpleReprModifier.__init__(self, "helix", selector)
