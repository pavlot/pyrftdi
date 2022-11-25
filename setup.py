import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyRFTdi",
    version="0.0.1",
    author="Pavlo Taranov",
    author_email="taranov.pavel@gmail.com",
    description="Python library for RFMx modules to be controlled with FTDI chip",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    project_urls={
        "Bug Tracker": "",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
#    entry_points={
#        "console_scripts": [
#            "intesko_dryer_controller_service = intesko_dryer_controller.intesko_dryer_controller_service:main",
#            "intesko_dryer_controller_cli = intesko_dryer_controller.intesko_dryer_controller_cli:main",
#        ]
#    },
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    install_requires=[
        "pyFtdi",
    ],
)
