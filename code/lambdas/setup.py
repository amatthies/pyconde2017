"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# To use a consistent encoding
from codecs import open
from os import path

# Always prefer setuptools over distutils
from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

# get the dependencies and installs
# with open(path.join(here, 'requirements.txt'), encoding='utf-8') as f:
#    all_reqs = f.read().split('\n')

# install_requires = [x.strip() for x in all_reqs if 'git+' not in x]
# dependency_links = [x.strip().replace('git+', '') for x in all_reqs if x.startswith('git+')]

setup(
    name='lambdas',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version='0.0.1',

    description='AWS Lambda Functions by Babbel Data Engineering',
    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/amatthies/pyconde2017',

    # Author details
    author='Anne Matthies',
    author_email='amatthies@babbel.com',

    # Choose your license
    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS :: MacOS X'

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],

    # What does your project relate to?
    keywords='aws data development',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages('src'),
    package_dir={'': 'src'},

    # Alternatively, if you want to distribute just a my_module.py, uncomment
    # this:
    #   py_modules=["my_module"],

    include_package_data=True,
    zip_safe=False,

    # When changing requires and you have a conda recipe, also update conda.recipe/meta.yaml

    install_requires=[
        'setuptools>=27.2.0',
        'pyaml>=16.12.2',
        'boto3>=1.4.4',
        'cliff>=2.4.0',
        'requests>=2.13.0',
        'tqdm>=4.14.0'
    ],

    entry_points={
        'console_scripts': [
            'lambdas=lambdas.main:main',
        ],
        'lambdas.cli': [
            'lambdas = lambdas.cli:Lambdas',
            'package = lambdas.cli:Package'
        ],
        'klempner.cli': [
            'lambdas_show = lambdas.cli:Lambdas',
            'lambdas_package = lambdas.cli:Package'
        ]
    },
)

