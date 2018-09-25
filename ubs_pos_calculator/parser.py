import argparse
import sys

from api.ubs import PosCalculator


def get_user_options():
    """
    Get user input for source and target directory
    :return: source, target
    """
    source = target = None
    parser = argparse.ArgumentParser(description="""Get input from user""",
                                     formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument("-source",
                        help="dir where Input_StartOfDay_Positions.txt and Input_Transactions.txt will be present",
                        type=str,
                        required=True)
    parser.add_argument("-target",
                        help="dir where EndOfDay_Positions.txt will be created",
                        type=str,
                        required=True)

    args = parser.parse_args()
    return args.source, args.target

if __name__ == '__main__':
    # Get source and target directory path from user as an input
    source_dir, target_dir = get_user_options()

    # Create parser object
    pc = PosCalculator(source_dir, target_dir)
    pc.calculate()

