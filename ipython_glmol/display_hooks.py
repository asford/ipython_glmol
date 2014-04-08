import logging
logger = logging.getLogger("ipython_glmol.display_hooks")

import sys
import numpy

from .glmol_embed import PDBEmbed
from .glmol_repr import Ribbon, Helix, Sheet

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

    residue_ids = [pose.pdb_info().number(i + 1) for i in xrange(pose.n_residue())]

    residue_properties = {}
    residue_properties["residue_number"] = dict((residue_id, i) for i, residue_id in enumerate(residue_ids))

    if pose.energies().energies_updated() and hasattr( pose.energies(), "residue_total_energies_array"):
        residue_energies = pose.energies().residue_total_energies_array()
        for n in residue_energies.dtype.names:
            residue_properties[n] = dict((residue_id, residue_energies[i][n]) for i, residue_id in enumerate(residue_ids))

    embed = PDBEmbed(pdb_string, residue_properties)

    ss_string = pose.secstruct()
    # Missing pose secondary structure assignment, recalculate
    if not re.search("[^L]", ss_string):
        logger.debug("Performing DSSP.")
        ss_string = rosetta.core.scoring.dssp.Dssp(pose).get_dssp_secstruct()

    embed += ss_repr_entries( ss_string, residue_ids )

    if default_pose_repr:
        embed += default_pose_repr

    return embed

def ss_repr_entries(ss_sequence, residue_ids):
    """Generate repr objects for the given secondary structure sequence."""

    logger.debug("ss_sequence: %s", ss_sequence)

    ss_spans = extract_character_spans(ss_sequence)

    sheet_spans = []
    helix_spans = []
    for s, start, end in ss_spans:
        span_residue_ids = residue_ids[start:end]

        if numpy.all(span_residue_ids[:-1] < span_residue_ids[1:]):
            residue_span = "%s-%s" % (span_residue_ids[0], span_residue_ids[-1])
        else:
            residue_span = ",".join(str(i) for i in span_residue_ids)

        logger.debug("ss span: %s residue_span: %s", (s, start, end), residue_span)

        if s == "H":
            helix_spans.append(residue_span)
        elif s == "E":
            sheet_spans.append(residue_span)

    repr_entries = []

    if sheet_spans:
        repr_entries.append( Sheet("residue %s" % ",".join(r for r in sheet_spans)) )

    if helix_spans:
        repr_entries.append( Helix("residue %s" % ",".join(r for r in helix_spans)) )

    return repr_entries

def setup_display_hooks():
    """Setup display hooks for all currently loaded modules."""
    if "rosetta" in sys.modules:
        import rosetta.core.pose
        rosetta.core.pose.Pose._repr_javascript_ = lambda self: pose_display(self)._repr_javascript_()

default_pose_repr = Ribbon()
