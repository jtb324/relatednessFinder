from datetime import datetime
import logging
import typer
from pathlib import Path
import itertools
import sqlite3
import log
from enum import Enum

app = typer.Typer(add_completion=False)


class IncorrectGridFileFormat(Exception):
    """Exception that will be thrown if the grid file is not in the right format"""

    def __init__(self, line_num: int, grid_file: str) -> None:
        super().__init__(
            f"There was an error reading in the file: {grid_file} at line {line_num}. Program expected each line to be a separate ID."
        )


class LogLevel(str, Enum):
    """Enum used to define the options for the log level in the cli"""

    WARNING = "warning"
    VERBOSE = "verbose"
    DEBUG = "debug"


def read_in_grids(grid_filepath: Path, logger: logging.Logger) -> list[str]:
    """Function that will read in all of the IDs from the provided file.

    Parameters
    ----------
    grid_filepath : Path
        path to a tab separated text file that list all the grids that the user
        wishes to find values for

    logger : logging.Logger
        logging object

    Returns
    -------
    list[str]
        returns a list of IDs
    """
    logger.debug(f"Reading in grids from the file {grid_filepath}")

    return_list = []

    with open(grid_filepath, "r", encoding="utf-8") as grid_input:
        for line_num, line in enumerate(grid_input):
            if len(line.split("\t")) != 1:
                raise IncorrectGridFileFormat(line_num, grid_filepath)
            if "grid" not in line.lower():
                return_list.append(line.strip())

    return return_list


def determine_combinations(
    id_list: list[str], logger: logging.Logger
) -> dict[str, dict[str, int]]:
    """Function that will construct a dictionary that has all the possible pairs from the grid list.

    Parameters
    ----------
    id_list : list[str]
        list of id string

    logger : logging.Logger
        Logging object

    Returns
    -------
    dict[str, dict[str, int]]
        dictionary where the outer keys are ids and the inner keys are the se cond individual in the pair.
        The inner value is going to be initialized at 0 and will be filled in with the estimated relatedness
        value later on in the program
    """
    logger.debug("Creating the combinations of all pairwise individuals")

    return_dict = {}

    for grid in id_list:
        return_dict.setdefault(
            grid,
            {
                ind: 0
                for ind in id_list
                if ind != grid and ind not in return_dict.keys()
            },
        )

    return return_dict


def construct_query_str(grid_list: list[str]) -> str:
    """Function that will construct the sql string to use in the query

    Parameters
    ----------
    grid_list : list[str]
        list of IDs that will be used in the query

    Returns
    -------
    str
        returns a string to use in the where clause
    """
    start_str = "('"

    start_str += "', '".join(grid_list)

    start_str += "')"

    return start_str


def get_connection(db: str, logger: logging.Logger) -> sqlite3.Connection:
    """Function to connect to the database

    Parameters
    ----------
    db : str
        database name

    logger : logging.Logger
        logging object

    Returns
    -------
    sqlite3.Connection
        returns a connection object or terminates the
        program if an error is encountered
    """

    try:
        logger.info(f"Attempting to connect to the database at {db}")
        conn = sqlite3.connect(db)
    except sqlite3.Error as e:
        logger.fatal(e)
        logger.fatal("Error connecting to database")
        typer.exit(1)

    logger.info(f"Successfully connected to the database at {db}")

    return conn


def get_relatedness(
    query: str,
    connection: sqlite3.Connection,
    combinations: dict[str, dict[str, int]],
    logger: logging.Logger,
) -> dict[str, dict[str, int]]:
    """Function that will execute the query

    Parameters
    ----------
    query : str
        string that contains the sql query to be executed

    connection : sqlite3.Connection
        Connection object

    combinations : dict[str, dict[str, int]]
        dictionary where both inner keys and outer keys are IDs represent individuals in a pair.
        The inner value is the estimated relatedness for the pair. This value will be zero if there
        is no significant relatedness

    logger : logging.Logger
        logging object

    """
    logger.debug("Executing the query")

    cursor = connection.cursor()

    cursor.execute(query)

    rows = cursor.fetchall()

    for row in rows:
        # pull out the pair ids and the estimated relatedness
        pair_1 = row[1]
        pair_2 = row[2]
        estimated_relatedness = row[3]

        if inner_pair := combinations.get(pair_1, 0):
            inner_pair[pair_2] = estimated_relatedness
        else:
            inner_pair = combinations.get(pair_2)
            inner_pair[pair_1] = estimated_relatedness

    return combinations


