from setuptools import setup

setup(name='ipython_glmol',
    version='0.1.0',
    description='IPython GLmol embedding support.',
    author='Alex Ford',
    author_email='a.sewall.ford@gmail.com',
    packages=['ipython_glmol'],
    package_data={'ipython_glmol' : ["GLmol/src/js/*"]}
    install_requires = [
        "ipython>=1.2.0",
    ]
)
