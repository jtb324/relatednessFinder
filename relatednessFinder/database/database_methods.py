import asyncio
import logging
from pathlib import Path
import sqlite3
from dataclasses import dataclass

import aiosqlite
from log import log_msg_debug


@dataclass
class dbResults:
    database_path: Path
    table_name: str
    case_results: list[tuple[int, str, str, int]] | None = None
    control_results: list[tuple[int, str, str, int]] | None = None


@log_msg_debug("Attempting to connect to the database")
async def get_connection(
    db: Path, logger: logging.Logger = logging.getLogger("__main__")
) -> sqlite3.Connection:
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

    conn = await aiosqlite.connect(db)

    logger.info(f"Successfully connected to the database at {db}")

    return conn


def construct_query_str(
    grid_list: list[str], db_obj: dbResults, logger: logging.Logger
) -> str:
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
    grid_str = "('"

    grid_str += "', '".join(grid_list)

    grid_str += "')"

    # This will be the query string that we execute
    sql_str = (
        "SELECT * FROM "
        + db_obj.table_name
        + f" WHERE ID1 in {grid_str}"
        + f" AND ID2 in {grid_str};"
    )

    logger.debug(f"String used for SQL Query: \n {sql_str}")

    return sql_str


@log_msg_debug("Executing query to get the relatedness for a list of individuals.")
async def get_relatedness(
    ind_list: list[str],
    connection: sqlite3.Connection,
    db_result_obj: dbResults,
    case_or_control: str,
    logger: logging.Logger,
) -> None:
    """Function that will execute the query

    Parameters
    ----------
    ind_list : list[str]
        list of individuals to find in the database

    connection : sqlite3.Connection
        database connection object to get the cursor from

    db_result_obj: dbResults
        class that will have results from the database

    case_or_control : str
        string telling whether we are finding a status for cases or controls

    logger : logging.Logger
        logging object

    """


    # we need to then create the query string
    query = construct_query_str(ind_list, db_result_obj, logger)

   
    cursor = await connection.cursor()

    await cursor.execute(query)

    rows = await cursor.fetchall()

    if case_or_control == "case":
        db_result_obj.case_results = rows
    else:
        db_result_obj.control_results = rows

    logger.debug(f"Returning {len(rows)} results from the database")


async def perform_db_operation(
    db_obj: dbResults,
    logger: logging.Logger,
    case_list: list[str],
    control_list: list[str] | None = None,
) -> None:
    """Async Function that will be responsible for calling the async coroutine
    get_relatedness to make the database query

    Parameters
    ----------

    db_obj: dbResults
        class that will have results from the database

    logger : logging.Logger
        logging object

    case_list : list[str]
        list of IDs for cases

    control_list : list[str]
        list of IDs for controls
    """

    # we need to get the database connection
    connection = await get_connection(db_obj.database_path, logger=logger)


    if control_list:
        await asyncio.gather(
            get_relatedness(case_list, connection, db_obj, "case", logger=logger),
            get_relatedness(control_list, connection, db_obj, "control", logger=logger),
        )
    else:
        await asyncio.gather(get_relatedness(case_list, connection, db_obj, "case", logger=logger))
    
    await connection.close()
    
