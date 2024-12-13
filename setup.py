# setup file to make repository into python package
import os
from distutils.core import setup

from setuptools import PEP420PackageFinder

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "src")


def get_version_info():
    """
    Extract version information as a dictionary from version.py
    """
    version_info = {}
    version_filename = os.path.join("src", "chatdb", "version.py")
    with open(version_filename, "r") as version_module:
        version_code = compile(version_module.read(), "version.py", "exec")
    exec(version_code, version_info)
    return version_info


setup(
    name="chatdb",
    version=get_version_info()["version"],
    package_dir={"": "src"},
    description="Project - interactive chatbot with database querying capabilities",
    author="Vedant Tibrewal & Gleice Chaves",
    packages=PEP420PackageFinder.find(where=str(SRC)),
    entry_points={"console_scripts": ["project=production.entrypoint"]},
)
