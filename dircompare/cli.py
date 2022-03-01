"""Command line interface for dircompare"""
import os
import click
from datetime import datetime
from dircompare.colllectors import CollectionResult, FlatCollector, DATEFORMAT
from dircompare.triggers import FilesMissingTrigger
from dircompare.actions import ACTIONMAP
import logging

logging.basicConfig()


@click.group()
def cli():
    pass


@click.command()
@click.option("--outputDir", default="./", help="Output directory for scan file")
@click.argument("root_directories", nargs=-1)
def scan(root_directories, outputdir):
    collector = FlatCollector(root_directories)
    collector.collect_files()
    collector.save(outputdir)


@cli.group()
def triggers():
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
    "--threshhold",
    default=50,
    help="Threshold of missing files above which actions are triggered",
)
def missing_files(newscan, oldscan, action_names, threshhold):
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
    trigger = FilesMissingTrigger(actions=actions, number_threshold=threshhold)
    trigger.inspect(old_result, new_result)


cli.add_command(scan)
triggers.add_command(missing_files)
