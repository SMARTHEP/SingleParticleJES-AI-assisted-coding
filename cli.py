"""
Command-line interface for SmartHEP SingleParticleJES package.

This module provides a command-line interface for running the SingleParticleJES
analysis on xAOD ROOT files.
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import List, Optional

from smarthep_singleparticlejes.core.analyzer import run_single_particle_jes_analysis


def setup_logging(verbose: bool = False) -> None:
    """
    Set up logging configuration.
    
    Args:
        verbose: If True, set log level to DEBUG, otherwise INFO.
    """
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)]
    )


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """
    Parse command-line arguments.
    
    Args:
        args: Command-line arguments to parse. If None, sys.argv[1:] is used.
        
    Returns:
        Parsed arguments namespace.
    """
    parser = argparse.ArgumentParser(
        description="SmartHEP SingleParticleJES - High Energy Physics Analysis Tool",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        "input_files",
        nargs="+",
        help="Path to input xAOD ROOT file(s). Can be a single file or multiple files."
    )
    
    parser.add_argument(
        "-o", "--output",
        default="analysis_output.root",
        help="Path to output ROOT file for histograms."
    )
    
    parser.add_argument(
        "-t", "--tree-name",
        default="CollectionTree",
        help="Name of the TTree in the input file."
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output."
    )
    
    return parser.parse_args(args)


def main(args: Optional[List[str]] = None) -> int:
    """
    Main entry point for the CLI.
    
    Args:
        args: Command-line arguments to parse. If None, sys.argv[1:] is used.
        
    Returns:
        Exit code (0 for success, non-zero for failure).
    """
    parsed_args = parse_args(args)
    setup_logging(parsed_args.verbose)
    
    logger = logging.getLogger(__name__)
    logger.info(f"Starting SingleParticleJES analysis with {len(parsed_args.input_files)} input file(s)")
    
    # Validate input files
    for input_file in parsed_args.input_files:
        if not Path(input_file).exists():
            logger.error(f"Input file does not exist: {input_file}")
            return 1
    
    # Run analysis
    success = run_single_particle_jes_analysis(
        parsed_args.input_files,
        parsed_args.output,
        parsed_args.tree_name
    )
    
    if success:
        logger.info(f"Analysis completed successfully. Output saved to: {parsed_args.output}")
        return 0
    else:
        logger.error("Analysis failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
