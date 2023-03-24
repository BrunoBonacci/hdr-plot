import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="hdr-plot",
    version="0.6.0",
    author="Bruno Bonacci",
    author_email="bonacci.bruno@gmail.com",
    description="A simple HdrHistogram plotting script.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/BrunoBonacci/hdr-plot",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent"
    ),
    install_requires=[
        'matplotlib',
        'pandas'
    ],
    scripts=['bin/hdr-plot'],

)
