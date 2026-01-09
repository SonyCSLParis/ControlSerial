from setuptools import setup, find_packages
from pathlib import Path


def parse_requirements(filename):
    """Load requirements from a pip requirements file."""
    lineiter = (line.strip() for line in Path(filename).read_text().splitlines())
    return [line for line in lineiter if line and not line.startswith("#") and not line.startswith("-r")]


install_requires = parse_requirements('requirements.txt')
dev_requires = parse_requirements('requirements-dev.txt')

extras_require = {
    'dev': dev_requires,
}


setup(name="ControlSerial",
version="0.0.1",
description="Serial interface Arduino-Python",
author="Peter Hanappe",
author_email="peter@hanappe.com",
packages = find_packages(),
install_requires = install_requires,
extras_require = extras_require,
license="GPLv3",
python_requires='>=3.6',
classifiers=[
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
    'Topic :: Scientific/Engineering',
    'Topic :: System :: Hardware',
],
keywords='serial arduino communication hardware control',
)