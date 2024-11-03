from setuptools import setup, find_packages


# Function to read the requirements.txt file
def read_requirements():
    with open("requirements.txt") as f:
        return f.read().splitlines()


# Function to read the README.md file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as f:
        return f.read()


setup(
    name="tree-ring-analyzer",
    version="0.3.0",
    description="A package for tree ring detection in images",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/tuke307/tree-disk-analyzer",
    author="Tony Meissner",
    author_email="tonymeissner70@gmail.com",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "tree-ring-analyzer=treeringanalyzer.cli:main",
        ],
    },
    python_requires=">=3.7",
    include_package_data=True,  # This tells setuptools to read MANIFEST.in
)
