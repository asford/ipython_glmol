from collections import defaultdict

from IPython.display import Javascript
import uuid

from .setup_js import install_ipython_js, render_js
import json

glmol_source_library = install_ipython_js()

class PDBEmbed(object):
    """Embeds pdb and repr as GLmol canvas."""

    def __init__(self, pdb_string, **repr_entries):
        """Init from given pdb and repr."""
        self.pdb_string = pdb_string
        self.repr_entries = defaultdict(list)

        if repr_entries:
            for repr_type, selection in repr_entries.items():
                if isinstance(selection, basestring):
                    self.repr_entries[repr_type].append(selection)
                elif selection:
                    self.repr_entries[repr_type].extend(selection)

    @property
    def repr_string(self):
        repr_lines = ["%s:%s" % (repr_type, selection) for repr_type in self.repr_entries for selection in self.repr_entries[repr_type]]
        return "\n".join(repr_lines)

    def generate_id(self):
        return "glmol_%i" % uuid.uuid4()

    pdb_textarea_template = """
<textarea  wrap='off' id='%(embed_id)s_src' style='display:none;'>
%(pdb_string)s
</textarea>
        """
    
    repr_textarea_template = """
<textarea  wrap='off' id='%(embed_id)s_rep' style='display:none;'>
%(repr_string)s
</textarea>
        """
    
    data_js_template = """
        var pdb_textarea_json = %(pdb_textarea_json)s;
        element.append(pdb_textarea_json);

        var repr_textarea_json = %(repr_textarea_json)s;
        element.append(repr_textarea_json);
    """

    display_js_template = """
        element.append('<div id="%(embed_id)s" style="width: auto; height:8in"></div>');

        console.log("Created elements.");
        container.show();

        var %(embed_id)s = new GLmol('%(embed_id)s', true);

        console.log("Loaded GLmol as id: %(embed_id)s.");

        function parseAndDefineRepresentation()
          {
              var all = this.getAllAtoms(),
                  hetatm = this.getHetatms(all).filter(this.isNotSolvent);

              this.colorByChain(all, true);
              this.colorByAtom(this.atoms.filter(this.propertyIsnt("elem", "C")), {});

              this.parseRep(this.modelGroup, $('#%(embed_id)s_rep').val());

              this.drawAtomsAsSphere(this.modelGroup, hetatm, this.sphereRadius);
          }

        %(embed_id)s.rebuildScene = function (repressDraw)
          {
              var time = new Date();

              this.initializeScene();
              this.defineRepresentation();

              console.log("Built scene in " + (new Date() - time) + "ms");
              
              if (repressDraw)
              {
                return;
              }
              else
              {
                this.show();
              }
          };

        %(embed_id)s.defineRepresentation = parseAndDefineRepresentation;
        %(embed_id)s.loadMolecule(true);

        $.data(element.children()[0], "glmol", %(embed_id)s)
        """

    def _repr_javascript_(self):
        """docstring for _repr_javascript"""

        embed_id = self.generate_id()

        pdb_textarea_json = json.dumps(
                self.pdb_textarea_template % dict(embed_id = embed_id, pdb_string = self.pdb_string))

        repr_textarea_json = json.dumps(
                self.repr_textarea_template % dict(embed_id = embed_id, repr_string = self.repr_string))

        display_js = \
            self.data_js_template % dict(
                embed_id = embed_id,
                pdb_textarea_json = pdb_textarea_json,
                repr_textarea_json = repr_textarea_json) + \
            self.display_js_template % dict(embed_id = embed_id)


        return Javascript(display_js, lib = glmol_source_library)._repr_javascript_()

    dump_html_template = """
    <!doctype html>
    <title></title>
    <body>

    <script src="http://code.jquery.com/jquery-1.7.2.min.js" type="text/javascript"></script>
    <script>
    %(glmol_library)s
    </script>

    <div id="element"></div>


    <script>
// Setup element and container equiv. to that provided in ipython notebook.
var element = $("#element")
var container = element

    %(embed_js)s
    </script>

    </body>
    """
    def dump_html(self):
        """Create minimal html page for the given representation."""

        embed_id = "glmol"

        pdb_textarea_json = json.dumps(
                self.pdb_textarea_template % dict(embed_id = embed_id, pdb_string = self.pdb_string))

        repr_textarea_json = json.dumps(
                self.repr_textarea_template % dict(embed_id = embed_id, repr_string = self.repr_string))

        embed_js = \
            self.data_js_template % dict(
                embed_id = embed_id,
                pdb_textarea_json = pdb_textarea_json,
                repr_textarea_json = repr_textarea_json) + \
            self.display_js_template % dict(embed_id = embed_id)

        glmol_library = render_js()
    
        return self.dump_html_template % dict(
                embed_js = embed_js,
                glmol_library=glmol_library)

