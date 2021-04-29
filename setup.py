import os
from setuptools import setup

PATH = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(PATH, "README.md")) as f:
    README_TEXT = f.read()

AUTHOR = "Conservation Technology Lab at the San Diego Zoo Wildlife Alliance"
DESC = "Code for MiniDencam: Polar bear maternal den observation system."

setup(
    name="dencam",
    version="0.0.2",
    author=AUTHOR,
    description=DESC,
    long_description=README_TEXT,
    long_description_content_type="text/markdown",
    url="https://github.com/icr-ctl/dencam",
    license="MIT",
    packages=['dencam'],
    include_package_data=True,
    install_requires=[
        'pyyaml',
        'rpi.gpio',
        'picamera',
        'netifaces',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    entry_points={"console_scripts": ["dencam=dencam.__main__:main"]},
)
