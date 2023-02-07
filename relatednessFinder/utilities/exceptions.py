class IncorrectGridFileFormat(Exception):
    """Exception that will be thrown if the grid file is not in the right format"""

    def __init__(self, line_num: int, grid_file: str) -> None:
        super().__init__(
            f"There was an error reading in the file: {grid_file} at line {line_num}. Program expected each line to be a separate ID."
        )