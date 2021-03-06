import setuptools


setuptools.setup(
    name="dencam",
    author="Conservation Technology Lab at the San Diego Zoo Wildlife Alliance",
    description="Code for MiniDencam: Polar bear maternal den observation system.",
    packages=setuptools.find_packages(),
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
)
