"""Commands available in the CLI"""
import logging

from cliff.command import Command


class Check(Command):
    "Check klempner installation"

    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        self.log.debug(vars(parsed_args))
        self.app.stdout.write('Klempner is installed :-)\n')
