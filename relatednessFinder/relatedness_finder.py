import asyncio
from datetime import datetime
import typer
from pathlib import Path
import log

import utilities
import database


app = typer.Typer(add_completion=False)

@app.command()
def determine_relatedness(
    grid_file: Path = typer.Option(
        ...,
        "-g",
        "--grid-file",
        help="Filepath to a tab separated text file that has a list of grids. Program expects for there to be two columns: grid and phenotype. Phenotype should have 1 for cases or 0 for controls. If you do not need to differientiate between cases and controls then just label all individuals as either 0 or 1. The file should not have a header",
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
        Path("./test.txt"), "-o", "--output", help="Filepath to write the output to."
    ),
    relatedness_threshold: int = typer.Option(
        0,
        "--rel-threshold",
        help="Relatedness threshold. Pairs with estimated relatedness values higher than this will be removed. 0 is the default and will keep individuals who are not related. Values should be between 0 and 9.",
    ),
    loglevel: utilities.LogLevel = typer.Option(
        utilities.LogLevel.WARNING.value,
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
        "test_determine_relatedness.log", "--log-filename", help="Name for the log output file."
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

    # We need to read in the grids. This function return a list of cases and controls. We 
    # only need the cases in this situation so we are ignoring the second return 
    grid_list = utilities.read_in_grids(grid_file, logger=logger)

    logger.info(f"Identified {len(grid_list)} IDs from the input list")
    # Constructing the grid string for all of the individuals in the query so

    database_obj = database.dbResults(database_path, table_name)

    asyncio.run(database.perform_db_operation(database_obj, logger, grid_list))

    logger.debug(database_obj)

    utilities.write_to_file(database_obj, output_path, relatedness_threshold)

    end_time = datetime.now()

    logger.info(f"analysis end time: {end_time}")

    logger.info(f"Analysis runtime: {end_time - start_time}")

####### From here on the fucntions will be used to 

@app.command(
    help="Determine the distribution of relatedness within the cases and controls"
)
def gather_distributions(
    case_control_file: Path = typer.Argument(
        ...,
        help="File that has cases and controls. Expects the first column to be IDs and the second column to be phenotype status of 0/1 where 1 indicates a case and 0 indicates controls",
    ),
    output: Path = typer.Argument(
        ...,
        help="Output for all output files. This should be a directory and then the file name without an extension",
    ),
    database_path: Path = typer.Argument(
        ...,
        help="Filepath to the sqlite database that has all the information about pairwise relatedness for individuals",
    ),
    cores: int = typer.Option(
        1,
        "-c",
        "--cores",
        help="number of cores to parallelize out to."
    ),
    loglevel: utilities.LogLevel = typer.Option(
        utilities.LogLevel.WARNING.value,
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
        "test_distributions.log", "--log-filename", help="Name for the log output file."
    ),
) -> None:
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
        case_control_filepath=case_control_file,
        database_path=database_path,
        output_path=output,
        core_count=cores,
        loglevel=loglevel,
        log_filename=log_filename,
    )

    logger.info(f"analysis start time: {start_time}")

    cases = utilities.read_in_grids(case_control_file, logger=logger,  case_or_control="cases")
    
    controls = utilities.read_in_grids(case_control_file, logger, case_or_control="controls")

    logger.info(f"Identified {len(cases)} cases and {len(controls)} controls")
    # getting the database connection
    conn = database.get_connection(database_path, logger=logger)

    conn.close()
    end_time = datetime.now()

    logger.info(f"analysis end time: {end_time}")

    logger.info(f"Analysis runtime: {end_time - start_time}")


if __name__ == "__main__":
    app()
