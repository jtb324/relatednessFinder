from pathlib import Path
import database


def write_to_file(
    db_results: database.dbResults, output_filename: Path, relatedness_thres: int
) -> None:
    """Function that will write the output to a file

    Parameters
    ----------
    db_results : database.dbResults


    output_filename : Path
        Path to the output file

    relatedness_thres : int
        threashold for the minimum relatedness allowed. Should be between 0-9. Nine will be considered the highest threshold. 0 would remove all of the non related people

    """
    # We are going to iterate through the case results list because
    # thats the attribute that the database results get saved as when
    # the user determines relatedness for just a group of individuals
    # in the determine-relatedness command
    with open(output_filename, "w", encoding="utf-8") as output:
        output.write("ID1\tID2\tEstimated_relatedness\n")
        for pair_result in db_results.case_results:
            output.write(f"{pair_result[1]}\t{pair_result[2]}\t{pair_result[3]}\n")
