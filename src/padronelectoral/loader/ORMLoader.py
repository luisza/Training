import logging
from django.db import connection
from django.db.models import Sum, F, Q

from padronelectoral.models import District, Province, Canton, Elector

logger = logging.getLogger(__name__)


class ORM:
    cantons = {}

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
        for line in options['diselect'].readlines():
            code, province, canton, distr = line.split(',')
            objcanton = self.get_canton(province, canton, code)

            distrits.append(District(
                codelec=code,
                name=distr.strip(),
                canton=objcanton
            ))
        District.objects.bulk_create(distrits)
        print("Importing %d districts " % (len(distrits)))
        logger.info("Importing %d districts " % (len(distrits)))

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
        list_electors = Elector.objects.all()
        dist_list = District.objects.all()
        cant_list = Canton.objects.all()

        print("Calculating district stats")
        for dist in District.objects.all():
            dist.stats_male = list_electors.filter(codelec=dist.codelec, gender=1).count()
            dist.stats_female = list_electors.filter(codelec=dist.codelec, gender=2).count()
            dist.stats_total = dist.stats_male + dist.stats_female
            dist.save()

        print("Calculating canton stats")
        for canton in Canton.objects.all():
            d = dist_list.aggregate(men=Sum('stats_male', filter=Q(canton=canton.code)),
                                    women=Sum('stats_female', filter=Q(canton=canton.code)),
                                    elector_count=Sum('stats_total', filter=Q(canton=canton.code)))


            canton.stats_male = d['men']
            canton.stats_female = d['women']
            canton.stats_total = d['elector_count']
            canton.save()

        print("Calculating province stats")
        for prov in Province.objects.all():
            cn = cant_list.aggregate(men=Sum('stats_male', filter=Q(province=prov.code)),
                                     women=Sum('stats_female', filter=Q(province=prov.code)),
                                     elector_count=Sum('stats_total', filter=Q(province=prov.code)))

            prov.stats_male = cn['men']
            prov.stats_female = cn['women']
            prov.stats_total = cn['elector_count']
            prov.save()