test_repr_data = dict( helix = "atom 53-82", ribbon = "all", line = "all; heavy", bgcolor = "000000" )

test_pdb_data = """
ATOM      1  N   GLY A   2      35.259  38.537  16.817  1.00 30.55           N  
ATOM      2  CA  GLY A   2      35.919  39.084  15.596  1.00 30.30           C  
ATOM      3  C   GLY A   2      36.635  40.408  15.809  1.00 29.96           C  
ATOM      4  O   GLY A   2      37.109  41.023  14.854  1.00 30.60           O  
ATOM      5  N   LYS A   3      36.742  40.840  17.065  1.00 29.25           N  
ATOM      6  CA  LYS A   3      37.296  42.161  17.377  1.00 27.98           C  
ATOM      7  C   LYS A   3      38.767  42.155  17.787  1.00 27.26           C  
ATOM      8  O   LYS A   3      39.188  41.380  18.634  1.00 27.48           O  
ATOM      9  CB  LYS A   3      36.463  42.862  18.455  1.00 28.09           C  
ATOM     10  CG  LYS A   3      35.019  43.161  18.059  1.00 27.40           C  
ATOM     11  CD  LYS A   3      34.938  44.234  16.985  1.00 26.55           C  
ATOM     12  CE  LYS A   3      33.497  44.539  16.635  1.00 26.73           C  
ATOM     13  NZ  LYS A   3      33.331  45.206  15.307  1.00 25.20           N1+
ATOM     14  N   SER A   4      39.531  43.047  17.168  1.00 26.05           N  
ATOM     15  CA  SER A   4      40.904  43.292  17.537  1.00 24.61           C  
ATOM     16  C   SER A   4      41.020  44.777  17.878  1.00 23.52           C  
ATOM     17  O   SER A   4      41.208  45.603  16.987  1.00 23.44           O  
ATOM     18  CB  SER A   4      41.813  42.951  16.363  1.00 25.06           C  
ATOM     19  OG  SER A   4      43.164  43.074  16.751  1.00 26.61           O  
ATOM     20  N   TYR A   5      40.893  45.114  19.158  1.00 21.44           N  
ATOM     21  CA  TYR A   5      40.828  46.518  19.558  1.00 19.95           C  
ATOM     22  C   TYR A   5      42.193  47.198  19.470  1.00 19.91           C  
ATOM     23  O   TYR A   5      43.211  46.583  19.791  1.00 19.79           O  
ATOM     24  CB  TYR A   5      40.237  46.658  20.962  1.00 19.68           C  
ATOM     25  CG  TYR A   5      38.865  46.038  21.085  1.00 17.78           C  
ATOM     26  CD1 TYR A   5      37.752  46.642  20.496  1.00 15.68           C  
ATOM     27  CD2 TYR A   5      38.683  44.841  21.766  1.00 18.08           C  
ATOM     28  CE1 TYR A   5      36.491  46.079  20.607  1.00 15.31           C  
ATOM     29  CE2 TYR A   5      37.419  44.271  21.890  1.00 17.22           C  
ATOM     30  CZ  TYR A   5      36.330  44.888  21.290  1.00 16.52           C  
ATOM     31  OH  TYR A   5      35.083  44.326  21.398  1.00 16.14           O  
ATOM     32  N   PRO A   6      42.213  48.468  19.028  1.00 19.29           N  
ATOM     33  CA  PRO A   6      43.488  49.160  18.877  1.00 19.32           C  
ATOM     34  C   PRO A   6      44.110  49.530  20.228  1.00 19.13           C  
ATOM     35  O   PRO A   6      43.416  49.656  21.239  1.00 18.92           O  
ATOM     36  CB  PRO A   6      43.108  50.418  18.093  1.00 19.35           C  
ATOM     37  CG  PRO A   6      41.692  50.689  18.500  1.00 19.66           C  
ATOM     38  CD  PRO A   6      41.069  49.326  18.655  1.00 19.47           C  
ATOM     39  N   THR A   7      45.424  49.685  20.235  1.00 18.83           N  
ATOM     40  CA  THR A   7      46.113  50.224  21.386  1.00 18.73           C  
ATOM     41  C   THR A   7      45.872  51.735  21.418  1.00 17.61           C  
ATOM     42  O   THR A   7      45.934  52.414  20.370  1.00 17.00           O  
ATOM     43  CB  THR A   7      47.626  49.935  21.301  1.00 19.15           C  
ATOM     45  CG2 THR A   7      48.384  50.593  22.455  1.00 20.23           C  
ATOM     44  OG1 THR A   7      47.834  48.518  21.343  1.00 21.36           O  
ATOM     46  N   VAL A   8      45.550  52.235  22.609  1.00 15.80           N  
ATOM     47  CA  VAL A   8      45.543  53.671  22.884  1.00 15.09           C  
ATOM     48  C   VAL A   8      46.491  53.965  24.052  1.00 14.95           C  
ATOM     49  O   VAL A   8      46.751  53.088  24.899  1.00 15.53           O  
ATOM     50  CB  VAL A   8      44.122  54.226  23.147  1.00 14.98           C  
ATOM     51  CG1 VAL A   8      43.197  53.984  21.923  1.00 13.64           C  
ATOM     52  CG2 VAL A   8      43.525  53.630  24.427  1.00 13.52           C  
ATOM     53  N   SER A   9      46.996  55.196  24.112  1.00 14.69           N  
ATOM     54  CA  SER A   9      47.986  55.563  25.128  1.00 14.04           C  
ATOM     55  C   SER A   9      47.352  55.522  26.518  1.00 14.18           C  
ATOM     56  O   SER A   9      46.121  55.561  26.650  1.00 12.84           O  
ATOM     57  CB  SER A   9      48.511  56.972  24.867  1.00 14.01           C  
ATOM     58  OG  SER A   9      47.491  57.926  25.137  1.00 12.47           O  
ATOM     59  N   ALA A  10      48.200  55.475  27.543  1.00 14.43           N  
ATOM     60  CA  ALA A  10      47.739  55.572  28.926  1.00 14.82           C  
ATOM     61  C   ALA A  10      46.946  56.870  29.150  1.00 14.87           C  
ATOM     62  O   ALA A  10      45.911  56.858  29.835  1.00 14.80           O  
ATOM     63  CB  ALA A  10      48.931  55.498  29.884  1.00 15.41           C  
ATOM     64  N   ASP A  11      47.410  57.974  28.557  1.00 14.36           N  
ATOM     65  CA  ASP A  11      46.715  59.257  28.691  1.00 13.84           C  
ATOM     66  C   ASP A  11      45.322  59.168  28.091  1.00 12.60           C  
ATOM     67  O   ASP A  11      44.361  59.705  28.649  1.00 12.55           O  
ATOM     68  CB  ASP A  11      47.516  60.410  28.076  1.00 14.56           C  
ATOM     69  CG  ASP A  11      48.697  60.834  28.951  1.00 16.38           C  
ATOM     70  OD1 ASP A  11      48.722  60.505  30.159  1.00 20.25           O  
ATOM     71  OD2 ASP A  11      49.604  61.505  28.432  1.00 19.43           O1-
ATOM     72  N   TYR A  12      45.204  58.468  26.960  1.00 11.65           N  
ATOM     73  CA  TYR A  12      43.878  58.268  26.352  1.00 10.62           C  
ATOM     74  C   TYR A  12      42.953  57.501  27.321  1.00 11.06           C  
ATOM     75  O   TYR A  12      41.804  57.912  27.562  1.00  9.92           O  
ATOM     76  CB  TYR A  12      43.986  57.535  25.012  1.00 10.68           C  
ATOM     77  CG  TYR A  12      42.756  57.699  24.138  1.00 10.46           C  
ATOM     78  CD1 TYR A  12      41.569  57.009  24.421  1.00 11.80           C  
ATOM     79  CD2 TYR A  12      42.778  58.546  23.023  1.00 10.97           C  
ATOM     80  CE1 TYR A  12      40.431  57.161  23.614  1.00 10.47           C  
ATOM     81  CE2 TYR A  12      41.654  58.707  22.214  1.00 10.55           C  
ATOM     82  CZ  TYR A  12      40.485  58.015  22.504  1.00 10.71           C  
END
"""
