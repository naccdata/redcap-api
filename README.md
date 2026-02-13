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

Releases are automated via GitHub Actions. Here's the complete workflow:

### Development to Release Process

1. **Develop on a feature branch:**

   ```bash
   git checkout -b feature/my-feature
   # Make your changes
   git add .
   git commit -m "Add new feature"
   git push origin feature/my-feature
   ```

2. **Create a Pull Request:**
   - Open a PR from your feature branch to `main`
   - GitHub Actions will automatically run linting and tests
   - Wait for review and approval

3. **Merge to main:**
   - Merge the PR (squash, merge commit, or rebase - follow your team's convention)
   - Pull the latest main branch locally:

     ```bash
     git checkout main
     git pull origin main
     ```

4. **Create and push a release tag:**

   ```bash
   # Create an annotated tag with a descriptive message
   git tag -a v0.1.3 -m "Release v0.1.3: Add export_report method"
   
   # Push the specific tag to trigger the release workflow
   git push origin tag v0.1.3
   ```

5. **GitHub Actions will automatically:**
   - Update version numbers in BUILD files to match the tag
   - Run linting and type checking
   - Run all tests
   - Build distribution packages (wheels and sdists)
   - Create a GitHub release with auto-generated release notes
   - Upload all distribution files to the release

6. **Verify the release:**
   - Check the release at: `https://github.com/naccdata/redcap-api/releases`
   - Download and test the distribution files if needed

### Version Numbering

Follow [Semantic Versioning](https://semver.org/):

- `v1.0.0` - Major version (breaking changes)
- `v0.1.0` - Minor version (new features, backwards compatible)
- `v0.0.1` - Patch version (bug fixes)

> Note: The workflow automatically updates the version in BUILD files during the release process. You don't need to manually update them before tagging.
