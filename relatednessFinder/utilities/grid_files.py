import logging
from pathlib import Path

import utilities
import log

@log.log_msg_debug("Reading in IDs")
def read_in_grids(grid_filepath: Path, logger: logging.Logger, case_or_control: str | None = None) -> list[str]:
    """Function that will read in all of the IDs from the provided file.

    Parameters
    ----------
    grid_filepath : Path
        path to a tab separated text file that list all the grids that the user
        wishes to find values for. Expects two column: The IDs and phenotype (In 
        that order). Header is optional

    logger : logging.Logger
        logging object

    case_or_control : str
        sting indicating if the user is trying to fid the cases of controls from a 
        file. If "cases" then the program will look for 1 in the phecode column if 
        controls then it will look for 0.

    Returns
    -------
    list[str]
        returns a list of IDs

    Raises
    ------
    IncorrectGridFileFormat 
        if the file is not formated where there is only a grid per line and the 
        phenotype status then this exception is raised
    """

    return_list = []


    with open(grid_filepath, "r", encoding="utf-8") as grid_input:
        match case_or_control:
            case "cases":
                search_val = 1
            case "controls":
                search_val = 0
            case _:
                search_val = None
            
        for line_num, line in enumerate(grid_input):
            split_line = line.split("\t")
            if len(split_line) != 2:
                raise utilities.IncorrectGridFileFormat(line_num, grid_filepath)
            if search_val and split_line[1] == search_val:
                return_list.append(split_line[0])
            else:
                return_list.append(split_line[0])

    return return_list