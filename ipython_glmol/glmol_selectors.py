from abc import abstractproperty, ABCMeta
import collections
from copy import deepcopy

class GLMolSelectorMeta(ABCMeta):
    def __getitem__(self, arg):
        return self(arg)

class GLMolSelector(object):
    __metaclass__ = ABCMeta

    @abstractproperty
    def selector(self):
        return "%s %s" % (self.selector_name, self.selection_to_string(self.selection))

    @property
    def glmol_selection_string(self):
        return "; ".join( [self.selector] + [s.selector for s in self.subselections] )
    
    def __add__(self, subselection):
        assert isinstance(subselection, GLMolSubSelector)

        c = deepcopy(self)
        c.subselections.append(subselection)
        return c

class All(GLMolSelector):
    def __init__(self, subselections = None):
        self.subselections = subselections if subselections else []

    @property
    def selector_name(self):
        return "all"

    @property
    def selector(self):
        return self.selector_name

    def __repr__(self):
        return "%s(subselections = %r)" % (self.__class__.__name__, self.subselections)

class GLMolTypeSelector(GLMolSelector):
    __metaclass__ = GLMolSelectorMeta

    def __init__(self, selection, subselections = []):
        self.selection_to_string(selection)
        self.selection = selection
        self.subselections = subselections if subselections else []

    @abstractproperty
    def selector_name(self):
        pass

    @property
    def selector(self):
        return "%s %s" % (self.selector_name, self.selection_to_string(self.selection))
    
    @classmethod
    def selection_to_string(cls, selection):
        if isinstance(selection, slice):
            assert selection.start is not None and selection.stop is not None
            return "%s-%s" % (selection.start, selection.stop)
        elif isinstance(selection, collections.Iterable):
            return ",".join(map(str, selection))
        else:
            return str(selection)

    def __repr__(self):
        return "%s(selection = %r, subselections = %r)" % (self.__class__.__name__, self.selection, self.subselections)

class Chain(GLMolTypeSelector):
    @property
    def selector_name(self):
        return "chain"

class ChainNumber(GLMolTypeSelector):
    @property
    def selector_name(self):
        return "chain_number"

class Residue(GLMolTypeSelector):
    @property
    def selector_name(self):
        return "resi"

class ResidueNumber(GLMolTypeSelector):
    @property
    def selector_name(self):
        return "residue_number"

class Atom(GLMolTypeSelector):
    @property
    def selector_name(self):
        return "atomi"

class GLMolSubSelector(object):
    __metaclass__ = ABCMeta

    @abstractproperty
    def selector(self):
        pass

    def __repr__(self):
        return "%s()" % self.__class__.__name__

class Carbon(GLMolSubSelector):
    @property
    def selector(self):
        return "elem C"

class Heavyatom(GLMolSubSelector):
    @property
    def selector(self):
        return "heavy"
    
class Backbone(GLMolSubSelector):
    @property
    def selector(self):
        return "bb"
