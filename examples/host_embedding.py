import sys
import urllib2

sys.path.append("..")
import ipython_glmol


pdb_lines = urllib2.urlopen("http://www.rcsb.org/pdb/files/1sfc.pdb").readlines()
pdb_lines = [l.strip() for l in pdb_lines if l.startswith("ATOM")]

full_embed = full_embed = ipython_glmol.PDBEmbed("\n".join(pdb_lines + [""]))
full_embed.repr_entries["sphere"].append("all; bb")
full_embed.repr_entries["line"].append("all")

test_embed = ipython_glmol.PDBEmbed(ipython_glmol.test_pdb_data, **ipython_glmol.test_repr_data)

with open("test_embed.html", "w") as e:
    e.write(test_embed.dump_html())
    
with open("full_embed.html", "w") as e:
    e.write(full_embed.dump_html())

import SimpleHTTPServer
SimpleHTTPServer.test()
