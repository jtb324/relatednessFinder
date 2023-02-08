[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# relatednessFinder v0.3.0:

## Purpose:
C.L.I tool to help identify estimated relatedness values for the European cohort in BioVU individuals. This tool was main designed to interact with the database on teh below server.

## Cloning the repository from github:
If you wish to use this program first clone the repository using the following command:

```bash
git clone https://github.com/jtb324/relatednessFinder.git
```

Once you have cloned the repository you will need to create a virtual environment to properly install dependencies. It is recommended to use conda to create the virtual environment. There is a environment.yml file in the cloned repository so the following commands will create a virtual environment call "relatednessFinder"

```bash
cd relatednessFinder

conda env create -f environment.yml
```

*Alternatives:*
You could also create a virtual environment using virtualenv or pipenv. There is a requirements.txt file in the cloned directory so you can use the command:

```bash
pip install -r requirements.txt
```

Just make sure that you are using python version >= 3.10. If you are familiar with [poetry](https://python-poetry.org/) you could also use that. There is a pyproject.toml file in the cloned directory so you could use the command.

```bash
poetry install
```

Once you have the environment created you can call the program from the cloned directory using the command:

```bash
python3 relatednessFinder/relatedness_finder.py --help
```

This command should show a help message with all the arguments and the optional arguments