import logging
from pathlib import Path

import log
import utilities


class FileReader:
    def __init__(self, filepath: Path) -> None:
        self.filepath = filepath

    def __enter__(self) -> None:
        """Method that will be called by the with context manager.

        Raises
        ------
        OSError
            raises OSError if the file can't be opened"""
        try:
            self.open_file = open(self.filepath, "r", encoding="utf-8")
        except OSError as e:
            print(
                f"encountered an error while trying to open the file: {self.filepath}"
            )
            print(e)
        return self
    
    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.open_file.close()

    @log.log_msg_debug("Reading in IDs")
    def read_in_grids(
        self,
        logger: logging.Logger,
        cases_and_control: bool = False,
    ) -> tuple[list[str], list[str] | None]:
        """Function that will read in all of the IDs from the provided file.

        Parameters
        ----------
        grid_filepath : Path
            path to a tab separated text file that list all the grids that the user
            wishes to find values for. Expects two column: The IDs and phenotype (In
            that order). Program expects no header

        logger : logging.Logger
            logging object

        case_and_controls : bool
            boolean indicating if the program needs to consider the

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

        logger.debug("identifying grids within the provided file: {self.filepath}")

        if cases_and_control:
            cases = []
            controls = []
            for line_num, line in enumerate(self.open_file):
                split_line = line.strip().split("\t")
                grid_id = split_line[0]
                if len(split_line) != 2:
                    raise utilities.IncorrectGridFileFormat(line_num, self.filepath)
                if split_line[1] == "1":
                    cases.append(grid_id)
                elif split_line[0] == "0":
                    controls.append(grid_id)
            logger.info(
                f"Identified {len(cases)} case ids and {len(controls)} control ids in the grid file: {self.filepath}"
            )
            return cases, controls

        else:
            return_list = []
            for line_num, line in enumerate(self.open_file):
                split_line = line.strip().split("\t")

                if len(split_line) != 2:
                    raise utilities.IncorrectGridFileFormat(line_num, self.filepath)
                return_list.append(split_line[0])
            logger.info(
                f"Identified {len(return_list)} grids in the file: {self.filepath}"
            )
            return return_list, []
