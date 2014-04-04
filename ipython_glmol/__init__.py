from .glmol_embed import (PDBEmbed, glmol_source_library)
from .display_hooks import setup_display_hooks
from .test_data import (test_repr_data, test_pdb_data)
from .glmol_repr import Sphere, Line, Ribbon, Stick, ResidueSpectrum, Color

import glmol_embed
setup_display_hooks()
