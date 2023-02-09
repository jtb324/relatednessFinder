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

## Inputs for both commands:

The next sections will break down the commands for the relatednessFinder program. 

###*determine-relatedness*
This command is used to determine the relatedness between individuals in a list. It will return a text file where each row is a pair with the estimated relatedness between teh pair. You can see the arguments for this command by running:

```bash
python3 relatedness_finder.py determine-relatedness --help
```

**Required Inputs:**
* *grid file* - This is represented by either the -g or --grid-file flag. The argument is the filepath to a tab separated text file that has two columns. The first column should be the grid ids and the second column should be the phenotype status. For this command you can just label all of the ids as having a phenotype status of 1 because we are not comparing ratios between the cases and controls. The following table shows an example of how the file should look. I've added a header line for display but the grid file input should not have a header line

| GRID ID | PHENOTYPE STATUS |
|:--------|:----------------:|
|Patient 1|       1          |
|Patient 2|       1          |

* *database_path* - This argument is represented by either the -d or --database-path flag. This is the filepath to the database on the server.

* *table_name* - This argument is represented by either the -t or --table-name flag. This will be the table name within the database. You can find this output by running the following commands

```bash
sqlite3 {path to database}

sqlite>.table
```

* *output_path* - This argument is represented by either the -o or --output flags. This is ust the path to write the output to. This should be a full filepath that ends in .txt. By default the program writes to ./test.txt

**Optional Inputs:**
* *loglevel* - This optional argument is represented by the --loglevel flag. This flag allows the user to set the log level as 'warning', 'verbose', or 'debug'. This levels go from the least informative to the most informative, respectively. Warning will only provide information about what parameters were passed to the program while debug will write more information about the whole process.

* *log_to_console* - This flag is represented by --log-to-console. If the user provides this flag then output will be passed to the console through stdout. If not then the output will only be written to a log file.

* *log filename* - This optional argument is represented by the --log-filename flag. This flag allows the user to craete a custom filename for the output log file. By default the program writes log output to test_determine_relatedness.log.

An example of these commands is:

```bash
python3 relatedness_finder.py determine-relatedness -g {gene_file} -d {database_path} -t {table_name} --output {output_path} --log-filename {log filename} --loglevel verbose --log-to-console
```