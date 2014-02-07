import logging
logger = logging.getLogger("ipython_glmol.display_hooks")

import sys
from .glmol_embed import PDBEmbed

import urllib2
import tempfile

def pdb_display(pdb_id):
    """Download and embed pdb."""
    d = urllib2.urlopen("http://www.pdb.org/pdb/files/%s.pdb"% pdb_id)
    pdb_lines = [l for l in d.readlines() if l.startswith(("ATOM", "TER", "HELIX", "SHEET"))]

    return PDBEmbed("\n".join(pdb_lines), "")

def extract_character_spans(string):
    """Extract all contiguous character spans from given string.
    
    returns - Character, span structured array:
            array(num_spans, [("type", "start", "end")])
    """
    import numpy

    if isinstance(string, basestring):
        string = numpy.fromstring(string, "S1")
    elif isinstance(string, numpy.array) and string.dtype == numpy.dtype("S1"):
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

    ss_string = pose.secstruct()
    
    # Missing pose secondary structure assignment, recalculate
    if not re.search("[^L]", ss_string):
        logger.debug("Performing DSSP.")
        ss_string = rosetta.core.scoring.dssp.Dssp(pose).get_dssp_secstruct()

    logger.debug("ss_string: %s", ss_string)

    ss_spans = extract_character_spans(ss_string)

    sheet_spans = []
    helix_spans = []
    for s, start, end in ss_spans:

        residue_span = "%s-%s" % (pose.pdb_info().number(start+1), pose.pdb_info().number(end)+1)

        logger.debug("ss span: %s residue_span: %s", (s, start, end), residue_span)

        if s == "H":
            helix_spans.append(residue_span)
        elif s == "E":
            sheet_spans.append(residue_span)

    if sheet_spans:
        repr_entries["sheet"] = "residue %s" % ",".join(r for r in sheet_spans)

    if helix_spans:
        repr_entries["helix"] = "residue %s" % ",".join(r for r in helix_spans)


    if not "ribbon" in repr_entries:
        repr_entries["ribbon"] = "all"

    return PDBEmbed(
            pdb_string,
            **repr_entries)

def setup_display_hooks():
    """Setup display hooks for all currently loaded modules."""
    if "rosetta" in sys.modules:
        import rosetta.core.pose
        rosetta.core.pose.Pose._repr_javascript_ = lambda self: pose_display(self)._repr_javascript_()
