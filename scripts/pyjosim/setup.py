from setuptools import setup, find_packages

setup(
    name="pyjosim", # これがパッケージ名になります～
    version="0.0.1",
    packages=find_packages(),
    install_requires=[
        "pandas",
    ],
    author="tanetakumi",
    author_email="nutanetakumi@yahoo.co.jp",
    description="simulation from JoSIM result",
    url="https://github.com/tanetakumi/",
    python_requires='>=3.8',
)