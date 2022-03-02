from setuptools import setup

setup(
    name="fguard",
    version="0.1",
    py_modules=["fguard"],
    install_requires=["Click", "jinja2"],
    entry_points="""
        [console_scripts]
        fguard=fguard.cli:cli
    """,
)
