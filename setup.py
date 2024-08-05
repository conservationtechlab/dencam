import os
import re

import setuptools


def read(filename):
    path = os.path.join(os.path.abspath(os.path.dirname(__file__)), filename)
    with open(path , 'r') as f:
        return f.read()
    

def find_version(text):
    match = re.search(r"^__version__\s*=\s*['\"](.*)['\"]\s*$", text,
                      re.MULTILINE)
    return match.group(1)
    
    
AUTHOR = "Conservation Technology Lab at the San Diego Zoo Wildlife Alliance"
DESC = "Code for MiniDencam: Polar bear maternal den observation system."

setuptools.setup(
    name="dencam",
    version=find_version(read('dencam/__init__.py')),
    author=AUTHOR,
    description=DESC,
    long_description=read('README.md'),
    long_description_content_type="text/markdown",
    url="https://github.com/icr-ctl/dencam",
    license="MIT",
    packages=['dencam'],
    include_package_data=True,
    install_requires=[
        'minimalmodbus==2.0.1',
        'netifaces',
        'picamera',
        'pyserial',
        'pyyaml',
        'rpi.gpio'
    ],
    extras_require={
        'all': ['numpy',
                'opencv-python',
                'pillow',
                'scipy',
                'screeninfo']
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Operating System :: POSIX :: Linux',
        'Topic :: Scientific/Engineering',
    ],
    entry_points={"console_scripts": ["dencam=dencam.__main__:main"]},
)
