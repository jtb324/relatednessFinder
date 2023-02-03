import logging
import sqlite3
import typer

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

    Raises
    ------
    sqlite3.Error
        If the attempt to connect to the database encounters an error
    """

    try:
        logger.info(f"Attempting to connect to the database at {db}")
        conn = sqlite3.connect(db)
    except sqlite3.Error as e:
        logger.fatal(e)
        logger.fatal("Error connecting to database")
        raise sqlite3.Error(f"Error while trying to get the initial connection to the database at: {db}")

    logger.info(f"Successfully connected to the database at {db}")

    return conn