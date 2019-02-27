# !/usr/bin/python3

from pymongo import MongoClient, UpdateOne
from django.conf import settings


class MongoDB:
    def __init__(self):
        self.client = MongoClient(settings.MONGOSERVER,
                                  username=settings.MONGOUSERNAME,
                                  password=settings.MONGOPASSWORD)
        self.database = self.client.admin

    def get_values_from_file(self, options):
        """
        Reads registry text file to update the database
        :param options:
        :return:
        """
        max_element = options['truncate']
        count = 0
        values = []

        for line in options['registry'].readlines():
            count += 1
            data = line.strip().split(',')
            fullname = "%s %s %s" % (data[5].strip(), data[6].strip(), data[7].strip())
            # idCard, gender, cad_date, board, fullName, codelec_id

            Elector = {
                'idCard': data[0],
                'codelec': data[1],
                'gender': data[2],
                'cad_date': data[3],
                'board': data[4],
                'fullName': fullname
            }
            values.append(Elector)
            if count == max_element:
                count = 0
                yield values
                values = []
        if values != []:
            yield values

    def clean_tables(self):
        """
        This function drop all the data in each table
        :return:
        """
        self.database.province.drop()
        self.database.canton.drop()
        self.database.district.drop()
        self.database.electors.drop()

    def import_districts(self, options):
        """
        This function is to import disctricts, cantons, and provinces
        :param options: Options provide us the diselect path
        :return: Completed cantons, provinces y district list
        """
        districts_list = []
        provinces_list = []
        cantons_list = []
        actual_province_id = 0
        actual_canton_id = 0

        for line in options['diselect'].readlines():
            code, province, canton, distr = line.split(',')
            if (actual_province_id != code[0]):
                province_dictionary = {'code': code[0], 'name': province, 'canton_id': code[:3]}
                provinces_list.append(province_dictionary)
                actual_province_id = code[0]
            # code[:3] are the canton id, this is unique
            elif (actual_canton_id != code[:3]):
                canton_dictionary = {'code': code[:3], 'province': code[0], 'name': canton}
                cantons_list.append(canton_dictionary)
                actual_canton_id = code[:3]
            district_dictionary = {'code': code, 'canton': code[:3], 'name': distr}
            districts_list.append(district_dictionary)

        # save the lists created in the appropriate tables.
        self.database.province.insert_many(provinces_list)
        self.database.canton.insert_many(cantons_list)
        self.database.district.insert_many(districts_list)

    def import_registry(self, options):
        """
        This function is to save all the electors information, in this case is important to
        save the province, canton and district id. In this way, we can "join" the information
        :param options: Options provide us the registry path
        :return: Saving the data in mongodb
        """

        count = 0

        electors = self.database.electors
        for list_electors in self.get_values_from_file(options):
            electors.insert_many(list_electors)
            count += options['truncate']
            print("Importing %d electors" % count, end='')
            # revert the car to before line on console
            print('\r', end='')
        print("")


    def calculate_stats(self):

        """
        Counts all men and women on each district, canton and province and updates stats on each table.
        :return:
        """
        dist_updates = []
        canton_updates = []
        prov_updates = []

        dist_stats = list(self.database.electors.aggregate([
            {'$group': {
                "_id": "$codelec",
                "stats_male": {
                    "$sum": {"$cond": [{"$eq": ["$gender", '1']}, 1, 0]}
                },
                "stats_female": {
                    "$sum": {"$cond": [{"$eq": ["$gender", '2']}, 1, 0]}
                },
                "stats_total": {
                    "$sum": 1
                }
            }}
        ]))

        for d in dist_stats:
            dist_id = d.pop('_id')
            dist_updates.append(UpdateOne(
                {'code': dist_id},
                {'$set': d}
            ))

        # Bulk updates all stats from district, canton and province collections.
        print('Calculating District stats')
        self.database.district.bulk_write(dist_updates)

        canton_stats = list(self.database.district.aggregate([
            {'$group': {
                "_id": "$canton",
                "stats_male": {
                    "$sum": '$stats_male'
                },
                "stats_female": {
                    "$sum": '$stats_female'
                },
                "stats_total": {
                    "$sum": '$stats_total'
                }
            }}
        ]))


        for c in canton_stats:
            cant_id = c.pop('_id')
            canton_updates.append(UpdateOne(
                {'code': cant_id},
                {'$set': c}
            ))

        print('Calculating Canton stats')
        self.database.canton.bulk_write(canton_updates)

        province_stats = list(self.database.canton.aggregate([
            {'$group': {
                "_id": "$province",
                "stats_male": {
                    "$sum": '$stats_male'
                },
                "stats_female": {
                    "$sum": '$stats_female'
                },
                "stats_total": {
                    "$sum": '$stats_total'
                }
            }}
        ]))

        for p in province_stats:
            prov_id = p.pop('_id')
            prov_updates.append(UpdateOne(
                {'code': prov_id},
                {'$set': p}
            ))

        print('Calculating Province stats')
        self.database.province.bulk_write(prov_updates)
