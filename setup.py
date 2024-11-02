from setuptools import setup, find_packages

setup(
    name="personal-finance-manager",
    version="0.1.0",
    packages=find_packages(exclude=["tests*"]),
    install_requires=[
        "numpy",
        "pandas",
        "matplotlib",
        "sqlalchemy"
    ],
    extras_require={
        "dev": [
            "pytest",
            "pytest-cov",
        ],
    },
    setup_requires=["setuptools>=45.0"],
    entry_points={
        "console_scripts": [
            "finance-manager=finance_manager.main:main",
        ],
    },
    author="MoXeR MMH",
    author_email="lsmmmhytt@gmail.com",
    description="A comprehensive personal finance manager",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/moxer-mmh/Personal-Finance-Manager",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
