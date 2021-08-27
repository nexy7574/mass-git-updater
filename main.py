import re
import sys
import subprocess
import glob
import os
from pathlib import Path
from argparse import ArgumentParser
import time

from rich.console import Console
from rich.progress import track
from rich.prompt import Prompt

console = Console()


def recursively_discover_repos(top: Path):
    discovered = []
    for root, subdirs, files in os.walk(top):
        root = Path(root).resolve()
        if (root / ".git").exists():
            console.print("[ [green]OK[/green] ]    Discovered git repo at", str(root.resolve()))
            discovered.append(root / ".git")
    return discovered


parser = ArgumentParser()
parser.add_argument("--mode", "--discover", "--discover-mode", action="store", choices=["recursive", "glob"],
                    default="recursive")
args = parser.parse_args()

os.chdir(Path.home())

if args.mode == "glob":
    glob_pattern = Prompt.ask(
        "Please enter glob pattern",
        console=console,
        default="./*/*/.git"
    )
    glob_pattern = glob_pattern.replace("~", str(Path.home()))
    dirs = glob.glob(glob_pattern)
else:
    index_directory = Path(
        Prompt.ask("Which top-level directory should be indexed?", default=str(Path.home()))
    )
    if not index_directory.exists():
        console.print("Directory doesn't exist.")
        sys.exit()
    with console.status("Searching for git repositories in " + str(index_directory.resolve()), spinner="dots12"):
        dirs = list(map(str, recursively_discover_repos(index_directory)))

for path in track(dirs, description="Running 'git pull'", console=console):
    os.chdir(Path.home())
    top_level = Path(path).parent.resolve()
    os.chdir(top_level)
    result = subprocess.run(["git", "pull"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    if result.returncode == 0:
        console.print("[ [green]OK[/] ]    ", str(top_level), 0)
    else:
        console.print("[ [red]FAILED[/] ]", str(top_level), result.returncode)

console.print("Done.")
