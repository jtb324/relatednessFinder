from typing import Generator
from pathlib import Path
from logging import Logger
import matplotlib.pyplot as plt

from log import log_msg_debug


def generate_results_list(
    case_results: Generator[list[tuple[int, str, str, int]], None, None], logger: Logger
) -> list[int]:
    """Function that will gather all of the output from the database generator into a list of relatedness values. The pair ids are not kept

    Parameters
    ----------
    case_results : Generator[list[tuple[int, str, str, int]], None, None]
        generator object that has the row results from the dataframe
        where each row is a tuple

    logger : logging.Logger
        logging object

    Returns
    -------
    list[int]
        returns a list of the relatedness values where each value is
        an integer
    """
    return_rel_list = []
    for val in case_results:
        for relatedness_tuple in val:
            rel_val = relatedness_tuple[3]
            return_rel_list.append(rel_val)

    return return_rel_list


@log_msg_debug("creating a plot of the relatedness distributions")
def plot_distribution(
    relatedness_dist: list[int], output_path: Path, file_suffix: str, logger=Logger
) -> None:
    """Function that creates histograms of the relatedness values

    relatedness_dist : list[int]
        list of relatedness values

    output_path : Path
        path object representing the path to write the output paths
        to

    file_suffix : str
        ending to add to the output file

    logger : logging.Logger
        logging object
    """
    # we are going to set the theme of the plot
    plt.style.use("seaborn-v0_8-paper")

    _ = plt.hist(relatedness_dist)

    plt.title("Distribution of relatedness values")

    plt.xlabel("Estimated relatedness")

    plt.ylabel("Counts")

    plt.savefig("_".join([output_path.name, file_suffix]))
