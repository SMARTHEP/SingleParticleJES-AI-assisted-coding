# Contributing to SmartHEP SingleParticleJES

Thank you for considering contributing to the SmartHEP SingleParticleJES project! This document provides guidelines and instructions for contributing.

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue using the bug report template. Include:

1. A clear, descriptive title
2. A detailed description of the issue
3. Steps to reproduce the bug
4. Expected behavior
5. Actual behavior
6. Environment information (OS, Python version, ROOT version)
7. Any additional context or screenshots

### Suggesting Enhancements

For feature requests, please create an issue using the feature request template. Include:

1. A clear, descriptive title
2. A detailed description of the proposed feature
3. Rationale for the enhancement
4. Any implementation ideas you have
5. Any potential alternatives you've considered

### Pull Requests

1. Fork the repository
2. Create a new branch from `main`
3. Make your changes
4. Add or update tests as needed
5. Ensure all tests pass
6. Update documentation as needed
7. Submit a pull request

#### Pull Request Guidelines

- Follow the coding style of the project
- Include tests for new features or bug fixes
- Update documentation for any changed functionality
- Keep pull requests focused on a single change
- Link the pull request to any related issues

## Development Setup

1. Clone the repository
2. Install development dependencies:
   ```bash
   uv pip install -e ".[dev]"
   ```
3. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

## Coding Standards

- Follow PEP 8 style guidelines
- Use type hints
- Write docstrings for all functions, classes, and modules
- Keep functions focused on a single responsibility
- Write tests for new functionality

## Testing

Run tests with pytest:

```bash
pytest
```

## Documentation

- Update documentation for any changed functionality
- Follow the existing documentation style
- Use clear, concise language

## Versioning

We use [Semantic Versioning](https://semver.org/). Please ensure your changes are appropriately versioned.

## License

By contributing to this project, you agree that your contributions will be licensed under the project's [Apache 2.0 License](LICENSE).
