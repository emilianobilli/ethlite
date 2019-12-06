import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ethlite",
    version="0.0.10",
    author="Emiliano A. Billi",
    author_email="emiliano.billi@gmail.com",
    description="A tiny web3/python alternative to interact with any ethereum compatible blockchain",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/emilianobilli/ethlite",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
          'pysha3',
          'requests',
          'six'
    ],
    python_requires='>=3.5',
)