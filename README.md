# NACC REDCap API

Library for interacting with the REDCap API.

The core library is under `redcap_api`. Additional internal tools that utilize it are under `tools`.

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

To package the main `redcap_api` distribution with pants, run: 

```bash
pants package common/redcap_api ::
```

To package one of the internal tool distributions, run:

```bash
pants package tools/<name-of-tool> ::
# for example
# pants package tools/redcap_error_checks_import ::
```

The above will build sdist and wheel distributions in the `dist` directory.

> The version number on the distribution files is set in the `redcap_api/BUILD` file.