def write_to_file(
    results: dict[str, dict[str, int]], output_filename: Path, relatedness_thres: int
) -> None:
    """Function that will write the output to a file

    Parameters
    ----------
    combinations : dict[str, dict[str, int]]
        dictionary where both inner keys and outer keys are IDs represent individuals in a pair.
        The inner value is the estimated relatedness for the pair. This value will be zero if there
        is no significant relatedness

    output_filename : Path
        Path to the output file

    combinations : list[tuple[str, str]]
        list of all the possible pairs from the ID list

    relatedness_thres : int
        threashold for the minimum relatedness allowed. Should be between 0-9. Nine will be considered the highest threshold. 0 would remove all of the non related people

    """
    with open(output_filename, "w", encoding="utf-8") as output:
        output.write("ID1\tID2\tEstimated_relatedness\n")
        for pair_1, inner_dict in results.items():
            if inner_dict:
                for pair_2, estimated_rel in inner_dict.items():
                    if estimated_rel >= relatedness_thres:
                        output.write(f"{pair_1}\t{pair_2}\t{estimated_rel}\n")


@app.command()
def main(
    grid_file: Path = typer.Option(
        ...,
        "-g",
        "--grid-file",
        help="Filepath to a text file that has a list of grids. Program expects for there to be one grid for each line of the file.",
    ),
    database_path: Path = typer.Option(
        ...,
        "-d",
        "--database-path",
        help="path to the database that has the relatedness values for each pair.",
    ),
    table_name: str = typer.Option(
        ..., "-t", "--table-name", help="name of the table within the database"
    ),
    output_path: Path = typer.Option(
        ..., "-o", "--output", help="Filepath to write the output to."
    ),
    relatedness_threshold: int = typer.Option(
        0,
        "--rel-threshold",
        help="Relatedness threshold. Pairs with estimated relatedness values higher than this will be removed. 0 is the default and will keep individuals who are not related. Values should be between 0 and 9."
    ),
    loglevel: LogLevel = typer.Option(
        LogLevel.WARNING.value,
        "--loglevel",
        "-l",
        help="This argument sets the logging level for the program. Accepts values 'debug', 'warning', and 'verbose'.",
        case_sensitive=True,
    ),
    log_to_console: bool = typer.Option(
        False,
        "--log-to-console",
        help="Optional flag to log to only a file or also the console",
        is_flag=True,
    ),
    log_filename: str = typer.Option(
        "test.log", "--log-filename", help="Name for the log output file."
    ),
) -> None:
    """Main function to pull the relatedness from the ersa database"""
    # getting the programs start time
    start_time = datetime.now()

    # creating the logger and then configuring it
    logger = log.create_logger()

    log.configure(
        logger,
        "./",
        filename=log_filename,
        loglevel=loglevel,
        to_console=log_to_console,
    )

    # recording all the user inputs
    log.record_inputs(
        logger,
        grid_file_path=grid_file,
        database_path=database_path,
        database_table_path=table_name,
        output_path=output_path,
        loglevel=loglevel,
        log_filename=log_filename,
    )

    logger.info(f"analysis start time: {start_time}")

    grid_list = read_in_grids(grid_file, logger)

    # We are going to generate a dictionary that has all of the possible 
    # pairwise combinations
    combinations = determine_combinations(grid_list, logger)

    logger.info(f"Identified {len(grid_list)} from the input list")
    # Constructing the grid string for all of the individuals in the query so 
    # that we can use that string in the where clause
    grid_str = construct_query_str(grid_list)
    
    # This will be the query string that we execute
    sql_str = (
        "SELECT * FROM "
        + table_name
        + f" WHERE ID1 in {grid_str}"
        + f" AND ID2 in {grid_str};"
    )

    logger.debug(f"String used for SQL Query: \n {sql_str}")

    # getting the database connection
    conn = get_connection(database_path, logger)

    with conn:
        get_relatedness(sql_str, conn, combinations, logger)

    write_to_file(combinations, output_path, relatedness_threshold)

    end_time = datetime.now()

    logger.info(f"analysis end time: {end_time}")

    logger.info(f"Analysis runtime: {end_time - start_time}")


if __name__ == "__main__":
    app()
