from setuptools import setup, find_packages

setup(
    name="optimize", # これがパッケージ名になります～
    version="0.0.1",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "matplotlib",
    ],
    author="tanetakumi",
    author_email="nutanetakumi@yahoo.co.jp",
    description="Optimize the circuits containing pi-josephoson",
    url="https://github.com/tanetakumi/",
    python_requires='>=3.8',
)