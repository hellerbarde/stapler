from setuptools import setup, find_packages

version = '0.3.0'

setup(name='stapler',
    description="Manipulate PDF documents from the command line",
    classifiers=[
        "Programming Language :: Python :: 2",
        "Topic :: Utilities",
    ],
    keywords='pdf stapler cli',
    version=version,
    license='BSD',
    author='Fred Wenzel, Philip Stark',
    url='https://github.com/hellerbarde/stapler',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'pypdf == 1.12',
    ],
    entry_points="""
    [console_scripts]
    stapler = staplelib:main
    """,
    )

