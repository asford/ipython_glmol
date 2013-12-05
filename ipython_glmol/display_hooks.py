import sys
from .glmol_embed import PDBEmbed

import urllib2
import tempfile

def pdb_display(pdb_id):
    """Download and embed pdb."""
    d = urllib2.urlopen("http://www.pdb.org/pdb/files/%s.pdb"% pdb_id)
    pdb_lines = [l for l in d.readlines() if l.startswith(("ATOM", "TER", "HELIX", "SHEET"))]

    return PDBEmbed("\n".join(pdb_lines), "")

def pose_display(pose):
    """Setup embed display for rosetta.core.pose object with sensible default representation."""
    import re
    import cStringIO as StringIO
    from rosetta.utility import ostream
    import rosetta.core.scoring.dssp
    
    sio = StringIO.StringIO()
    pose.dump_pdb(ostream(sio))
    pdb_string = sio.getvalue()

    ss_string = pose.secstruct()
    
    # Missing pose secondary structure assignment, recalculate
    if not re.search("[^L]", ss_string):
        ss_string = rosetta.core.scoring.dssp.Dssp(pose).get_dssp_secstruct()

    ss_map = [(ss_string[i-1], pose.pdb_info().number(i)) for i in xrange(1, pose.n_residue() + 1)]
    helix_res = [r for (s, r) in ss_map if s == "H"]
    sheet_res = [r for (s, r) in ss_map if s == "E"]
    
    return PDBEmbed(
            pdb_string,
            ribbon= "all",
            helix = "residue %s" % ",".join(str(r) for r in helix_res),
            sheet = "residue %s" % ",".join(str(r) for r in sheet_res))

def setup_display_hooks():
    """Setup display hooks for all currently loaded modules."""
    if "rosetta" in sys.modules:
        import rosetta.core.pose
        rosetta.core.pose.Pose._repr_javascript_ = lambda self: pose_display(self)._repr_javascript_()
