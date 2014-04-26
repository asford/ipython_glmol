from abc import abstractproperty, ABCMeta

from .glmol_embed import EmbedReprModifier
from .glmol_selectors import GLMolSelector, GLMolSubSelector, All, ResidueNumber

class Clear(EmbedReprModifier):
    clear_types = ("ribbon", "stick", "line", "sphere")
    def __init__(self):
        pass

    def apply_to_embed(self, embed):
        for t in self.clear_types:
            embed.repr_entries[t] = []

class SimpleReprModifier(EmbedReprModifier):
    def __init__(self, selector = All() ):
        if selector is not None:
            assert isinstance(selector, (GLMolSelector, GLMolSubSelector))
            self.selector = selector if isinstance(selector, GLMolSelector) else All() + selector
        else:
            self.selector = selector

    def apply_to_embed(self, embed):
        if self.selector is None:
            embed.repr_entries[self.repr_type] = []
        else:
            embed.add_repr_entry(self.repr_type, self.selector.glmol_selection_string)

    @property
    def repr_type(self):
        return str.lower(self.__class__.__name__)

    def __repr__(self):
        return "%s(selector = %r)" % (self.__class__.__name__, self.selector)

class Ribbon(SimpleReprModifier):
    pass

class Stick(SimpleReprModifier):
    pass

class Line(SimpleReprModifier):
    pass

class Sphere(SimpleReprModifier):
    pass

class Sheet(SimpleReprModifier):
    pass

class Helix(SimpleReprModifier):
    pass

class BackgroundColor(EmbedReprModifier):
    def __init__(self, color):
        self.color = color

    def apply_to_embed(self, embed):
        embed.add_repr_entry("bgcolor", self.color)

class Color(EmbedReprModifier):
    def __init__(self, color, selector = All()):
        self.color = color

        assert isinstance(selector, (GLMolSelector, GLMolSubSelector))
        self.selector = selector if isinstance(selector, GLMolSelector) else All() + selector

    def apply_to_embed(self, embed):
        color_selector = "%s:%s" % (self.color, self.selector.glmol_selection_string)
        embed.add_repr_entry("color", color_selector)

class ResidueSpectrum(EmbedReprModifier):
    def __init__(self, residue_property, colors = None, sub_selector = None, thresholds = None):
        self.residue_property = residue_property
        self.colors = colors
        
        assert sub_selector is None or isinstance(sub_selector, GLMolSubSelector)
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

        color_entries = map(rgb2hex, sm.to_rgba(embed.residue_properties[self.residue_property]))

        selectors = [ResidueNumber[i] for i in range(len(color_entries))]
        if self.sub_selector:
            selectors = [s + self.sub_selector for s in selectors]

        embed.add_repr_entry("color",
                ["%s:%s" % (c, s.glmol_selection_string) for c, s in zip(color_entries, selectors) ])
