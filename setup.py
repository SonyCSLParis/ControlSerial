from setuptools import setup, find_packages


install_requires = [
    'pyserial',
    'argparse',
    'crc8'
]

tests_require = [
    'pytest>=6.0',
    'pytest-cov>=2.0',
    'coverage>=5.0'
]

extras_require = {
    'test': tests_require,
    'dev': tests_require + ['black', 'flake8', 'mypy']
}


setup(name="ControlSerial",
version="0.0.1",
description="Serial interface Arduino-Python",
author="Peter Hanappe",
author_email="peter@hanappe.com",
packages = find_packages(),
install_requires = install_requires,
tests_require = tests_require,
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