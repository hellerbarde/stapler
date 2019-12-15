from setuptools import setup, find_packages

version = "1.0.0-rc1"

setup(name="stapler",
    version=version,
    description="Manipulate PDF documents from the command line",
    keywords="pdf utility cli concatenate tool",
    
    author="Philip Stark, Fred Wenzel",
    author_email="git@codechaos.ch",
    url="https://github.com/hellerbarde/stapler",

    install_requires = [
        "PyPDF2>=1.26",
        "more-itertools>=4"
    ],

    include_package_data=True,
    packages=find_packages(),
    package_data={"": ["LICENSE", "CONTRIBUTORS", "README.md", ]},
    entry_points="""
    [console_scripts]
    stapler = staplelib:main
    pdf-stapler = staplelib:main
    """,

    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3",
        "Intended Audience :: Science/Research",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License"
    ],
)
