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

@log_msg_debug("Initializing parallel reading from the database")
def parallel_reader(db_path: Path, logger: logging.Logger) -> None:
    """Function that will read from the database using multiple streams to try to 
    speed up the process.
    
    Parameters
    ----------
    db_path : Path
        
    """