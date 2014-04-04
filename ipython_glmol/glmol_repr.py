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

class Color(EmbedReprModifier):
    def __init__(self, color, selector = "all"):
        self.color = color
        self.selector = selector

    def apply_to_embed(self, embed):
        color_selector = "%s:%s" % (self.color, self.selector)
        embed.add_repr_entry("color", color_selector)

class ResidueSpectrum(EmbedReprModifier):
    def __init__(self, colors, per_residue_scores, sub_selector = None, thresholds = None):
        self.colors = colors
        self.per_residue_scores = per_residue_scores

        self.sub_selector = sub_selector

        if thresholds:
            assert len(thresholds) == 2
        self.thresholds = thresholds

    def apply_to_embed(self, embed):
        import matplotlib.colors
        
        cmap = matplotlib.colors.LinearSegmentedColormap.from_list("residue_spectrum", self.colors)

        if self.thresholds:
            vmin, vmax = self.thresholds
            sm = matplotlib.cm.ScalarMappable(matplotlib.colors.Normalize(vmin=vmin, vmax=vmax), cmap=cmap)
        else:
            sm = matplotlib.cm.ScalarMappable(matplotlib.colors.Normalize(), cmap=cmap)

        color_entries = [matplotlib.colors.rgb2hex(c) for c in sm.to_rgba(self.per_residue_scores)]
        color_selector = ["%s:residue %i" %(c, i + 1) for i, c in enumerate(color_entries)]

        if self.sub_selector:
            color_selector = ["%s; %s" % (c, self.sub_selector) for c in color_selector]

        embed.add_repr_entry("color", color_selector)

class Sheet(SimpleReprModifier):
    def __init__(self, selector):
        SimpleReprModifier.__init__(self, "sheet", selector)

class Helix(SimpleReprModifier):
    def __init__(self, selector):
        SimpleReprModifier.__init__(self, "helix", selector)
