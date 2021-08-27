import sys
import subprocess
import glob
import os
from pathlib import Path
from argparse import ArgumentParser

from rich.console import Console
from rich.progress import track
from rich.prompt import Prompt

from logger import log, logfile

console = Console()


def recursively_discover_repos(top: Path):
    discovered = []
    for root, subdirs, files in os.walk(top):
        log("Indexing: " + root)
        root = Path(root).resolve()
        if (root / ".git").exists():
            log("Found repo at: " + str(root.resolve()))
            console.print("[ [green]OK[/green] ]    Discovered git repo at", str(root.resolve()))
            discovered.append(root / ".git")
        else:
            log("No repo found at: " + str(root.resolve()))
    log(f"Found {len(discovered)} repos in {str(top.resolve())}.")
    return discovered


parser = ArgumentParser()
parser.add_argument("--mode", "--discover", "--discover-mode", action="store", choices=["recursive", "glob"],
                    default="recursive")
parser.add_argument("--pattern", "--dir", action="store", default=None)
args = parser.parse_args()

os.chdir(Path.home())

if args.mode == "glob":
    glob_pattern = args.pattern or Prompt.ask(
        "Please enter glob pattern",
        console=console,
        default="./*/*/.git"
    )
    glob_pattern = glob_pattern.replace("~", str(Path.home()))
    log("Glob pattern: " + glob_pattern)
    dirs = glob.glob(glob_pattern)
else:
    index_directory = Path(
        args.pattern or Prompt.ask("Which top-level directory should be indexed?", default=str(Path.home()))
    )
    if not index_directory.exists():
        console.print("Directory doesn't exist.")
        sys.exit()
    with console.status("Searching for git repositories in " + str(index_directory.resolve()), spinner="arrow3"):
        dirs = list(map(str, recursively_discover_repos(index_directory)))

for path in track(dirs, description="Running 'git pull'", console=console):
    os.chdir(Path.home())
    top_level = Path(path).parent.resolve()
    os.chdir(top_level)
    log("Running 'git pull' in " + str(top_level))
    result = subprocess.run(["git", "pull"], capture_output=True)
    if result.stdout:
        log("========= stdout =========\n"+result.stdout.decode("utf-8", "replace")+"\n========== ////// ==========")
    if result.stderr:
        log("========= stderr =========\n"+result.stderr.decode("utf-8", "replace")+"\n========== ////// ==========")
    if result.returncode == 0:
        console.print("[ [green]OK[/] ]    ", str(top_level), 0)
    else:
        console.print("[ [red]FAILED[/] ]", str(top_level), result.returncode)

console.print("Done.")
log("Program finished.")
console.print("Flushing log file")
logfile.flush()
logfile.close()
