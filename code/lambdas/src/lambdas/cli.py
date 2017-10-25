"""Commands available in the CLI"""
import logging
from pathlib import Path

from cliff.command import Command
from cliff.lister import Lister
from pkg_resources import resource_filename
from lambdas.lambda_zip import LambdaZipper



class Package(Command):
    """Package a lambda project"""

    log = logging.getLogger(__name__)
    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument('project', help='Folder name of the lambda function')
        return parser

    def take_action(self, parsed_args):
        self.log.debug(vars(parsed_args))
        if parsed_args.project:
            zipper = LambdaZipper(parsed_args.project)
            zipper.package()
            self.app.stdout.write(f'Done. Created {zipper.zip_path}\n')




class Lambdas(Lister):
    """Show the lambda projects in lambdas
    """
    log = logging.getLogger(__name__)
    def take_action(self, parsed_args):
        r = Path(resource_filename('lambdas', 'main.py'))
        return ('Name', 'Size'), ((n.name, n.stat().st_size) for n in r.parent.glob('*[!_]/') if n.is_dir())
