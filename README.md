# NACC REDCap API

Library for interacting with the REDCap API.

The core library is under `common/src/python/redcap_api`. Additional internal tools that utilize it are under `tools`.

## Development Setup

### Installing Pants

This repository uses [pants](pantsbuild.org) for developing and building the distributions.

Install pants with one of the following. See [Installing Pants](https://www.pantsbuild.org/stable/docs/getting-started/installing-pants) for more information.

For Linux:

```bash
bash get-pants.sh
```

For macOS:

```bash
brew install pantsbuild/tap/pants
```

You will need to make sure that you have a Python version compatible with the interpreter set in the `pants.toml` file.

### Dev Container

This project includes a dev container configuration for consistent development environments. See the scripts in `bin/` for container management:

```bash
./bin/start-devcontainer.sh  # Start the container
./bin/terminal.sh            # Open interactive shell
./bin/stop-devcontainer.sh   # Stop the container
```

All Pants commands should be run inside the dev container using `./bin/exec-in-devcontainer.sh`.

## Development Workflow

### Formatting and Linting

To format and lint with pants, run:

```bash
pants fmt ::   # fixes formatting
pants lint ::  # run linter
pants check :: # type checking
```

### Testing

To test with pants, run:

```bash
pants test ::  # run all tests
pants test :: --test-force  # ignore cache and force all tests to run
```

### Building a Distribution

To package the main `redcap_api` distribution with pants, run:

```bash
pants package common::
```

To package one of the internal tool distributions, run:

```bash
pants package tools/<name-of-tool>::
# for example
# pants package tools/redcap_error_checks_import::
```

The above will build sdist and wheel distributions in the `dist` directory. Note most of the tools rely on the common distribution which will need to be installed first.

> The version number on the distribution files is set in the `BUILD` file(s).

## Releasing

Releases are automated via GitHub Actions. To create a new release:

1. **Create and push a git tag** with the version number:
   ```bash
   git tag v0.1.3
   git push origin v0.1.3
   ```

2. **GitHub Actions will automatically:**
   - Update version numbers in BUILD files to match the tag
   - Run linting and type checking
   - Run all tests
   - Build distribution packages (wheels and sdists)
   - Create a GitHub release with auto-generated release notes
   - Upload all distribution files to the release

The release will be available at: `https://github.com/naccdata/redcap-api/releases`

> Note: The workflow automatically updates the version in BUILD files during the release process. You don't need to manually update them before tagging.
