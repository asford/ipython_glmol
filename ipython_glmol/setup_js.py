#!/usr/bin/env python
import logging
logger = logging.getLogger("glmol_embed.setup_js")

import os
from os import path
import shutil

import subprocess
import fileinput

import argparse

output_template = """
(function (window, undefined) {

%(source_js)s

window.GLmol = GLmol;

}(window));
"""

source_library_names = ["csscolorparser.js", "three.js", "GLmol.js"]
source_libraries = [path.join(path.dirname(__file__), "GLmol", "src", "js", l) for l in source_library_names]

def render_js(target_files = source_libraries, js_filter=None):
    """docstring for do_setup"""
    logger.info("do_setup(%r)", locals())

    source_js = "".join(l for l in fileinput.FileInput(target_files))

    if js_filter is not None:
        cmd = subprocess.Popen(js_filter, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        source_js, _ = cmd.communicate(source_js)

    return output_template % dict(source_js = source_js)

def install_ipython_js():
    """Render GLmol library and install into ipython profile static include directory.
    
    Resolves current ipython profile directory and writes the rendered library as:
    '<ipython_profile_dir>/static/glmol/GLmol.full.devel.js'.
    
    returns - Script url for use in the notebook."""

    base_path = "static/glmol"
    base_name = "GLmol.full.devel.js"

    from IPython.utils.path import locate_profile
    base_dir = path.join(locate_profile(), base_path)

    if path.exists(base_dir):
        logger.info("Removing existing glmol: %s", base_dir)
        shutil.rmtree(base_dir)

    os.makedirs(base_dir)
    
    output_file = path.join(base_dir, base_name)

    logger.info("Writing glmol: %s", output_file)
    with open(output_file, "w") as o:
        o.write(render_js())
    
    return path.join(base_path, base_name)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")

    parser = argparse.ArgumentParser(description='Setup GLMol javascript.')

    js_filter = parser.add_mutually_exclusive_group()
    js_filter.add_argument('--beautify', "-b", action="store_const", const=["uglifyjs", "-b", "indent-level=4"], dest="js_filter", help='Produce beautified output js.')
    js_filter.add_argument('--compress', "-c", action="store_const", const=["uglifyjs", "-c"], dest="js_filter", help='Produce compressed output js.')

    parser.add_argument('target_files', type=str, nargs="*", default=source_libraries, help="Included files.")
    args = parser.parse_args()

    print render_js(**vars(args))
