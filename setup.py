from setuptools import find_packages, setup


def read_md(file):
    with open(file) as fin:
        return fin.read()


setup(
    name="elaspic-v2-web",
    version="0.1.0",
    description="ELASPIC v2 web server",
    long_description=read_md("README.md"),
    author="Alexey Strokach",
    author_email="alex.strokach@utoronto.ca",
    url="https://gitlab.com/ostrokach/elaspic-v2-web",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    package_data={},
    include_package_data=True,
    zip_safe=False,
    keywords="ev2web",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    test_suite="tests",
)