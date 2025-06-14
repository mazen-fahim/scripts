"""
Every Time I click mainMod + shift + somekey I open a clean playground in
an empty workspace (right now it's hard coded to 7).
Right now the script will only keep track of processes it created and that's it.
If there are other windows terminals + browsers not created by this script it will never kill
it. It will only kill pid's that itself created... by hold on a minute... here is a scenario you
should think about
1. I run the script and it creates a terminal and a browser at worskpace 7
2. I store the PID's of them
3. I close the terminal and the browser manually and launch other processes
that may take the save PID's of old terminal + browsers that I've already killed.
4. So having only a PID is not enough information to tell me whether or not
these are the terminal's and broswer's playground.
I need somehow to query the process which I stored its PID and make sure that they
are the one that I created. how would I do this?
mark the hyprland clients with special names or classes???
"""

import re
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path

config = {
    "live_server_port": 8082,
    "terminal": "kitty",
    "browser": "chromium",
    "tmux_session_name": "web_playground",
}


# create temp dif if doesn't exists
def init(path: Path):
    if not path.exists():
        path.mkdir()


def python_playground(path: Path):
    pass


def web_playground(web_path: Path):
    web_path = web_path / "web"
    if web_path.is_dir():
        for item in web_path.iterdir():
            if item.is_file():
                item.unlink()
    else:
        web_path.mkdir()
    Path(web_path / "style.css").touch()
    Path(web_path / "main.js").touch()
    _ = Path(web_path / "index.html").write_text(
        textwrap.dedent(""" <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta http-equiv="X-UA-Compatible" content="ie=edge">
        <title>HTML 5 Boilerplate</title>
        <link rel="stylesheet" href="style.css">
        <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
    </head>

    <body>
        <div class="h-dvh w-dvw bg-gray-500 flex justify-center items-center">
            <div class="w-[500px] h-[500px] border-1 border-black">
            </div>
        </div>
        <script src="main.js"></script>
    </body>
    </html>
    """)
    )

    # A small shell script file that sets up the new kitty instance environment
    _ = Path(web_path / "setup.sh").write_text(
        textwrap.dedent(f"""\
        #! /usr/bin/env bash
        cd ~/.tmp/web/
        tmux kill-session -t {config["tmux_session_name"]}
        tmux new-session -s {config["tmux_session_name"]} -d "nvim index.html"
        tmux rename-window dev
        tmux new-window "live-server --port={config["live_server_port"]} --no-browser"
        tmux rename-window live-server
        tmux select-window -t 0
        tmux -2 attach-session -t {config["tmux_session_name"]} -d
        """)
    )

    # TODO:: Change kitty to terminal and chromium to browser
    _ = subprocess.run(
        ["hyprctl", "dispatch", "killwindow", "class:web_playground_kitty"]
    )
    # _ = subprocess.run(
    #     ["hyprctl", "dispatch", "killwindow", "class:web_playground_chromium"]
    # )
    _ = subprocess.run(
        [
            "hyprctl",
            "dispatch",
            "exec",
            f"[workspace 7] kitty --class web_playground_kitty -e {web_path / 'setup.sh'}",
        ]
    )
    _ = subprocess.run(
        [
            "hyprctl",
            "dispatch",
            "exec",
            f"chromium --auto-open-devtools-for-tabs --new-window --app=http://localhost:{config['live_server_port']}",
        ]
    )

    _ = subprocess.run(
        [
            "hyprctl",
            "notify",
            "-1",
            "10000",
            "rgb(e78a4e)",
            f'Session "{config["tmux_session_name"]}" created!',
        ]
    )


def main():
    path = Path.home() / ".tmp"
    init(path)
    if len(sys.argv) == 2:
        arg = sys.argv[1]
        if arg == "python":
            python_playground(path)
        elif arg == "web":
            web_playground(path)
    else:
        raise Exception("Specify one argument playground name")


if __name__ == "__main__":
    main()
