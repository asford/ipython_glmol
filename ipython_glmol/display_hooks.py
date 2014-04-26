import logging
logger = logging.getLogger("ipython_glmol.display_hooks")

import sys
import numpy

from .glmol_embed import PDBEmbed
from .glmol_repr import Ribbon, Helix, Sheet
from .glmol_selectors import ResidueNumber

import urllib2
import tempfile

def pdb_display(pdb_id):
    """Download and embed pdb."""
    d = urllib2.urlopen("http://www.pdb.org/pdb/files/%s.pdb"% pdb_id)
    pdb_lines = [l for l in d.readlines() if l.startswith(("ATOM", "TER", "HELIX", "SHEET"))]

    return PDBEmbed("\n".join(pdb_lines))

def extract_character_spans(string):
    """Extract all contiguous character spans from given string.
    
    returns - Character, span structured array:
            array(num_spans, [("type", "start", "end")])
    """

    if isinstance(string, basestring):
        string = numpy.fromstring(string, "S1")
    elif isinstance(string, numpy.ndarray) and string.dtype == numpy.dtype("S1"):
        pass
    else:
        raise ValueError("Unable to process input string: %r" % string)

    char_edges = list(numpy.flatnonzero(string[1:] != string[:-1]) + 1)

    return numpy.array([(string[start], start, end) for start, end in zip([0] + char_edges, char_edges + [len(string)])], dtype=[("type", "S1"), ("start", int), ("end", int)])

def pose_display(pose, **repr_entries):
    """Setup embed display for rosetta.core.pose object with sensible default representation."""
    import re
    import cStringIO as StringIO
    from rosetta.utility import ostream
    import rosetta.core.scoring.dssp

    logger.debug("pose_display\n%s\nrepr_entries\n%r", pose, repr_entries)
    
    sio = StringIO.StringIO()
    pose.dump_pdb(ostream(sio))
    pdb_string = sio.getvalue()

    residue_properties = {}
    residue_properties["residue_number"] = range(pose.n_residue())

    if pose.energies().energies_updated() and hasattr( pose.energies(), "residue_total_energies_array"):
        residue_energies = pose.energies().residue_total_energies_array()
        for n in residue_energies.dtype.names:
            residue_properties[n] = list(residue_energies[n])

    embed = PDBEmbed(pdb_string, residue_properties)

    ss_string = pose.secstruct()
    # Missing pose secondary structure assignment, recalculate
    if not re.search("[^L]", ss_string):
        logger.debug("Performing DSSP.")
        ss_string = rosetta.core.scoring.dssp.Dssp(pose).get_dssp_secstruct()

    embed += ss_repr_entries( ss_string )

    if default_pose_repr:
        embed += default_pose_repr

    return embed

def ss_repr_entries(ss_sequence):
    """Generate repr objects for the given secondary structure sequence."""

    logger.debug("ss_sequence: %s", ss_sequence)

    ss_spans = extract_character_spans(ss_sequence)

    repr_entries = []
    for s, start, end in ss_spans:
        if s == "H":
            repr_entries.append( Helix(ResidueNumber[start:end]) )
        elif s == "E":
            repr_entries.append( Sheet(ResidueNumber[start:end]) )

    return repr_entries

def setup_display_hooks():
    """Setup display hooks for all currently loaded modules."""
    if "rosetta" in sys.modules:
        import rosetta.core.pose
        rosetta.core.pose.Pose._repr_javascript_ = lambda self: pose_display(self)._repr_javascript_()

default_pose_repr = Ribbon()
