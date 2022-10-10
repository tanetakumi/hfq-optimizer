from setuptools import setup, find_packages

setup(
    name="optimize", # これがパッケージ名になります～
    version="0.0.1",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "matplotlib",
        "numpy",
        "scipy",
        "itertools",
        "tqdm"
    ],
    author="tanetakumi",
    description="Optimize the circuits containing pi-josephoson junction",
    url="https://github.com/tanetakumi/",
    python_requires='>=3.8',
)