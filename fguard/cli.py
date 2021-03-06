"""Command line interface for dircompare"""
import os
import click
from datetime import datetime
from fguard.colllectors import CollectionResult, FlatCollector, DATEFORMAT
from fguard.triggers import FilesMissingTrigger, ExperimentsMissingTrigger
from fguard.actions import ACTIONMAP
import logging

logging.basicConfig()


@click.group()
def cli():
    pass


@click.command()
@click.option("--outputDir", default="./", help="Output directory for scan file")
@click.option("--logLevel", default="INFO", help="Loglevel of collector")
@click.argument("root_directories", nargs=-1)
def scan(root_directories, outputdir, loglevel):
    collector = FlatCollector(root_directories, log_level=loglevel)
    collector.collect_files()
    collector.save(outputdir)


@cli.group()
def check():
    pass


@click.command()
@click.option(
    "--newScan",
    default=None,
    help="Defaults to the newest scan in the current working directory",
)
@click.option(
    "--oldScan",
    default=None,
    help="Defaults to the second newest scan in the current working directory",
)
@click.option(
    "--actions",
    "action_names",
    default=["stdout"],
    help="Actions to be performed when triggers fire",
    multiple=True,
)
@click.option(
    "--threshold",
    default=50,
    help="Threshold of missing files above which actions are triggered",
)
def missing_files(newscan, oldscan, action_names, threshold):
    # get actions
    actions = []
    for action_name in action_names:
        if action_name not in ACTIONMAP:
            raise ValueError(f"Action '{action_name}' not registered!")
        actions.append(ACTIONMAP[action_name]())
    # check scans
    if newscan is None or oldscan is None:
        # list scans in current working directory
        scan_files = [file for file in os.listdir() if file.endswith(".scan")]
        if len(scan_files) < 2:
            raise ValueError("Not enough scan files found in directory!")
        # sort scans by date
        date_sorted = sorted(
            scan_files,
            key=lambda x: datetime.strptime(x.split("_")[0], DATEFORMAT),
            reverse=True,
        )
        new_result = CollectionResult.from_file(date_sorted[0])
        old_result = CollectionResult.from_file(date_sorted[1])
    else:
        new_result = CollectionResult.from_file(newscan)
        old_result = CollectionResult.from_file(oldscan)
    # do comparison
    trigger = FilesMissingTrigger(actions=actions, number_threshold=threshold)
    trigger.inspect(old_result, new_result)


@click.command()
@click.option(
    "--newScan",
    default=None,
    help="Defaults to the newest scan in the current working directory",
)
@click.option(
    "--oldScan",
    default=None,
    help="Defaults to the second newest scan in the current working directory",
)
@click.option(
    "--actions",
    "action_names",
    default=["stdout"],
    help="Actions to be performed when triggers fire",
    multiple=True,
)
def missing_experiments(newscan, oldscan, action_names):
    # get actions
    actions = []
    for action_name in action_names:
        if action_name not in ACTIONMAP:
            raise ValueError(f"Action '{action_name}' not registered!")
        actions.append(ACTIONMAP[action_name]())
    # check scans
    if newscan is None or oldscan is None:
        # list scans in current working directory
        scan_files = [file for file in os.listdir() if file.endswith(".scan")]
        if len(scan_files) < 2:
            raise ValueError("Not enough scan files found in directory!")
        # sort scans by date
        date_sorted = sorted(
            scan_files,
            key=lambda x: datetime.strptime(x.split("_")[0], DATEFORMAT),
            reverse=True,
        )
        new_result = CollectionResult.from_file(date_sorted[0])
        old_result = CollectionResult.from_file(date_sorted[1])
    else:
        new_result = CollectionResult.from_file(newscan)
        old_result = CollectionResult.from_file(oldscan)
    # do comparison
    trigger = ExperimentsMissingTrigger(actions=actions)
    trigger.inspect(old_result, new_result)

cli.add_command(scan)
check.add_command(missing_files)
check.add_command(missing_experiments)
