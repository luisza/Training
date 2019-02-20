import argparse
import time
import logging

from django.core.management.base import BaseCommand
from padronelectoral.loader.ORMLoader import ORM
from padronelectoral.loader.MongoLoader import MongoDB
from django.conf import settings

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Import CR registry '

    #   cantons = {}

    def add_arguments(self, parser):
        """
        Include extra parameters to command pipeline, define truncate value to 40000.
        Allow no clean parameter to prevent data clean.


        :param parser: Python argparse see https://docs.python.org/3/library/argparse.html for more information
        """

        parser.add_argument('registry', type=argparse.FileType('r', encoding="ISO-8859-1"),
                            help='Path to PADRON_COMPLETO.txt')
        parser.add_argument('diselect', type=argparse.FileType('r', encoding="ISO-8859-1"),
                            help='Path to Distelec.txt')
        parser.add_argument(
            '--truncate',
            dest='truncate',
            default=40000,
            type=int,
            help='Max number of elements inserted by statement',
        )

        parser.add_argument(
            '--noclean',
            dest='noclean',
            default=False,
            type=bool,
            help='',
        )

    def define_database(self):
        """"
            this method is for define the active_database,
            to use the factory method to call your own registry imports
        """
        if settings.ACTIVE_DATABASE == "MONGO":
            return MongoDB()
        elif settings.ACTIVE_DATABASE == "ORM":
            return ORM()

    def calculate_speed(self, func, message, *args):
        """
        Calculate the time spend by a function call

        :param func:  Function to call
        :param message: Message to print when time speed is available
        :param args:  Arguments to pass to functions
        """
        start = time.time()
        func(*args)
        end = time.time()
        print("Complete %s in " % message, end - start, " s")

    def handle(self, *args, **options):
        """
        Main call, process management callback and import all registry
        """
        db = self.define_database()

        start = time.time()
        logger.info("Stating import of registry")
        if not options['noclean']:
            logger.info("Cleanup datatables")
            self.calculate_speed(db.clean_tables, "Cleaning datatables")

        self.calculate_speed(db.import_districts, "Importing districts", options)
        self.calculate_speed(db.import_registry, "Importing registry", options)
        self.calculate_speed(db.calculate_stats, "Calculating stats")
        end = time.time()
        print("Complete in ", end - start, " s")
