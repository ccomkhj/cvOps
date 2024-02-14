"""
Huijo Kim (huijo@hexafarms.com)
"""

from setuptools import setup, find_packages

# Read the dependencies from requirements.txt
with open("requirements/requirements.txt", encoding="utf-8") as f:
    install_requires = [line.strip() for line in f if line.strip()]

# additional run for pip install -r git-requirements.txt

setup(
    name='cvops',
    version='0.1.0',
    packages=find_packages(),
    install_requires=install_requires,
    author='Huijo Kim',
    author_email='huijo@hexafarms.com',
    description='Supporting tool for computer vision tasks',
    long_description=open('readme.MD').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/ccomkhj/cvops'
)
