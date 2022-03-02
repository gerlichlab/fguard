# File guard

A command line utility to monitor integrity of filesystems. File guard allows to scan directory trees and compare its state with previous scans. You can define triggers that perform actions in case of an integrity violation.

## Installation

You can install File guard from github using the following command:

```
pip install git+https://github.com/gerlichlab/fguard
```

## Usage

### Scan directory trees

You can scan a list of root directories with the `scan` command:

```
Usage: fguard scan [OPTIONS] [ROOT_DIRECTORIES]...

Options:
  --outputDir TEXT  Output directory for scan file
  --help            Show this message and exit.
```

You can supply a list of root directories that will be traversed. The absolute paths of found files are stored with associated statistics (size, last updated, created, uid) in a `pickle` file with the extension `.scan`.

### Compare scan

To compare scan files, you use the `triggers` command:

```
Usage: fguard triggers [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  missing-files
```

The `triggers` command has a sub-command for each trigger, e.g. the `missing-files` trigger. The `missing-files` trigger performs actions if a above a threshold number of files are missing:

```
Usage: fguard triggers missing-files [OPTIONS]

Options:
  --newScan TEXT        Defaults to the newest scan in the current working
                        directory
  --oldScan TEXT        Defaults to the second newest scan in the current
                        working directory
  --actions TEXT        Actions to be performed when triggers fire
  --threshhold INTEGER  Threshold of missing files above which actions are
                        triggered
  --help                Show this message and exit.
```

Actions can be found in the `actions.py` file and can currently be the `standardout` action and the `email` action (Note that for the `email` action, the `sendmail` command needs to be set-up and the environment variable `FGUARD_EMAIL_ADDRESS` of the recipient needs to be defined). Actions can be passed as a multiple style argument:

```
 fguard triggers missing-files --actions stdout --actions email
```

The `triggers` command defaults to comparing the newest two `.scan` files in the current working directory, but `.scan` files can also be supplied as separate arguments.