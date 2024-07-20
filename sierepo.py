import argparse

import commands

parser = argparse.ArgumentParser(prog='SIERRA Repository Client',
                                 description='CLI tool to work with SIERRA repository servers')

parser.add_argument("command")
parser.add_argument("-r", required=False)
parser.add_argument("-s", required=False)
args = parser.parse_args()

match args.command:
    case "update":
        commands.update()
    case "info":
        commands.info(args.s)
    case "install":
        commands.install(args.r)
