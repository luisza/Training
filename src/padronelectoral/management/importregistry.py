import argparse
import time
import logging
from pymongo import MongoClient
from django.core.management.base import BaseCommand
from django.db import connection
from django.db.models import signals
from padronelectoral.models import Elector, Province, Canton, District
from crpadron import settings
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Import CR registry '
    cantons = {}

    def add_arguments(self, parser):
        """
        Include extra parameters to command pipeline, define truncate value to 40000.
        Allow no clean parameter to prevent data clean.


        :param parser: Python argparse see https://docs.python.org/3/library/argparse.html for more information
        """

        parser.add_argument('registry', type=argparse.FileType('r', encoding="ISO-8859-1"),
                            help='Path to PADRON_COMPLETO.txt')
        parser.add_argument('distelec', type=argparse.FileType('r', encoding="ISO-8859-1"),
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
        start = time.time()
        logger.info("Stating import of registry")
        loader = self.get_loader()
        if not options['noclean']:
            logger.info("Cleanup datatables")
            self.calculate_speed(loader.clean_tables, "Cleaning datatables")

        self.calculate_speed(loader.import_districts, "Importing districts", options)
        self.calculate_speed(loader.import_registry, "Importing registry", options)
        self.calculate_speed(loader.calculate_stats, "Calculating stats")
        end = time.time()
        print("Complete in ", end - start, " s")

    def get_loader(self, options):
        loader = None
        if settings.MONGOSERVER != '':
            loader = MongoLoader

        else:
            loader = OrmLoader

        return loader


class OrmLoader:
    def get_canton(self, province, name, code):
        """
        Return a canton based on the name and code passed to function.

        :param province: province name
        :param name: canton name
        :param code: district code
        :return: Django Canton model
        """
        cantonid = code[:3]
        if cantonid not in self.cantons:
            province, created = Province.objects.get_or_create(
                code=code[0],
                name=province.strip()
            )
            canton, created = Canton.objects.get_or_create(
                code=cantonid,
                name=name.strip(),
                province=province)
            self.cantons[cantonid] = canton
        return self.cantons[cantonid]

    def import_districts(self, options):
        """
        Import all districts form diselect.txt file.

        :param options: Argparse arguments (required diselect)
        """
        print("Importing Districts ")
        distrits = []
        for line in options['distelec'].readlines():
            code, province, canton, distr = line.split(',')
            objcanton = self.get_canton(province, canton, code)

            distrits.append(District(
                codelec=code,
                name=distr.strip(),
                canton=objcanton
            ))
        # District.objects.bulk_create(distrits)
        print("Importing %d districts " % (len(distrits)))
        logger.info("Importing %d districts " % (len(distrits)))

    def clean_tables(self):
        """
        Delete all data on database if exists.
        """
        print("Deleting all registry data")
        with connection.cursor() as cursor:
            logger.debug("Execute 'TRUNCATE `padronelectoral_elector`' ")
            # Delete in raw for optimization
            cursor.execute('TRUNCATE `padronelectoral_elector`')

        # Using cascade aproach to delete other tables
        print(Province.objects.all().delete())

    def get_values_from_file(self, options):
        """
        Extract some amount of  values based on truncate parameter on options, yield data with sql structure to insert
        into database.
        :param options:  Argparse arguments (required registry)
        """
        max_element = options['truncate']
        count = 0
        values = ""

        for line in options['registry'].readlines():
            count += 1
            data = line.strip().split(',')
            fullname = "%s %s %s" % (data[5].strip(), data[6].strip(), data[7].strip())
            # idCard, gender, cad_date, board, fullName, codelec_id
            values += "( %s, %s, %s, %s, \"%s\", %s ), " % (
                data[0], data[2], data[3], data[4], fullname, data[1])
            if count == max_element:
                count = 0
                yield values[:-2]
                values = ""
        if values != "":
            yield values[:-2]

    def import_registry(self, options):
        sql = "INSERT INTO padronelectoral_elector (idCard, gender, cad_date, board, fullName, codelec_id) VALUES %s;"

        count = 0
        with connection.cursor() as cursor:
            for values in self.get_values_from_file(options):
                # print(sql%values)
                cursor.execute(sql % (values,))
                count += options['truncate']
                print("Importing %d electors" % count, end='')
                # revert the car to before line on console
                print('\r', end='')
        print("")
        logger.info("Importing %d electors " % (count))

    def calculate_stats(self):
        """
        Calculate the stats base on imported data
        """
        print("Doing stats")
        for dist in District.objects.all():
            update_district(dist)
        logger.info("Calculate stats to %d districts " % (District.objects.all().count()))


class MongoLoader:

    def import_districts(self, options):
        """
        Import all districts form diselect.txt file.

        :param options: Argparse arguments (required diselect)
        """

        client = MongoClient(settings.MONGOSERVER,
                             username=settings.MONGOUSERNAME, password=settings.MONGOPASSWORD)
        db = client['padron']

        print("Importing Districts ")
        dist_list = []
        for line in options['distelec'].readlines():
            code, province, canton, distr = line.split(',')
            objcanton = self.get_canton(province, canton, code)
            dist_doc = {
                'codelec': code,
                'name': distr,
                'canton': objcanton

            }
            dist_list.append(dist_doc)

        districts = db.districts
        districts.insert_many(dist_list)

        print("Importing %d districts using mongo" % (len(dist_list)))
        logger.info("Importing %d districts using mongo" % (len(dist_list)))

    def get_canton(self, province, name, code):
        """
        Return a canton based on the name and code passed to function.

        :param province: province name
        :param name: canton name
        :param code: district code
        :return: Django Canton model
        """

        client = MongoClient(settings.MONGOSERVER,
                             username=settings.MONGOUSERNAME, password=settings.MONGOPASSWORD)
        db = client['padron']
        cantonid = code[:3]
        if cantonid not in self.cantons:
            # province mongo document

            prov_doc = {
                'code': code[0],
                'name': province.strip
            }
            provinces = db.provinces
            provinces.insert_one(prov_doc)

            # canton mongo document
            cant_doc = {
                'code': cantonid,
                'name': name.strip
            }
            cantons = db.cantons
            cantons.insert_one(cant_doc)
            self.cantons[cantonid] = cant_doc['code']
        return self.cantons[cantonid]

    def get_values_from_file(self, options):
        """
        Extract some amount of  values based on truncate parameter on options, yield data with sql structure to insert
        into database.
        :param options:  Argparse arguments (required registry)
        """
        max_element = options['truncate']
        count = 0
        values = []

        for line in options['registry'].readlines():
            count += 1
            data = line.strip().split(',')
            fullname = "%s %s %s" % (data[5].strip(), data[6].strip(), data[7].strip())
            # idCard, gender, cad_date, board, fullName, codelec_id
            values += "( %s, %s, %s, %s, \"%s\", %s ), " % (
                data[0], data[2], data[3], data[4], fullname, data[1])
            Elector = {
                'idCard': data[0],
                'codelec': data[1],
                'gender': [2],
                'cad_date': data[3],
                'board': data[4],
                'fullName': fullname
            }
            values.append(Elector)
            if count == max_element:
                count = 0
                yield values[:-2]
                values = ""
        if values != "":
            yield values[:-2]

    def import_registry(self, options):

        client = MongoClient(settings.MONGOSERVER,
                             username=settings.MONGOUSERNAME, password=settings.MONGOPASSWORD)
        db = client['padron']

        elector_list = self.get_values_from_file(options)
        electors = db.electors
        electors.insert_many(elector_list)

        print("")
        logger.info("Importing %d electors " % (len(elector_list)))

    def clean_tables(self):
        """
        Delete all data on database if exists.
        """
        client = MongoClient(settings.MONGOSERVER,
                             username=settings.MONGOUSERNAME, password=settings.MONGOPASSWORD)
        db = client['padron']
        db.dropDatabase()
        print("Deleting all registry data")

    def calculate_stats(self):
        """
        Calculate the stats base on imported data
        """
        print("Working on Doing stats")
