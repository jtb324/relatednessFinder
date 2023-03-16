import asyncio
import logging
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Generator

from log import log_msg_debug


@dataclass
class dbResults:
    database_path: Path
    table_name: str
    case_results: list[Any] = field(default_factory=list)
    control_results: list[Any] = field(default_factory=list)


@log_msg_debug("Attempting to connect to the database")
def get_connection(
    db: Path, logger: logging.Logger = logging.getLogger("__main__")
) -> sqlite3.Connection:
    """Function to connect to the database

    Parameters
    ----------
    db : Path
        database name

    logger : logging.Logger
        logging object

    Returns
    -------
    sqlite3.Connection
        returns a connection object or terminates the
        program if an error is encountered

    Raises
    ------
    sqlite3.Error
        If the attempt to connect to the database encounters an error
    """

    logger.info(f"Attempting to connect to the database at {db}")

    conn = sqlite3.connect(db)

    logger.info(f"Successfully connected to the database at {db}")

    return conn


def construct_query_str(
    grid_list: list[str], db_obj: dbResults, all_connections: bool, logger: logging.Logger
) -> str:
    """Function that will construct the sql string to use in the query

    Parameters
    ----------
    grid_list : list[str]
        list of IDs that will be used in the query

    db_obj: dbResults
        object that will have the results for the relatedness for cases and controls
    
    all_connections : bool
        boolean indicating if the user wishes to identify all connections or just those in the grid file. This will differentiate the query between an AND or OR

    logger : logging.Logger
        logger object to keep track of the state of the program

    Returns
    -------
    str
        returns a string to use in the where clause
    """
    grid_str = "('"

    grid_str += "', '".join(grid_list)

    grid_str += "')"

    # This will be the query string that we execute
    if all_connections:
        sql_str = (
            "SELECT * FROM "
            + db_obj.table_name
            + f" WHERE ID1 in {grid_str}"
            + f" OR ID2 in {grid_str};"
        )
    else:
        sql_str = (
            "SELECT * FROM "
            + db_obj.table_name
            + f" WHERE ID1 in {grid_str}"
            + f" AND ID2 in {grid_str};"
        )

    logger.debug(f"String used for SQL Query: \n {sql_str}")

    return sql_str


@log_msg_debug("Executing query to get the relatedness for a list of individuals.")
def get_relatedness(
    ind_list: list[str],
    db_obj: dbResults,
    logger: logging.Logger,
    all_connections: bool = False
) -> Generator[list[tuple[int, str, str, int]], None, None]:
    """Function that will execute the query and return a generator
    object that has so many rows at a time

    Parameters
    ----------

    ind_list : list[str]
        list of individuals to find in the database

    db_obj : dbResults
        object that contains the results from the database in list, as well as the database path and the table name

    all_connections : bool
        boolean indicating if the user wishes to identify all connections or just those in the grid file. This will differentiate the query between an AND or OR

    logger : logging.Logger
        logging object

    Returns
    -------
    Generator[list[tuple[int, str, str, int]], None, None]
        returns a generator of list where the list contains all the information in the database row such as id, id1, id2, and the estimated_relatedness
    """
    # we need to get the database connection
    connection = get_connection(db_obj.database_path, logger=logger)

    # we need to then create the query string
    query = construct_query_str(ind_list, db_obj, all_connections, logger)

    with connection:
        cursor = connection.cursor()

        cursor.execute(query)
        while rows := cursor.fetchmany(size=40):
            yield rows
