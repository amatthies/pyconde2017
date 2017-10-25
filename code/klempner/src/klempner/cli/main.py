"""A CLI for klempner"""
import sys

from cliff.app import App
from cliff.commandmanager import CommandManager


class KlempnerApp(App):
    def __init__(self):
        super().__init__(
            description='Klempner CLI',
            version='0.0.1',
            command_manager=CommandManager('klempner.cli'),
            deferred_help=True,
        )

    def initialize_app(self, argv):
        self.LOG.debug('initialize_app')
        # hide the cliff complete command, it's confusing
        self.command_manager.commands.pop('complete', None)

    def prepare_to_run_command(self, cmd):
        self.LOG.debug('prepare_to_run_command %s', cmd.__class__.__name__)

    def clean_up(self, cmd, result, err):
        self.LOG.debug('clean_up %s', cmd.__class__.__name__)
        if err:
            self.LOG.debug('got an error: %s', err)


def main(argv=sys.argv[1:]):
    myapp = KlempnerApp()
    return myapp.run(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
