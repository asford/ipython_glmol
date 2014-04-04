from collections import defaultdict, Iterable

from IPython.display import Javascript
import uuid

from .setup_js import install_ipython_js, render_js
import json

glmol_source_library = install_ipython_js()

_repr_textarea_template = """
<textarea  wrap='off' id='%(embed_id)s_rep' style='display:none;'>
%(repr_string)s
</textarea>
"""

_pdb_textarea_template = """
<textarea  wrap='off' id='%(embed_id)s_src' style='display:none;'>
%(pdb_string)s
</textarea>
"""

_dump_html_template = """
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

_data_js_template = """
    var pdb_textarea_json = %(pdb_textarea_json)s;
    element.append(pdb_textarea_json);

    var repr_textarea_json = %(repr_textarea_json)s;
    element.append(repr_textarea_json);
"""

_display_js_template = """
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

        $.data(element.children()[0], "glmol", %(embed_id)s);
        document.getElementById("%(embed_id)s").scrollIntoViewIfNeeded();
        
        """
    
class PDBEmbed(object):
    """Embeds pdb and repr as GLmol canvas."""

    def __init__(self, pdb_string, **repr_entries):
        """Init from given pdb and repr."""
        self.pdb_string = pdb_string
        self.repr_entries = defaultdict(list)

        if repr_entries:
            for repr_type, selection in repr_entries.items():
                self.add_repr_entry(repr_type, selection)

    def __add__(self, modifier):
        ## TODO should implement correct shallow-copy semantics for embed object to suppoort
        # immutable add
        if isinstance(modifier, EmbedReprModifier):
            modifier.apply_to_embed(self)
        elif isinstance(modifier, Iterable):
            for m in modifier:
                m.apply_to_embed(self)
        else:
            raise ValueError("Invalid PDBEmbed modifier: %s", modifier)
        
        return self

    def __iadd__(self, modifier):
        return self.__add__(modifier)

    def add_repr_entry(self, repr_type, selection):
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

    def _repr_javascript_(self):
        """docstring for _repr_javascript"""

        embed_id = self.generate_id()

        pdb_textarea_json = json.dumps(
                _pdb_textarea_template % dict(embed_id = embed_id, pdb_string = self.pdb_string))

        repr_textarea_json = json.dumps(
                _repr_textarea_template % dict(embed_id = embed_id, repr_string = self.repr_string))

        display_js = \
            _data_js_template % dict(
                embed_id = embed_id,
                pdb_textarea_json = pdb_textarea_json,
                repr_textarea_json = repr_textarea_json) + \
            _display_js_template % dict(embed_id = embed_id)


        return Javascript(display_js, lib = glmol_source_library)._repr_javascript_()

    def dump_html(self):
        """Create minimal html page for the given representation."""

        embed_id = "glmol"

        pdb_textarea_json = json.dumps(
                _pdb_textarea_template % dict(embed_id = embed_id, pdb_string = self.pdb_string))

        repr_textarea_json = json.dumps(
                _repr_textarea_template % dict(embed_id = embed_id, repr_string = self.repr_string))

        embed_js = \
            _data_js_template % dict(
                embed_id = embed_id,
                pdb_textarea_json = pdb_textarea_json,
                repr_textarea_json = repr_textarea_json) + \
            _display_js_template % dict(embed_id = embed_id)

        glmol_library = render_js()
    
        return _dump_html_template % dict(
                embed_js = embed_js,
                glmol_library=glmol_library)
    
class EmbedReprModifier(object):
    def __add__(self, modifier):
        assert isinstance(modifier, EmbedReprModifier)
        return CompositeReprModifier([self, modifier])

class CompositeReprModifier(EmbedReprModifier):
    def __init__(self, modifiers = []):
        self.modifiers = modifiers

    def apply_to_embed(self, embed):
        for m in self.modifiers:
            m.apply_to_embed(embed)

    def __add__(self, modifier):
        assert isinstance(modifier, EmbedReprModifier)

        if isinstance(modifier, CompositeReprModifier):
            return CompositeReprModifier(self.modifiers + modifier.modifiers)
        else:
            return CompositeReprModifier(self.modifiers + [modifier])
