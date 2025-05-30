"""
Basic tests for the CLI module.

These tests verify that the CLI argument parsing works correctly.
"""

import pytest
from unittest.mock import patch
import sys
from smarthep_singleparticlejes.cli import parse_args, main


def test_parse_args_defaults():
    """Test that default arguments are set correctly."""
    with patch.object(sys, 'argv', ['smarthep-jes', 'input.root']):
        args = parse_args()
        assert args.input_files == ['input.root']
        assert args.output == 'analysis_output.root'
        assert args.tree_name == 'CollectionTree'
        assert not args.verbose


def test_parse_args_custom():
    """Test that custom arguments are parsed correctly."""
    with patch.object(sys, 'argv', [
        'smarthep-jes',
        'input1.root',
        'input2.root',
        '-o', 'custom_output.root',
        '-t', 'MyTree',
        '-v'
    ]):
        args = parse_args()
        assert args.input_files == ['input1.root', 'input2.root']
        assert args.output == 'custom_output.root'
        assert args.tree_name == 'MyTree'
        assert args.verbose
