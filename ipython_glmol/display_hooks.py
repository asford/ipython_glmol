import sys
from .glmol_embed import PDBEmbed

def pose_display(pose):
    """Setup embed display for rosetta.core.pose object with sensible default representation."""
    import re
    import cStringIO as StringIO
    from rosetta.utility import ostream
    import rosetta.core.scoring.dssp
    
    sio = StringIO.StringIO()
    pose.dump_pdb(ostream(sio))
    pdb_string = sio.getvalue()
    
    # Missing pose secondary structure assignment
    if not re.search("[^L]", pose.secstruct()):
        dssp = rosetta.core.scoring.dssp.Dssp(pose)
        dssp.insert_ss_into_pose(pose)
    
    ss_map = [(pose.secstruct(i), pose.pdb_info().number(i)) for i in xrange(1, pose.n_residue() + 1)]
    helix_res = [r for (s, r) in ss_map if s == "H"]
    sheet_res = [r for (s, r) in ss_map if s == "E"]
    
    repr_lines = []
    repr_lines.append("ribbon: residue %s-%s" % (pose.pdb_info().number(1), pose.pdb_info().number(pose.n_residue())))
    repr_lines.append("line: residue %s-%s" % (pose.pdb_info().number(1), pose.pdb_info().number(pose.n_residue())))

    if helix_res:
        repr_lines.append("helix: residue %s" % ",".join(str(r) for r in helix_res))
    if sheet_res:
        repr_lines.append("sheet: residue %s" % ",".join(str(r) for r in sheet_res))
    
    return PDBEmbed(pdb_string, "\n".join(repr_lines))


def setup_display_hooks():
    """Setup display hooks for all currently loaded modules."""
    if "rosetta" in sys.modules:
        import rosetta.core.pose
        rosetta.core.pose.Pose._repr_javascript_ = lambda self: pose_display(self)._repr_javascript_()
