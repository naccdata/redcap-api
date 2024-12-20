# NACC REDCap API

Library for interacting with the REDCap API.

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

### Formatting and Linting 

To format and lint with pants, run:

```bash
pants fmt ::   # fixes formatting
pants lint ::  # run linter
```

### Testing

To test with pants, run:

```bash
# use the --test-force flag to ignore the cache and force all tests to run
pants test ::
``` 

### Building a Distribution

To package the distribution with pants, run: 

```bash
pants package ::
```

will then build sdist and wheel distributions in the `dist` directory.

> The version number on the distribution files is set in the `redcap_api/BUILD` file.
