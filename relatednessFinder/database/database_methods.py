import logging
from pathlib import Path
import sqlite3
from log import log_msg_debug

@log_msg_debug("Attempting to connect to the database")
def get_connection(db: str, logger: logging.Logger = logging.getLogger("__main__")) -> sqlite3.Connection:
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

    Raises
    ------
    sqlite3.Error
        If the attempt to connect to the database encounters an error
    """

    logger.info(f"Attempting to connect to the database at {db}")
    conn = sqlite3.connect(db)
    
    logger.info(f"Successfully connected to the database at {db}")

    return conn

@log_msg_debug("Executing query to get the relatedness for a list of individuals.")
def get_relatedness(
    query: str,
    connection: sqlite3.Connection,
    logger: logging.Logger,
) -> list[tuple[int, str, str, int]]:
    """Function that will execute the query

    Parameters
    ----------
    query : str
        string that contains the sql query to be executed

    connection : sqlite3.Connection
        Connection object

    logger : logging.Logger
        logging object

    """

    cursor = connection.cursor()

    cursor.execute(query)

    rows = cursor.fetchall()

    logger.debug(f"Returning {len(rows)} results from the database")

    return rows
