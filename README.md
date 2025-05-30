# SmartHEP SingleParticleJES

High Energy Physics Analysis Package for Single Particle Jet Energy Scale calibration in ATLAS.

## Overview

This package provides tools for analyzing single particle jet energy scale calibration in ATLAS using ROOT's RDataFrame for efficient data processing. It implements an optimized version of the SingleParticleJES analysis algorithm, focusing on performance and maintainability.

## Features

- Efficient data processing using ROOT's RDataFrame
- Command-line interface for easy analysis execution
- Comprehensive logging and error handling
- Modular design for extensibility and maintainability
- Support for multiple input files

## Installation

### Using uv (Recommended)

The SmartHEP SingleParticleJES package can be installed using the [uv package manager](https://github.com/astral-sh/uv), which provides fast, reliable Python package management.

```bash
# Install uv if you don't have it already
pip install uv

# Install the package
uv pip install smarthep-singleparticlejes
```

For development installation:

```bash
# Clone the repository
git clone https://github.com/smarthep/singleparticlejes.git
cd singleparticlejes

# Install in development mode with dev dependencies
uv pip install -e ".[dev]"
```

### Requirements

- Python 3.8 or higher
- ROOT with xAOD support
- xAODDataSource helper library

## Usage

### Command Line Interface

The package provides a command-line interface for running the analysis:

```bash
# Basic usage
smarthep-jes input_file.root

# Multiple input files
smarthep-jes input_file1.root input_file2.root

# Specify output file
smarthep-jes input_file.root -o output.root

# Specify tree name
smarthep-jes input_file.root -t CollectionTree

# Enable verbose output
smarthep-jes input_file.root -v
```

### Python API

You can also use the package as a Python library:

```python
from smarthep_singleparticlejes.core.analyzer import run_single_particle_jes_analysis

# Run analysis with default parameters
run_single_particle_jes_analysis("input_file.root")

# Run analysis with custom parameters
run_single_particle_jes_analysis(
    input_files=["input_file1.root", "input_file2.root"],
    output_filename="custom_output.root",
    tree_name="CollectionTree"
)
```

## Output

The analysis produces a ROOT file containing histograms of:

- Number of clusters
- Number of particles
- Leading cluster energy
- Particle PDG IDs
- Response (pT,cluster/pT,particle)
- 3D response binned by pT and eta

## Development

### Testing

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=smarthep_singleparticlejes
```

### Code Style

The codebase follows PEP 8 style guidelines and uses type hints. Code formatting is enforced using Black and isort.

```bash
# Check code style
black --check smarthep_singleparticlejes
isort --check smarthep_singleparticlejes

# Apply code style
black smarthep_singleparticlejes
isort smarthep_singleparticlejes
```

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to contribute to this project.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Citation

If you use this software in your research, please cite it using the information in [CITATION.cff](CITATION.cff).
