from bpyutils.util.array   import sequencify
from bpyutils.util.imports import import_handler

# imports - module imports
from s3mart.cli.parser import get_args
from s3mart import cli

def group_commands(group, commands):
    """
    Add command-paths to a click.Group
    """
    commands = sequencify(commands, type_ = tuple)

    for command in commands:
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
        _, tail = command.rsplit(".", 1)
        tails   = ("", tail, "command")
=======
        head, tail = command.rsplit(".", 1)
        tails      = ("", tail, "command")
>>>>>>> template/master
=======
        head, tail = command.rsplit(".", 1)
        tails      = ("", tail, "command")
>>>>>>> template/master
=======
        head, tail = command.rsplit(".", 1)
        tails      = ("", tail, "command")
>>>>>>> template/master

        for i, tail in enumerate(tails):
            try:
                path    = "%s.%s" % (command, tail)
                command = import_handler(path)

                break
            except:
                if i == len(tails) - 1:
                    raise
        
        group.add_command(command)
    
    return group

def cli_format(string, type_):
    args = get_args(as_dict = False)
    
    if hasattr(args, "no_color") and not args.no_color:
        string = cli.format(string, type_)

    return string