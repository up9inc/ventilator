from setuptools import setup
from os import path

__location__ = path.abspath(path.dirname(__file__))


def read_requirements():
    """parses requirements from requirements.txt"""
    reqs_path = path.join(__location__, 'requirements.txt')
    with open(reqs_path, encoding='utf8') as f:
        reqs = [line.strip() for line in f if not line.strip().startswith('#')]

    names = []
    for req in reqs:
        names.append(req)
    return {'install_requires': names}


setup(
    name="ventilator",
    version="0.0.0",

    author="UP9INC",
    author_email="support@up9.com",
    license="MIT",
    description="Create Test Virtual Environments from existing environments",
    url='https://github.com/up9inc/ventilator',
    keywords=['TEST', 'MOCKS', 'ENVIRONMENT'],
    packages=["ventilator"],
    classifiers=[
        'Intended Audience :: Developers',
        'Topic :: Internet :: WWW/HTTP :: HTTP Servers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3 :: Only',
    ],
    **read_requirements(),
    package_data={
        'ventilator': ['configurator/*']
    },
    entry_points={
        'console_scripts': [
            'ventilator=ventilator:initiate',
        ],
    },
    python_requires=">=3.6"
)
