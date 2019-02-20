# !/usr/bin/python3

from pymongo import *
from django.conf import settings


class MongoDB:
    def __init__(self):
        self.client = MongoClient(settings.MONGOSERVER,
                                  username=settings.MONGOUSERNAME,
                                  password=settings.MONGOPASSWORD)
        self.database = self.client.admin

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

        # Save the cantons and provinces ids
        provinces_ids = []
        cantons_ids = []

        for line in options['diselect'].readlines():
            code, province, canton, distr = line.split(',')

            # It is to save only the provinces that have not been saved in the list of provinces.
            if code[0] not in provinces_ids:
                province_dictionary = {'code': code[0], 'name': province,
                                       'stats_female': 0, 'stats_male': 0, 'stats_total': 0}
                provinces_list.append(province_dictionary)
                provinces_ids.append(code[0])

            # It is to save only cantons that have not been saved in the list. code[:3] is the canton id and its unique
            elif code[:3] not in cantons_ids:
                canton_dictionary = {'code': code[:3], 'name': canton, 'stats_female': 0, 'stats_male': 0, 'stats_total': 0}
                cantons_list.append(canton_dictionary)
                cantons_ids.append(code[:3])
            district_dictionary = {'code': code, 'name': distr, 'stats_female': 0, 'stats_male': 0, 'stats_total': 0}
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
        electors_list = []
        for line in options['registry'].readlines():
            # split all the information in each line, then is necessary to create an dictionary in a list
            idCard, codelec, gender, cad_date, board, name, first_name, last_name = line.split(',')
            full_name = "%s %s %s" % (name.strip(), first_name.strip(), last_name.strip())
            electors_dictionary = {'id_card': int(idCard), 'id_district': codelec, 'id_province': codelec[0],
                                   'id_canton': codelec[:3], 'gender': gender, 'cad_date': cad_date,
                                   'board': board, 'full_name': full_name}
            electors_list.append(electors_dictionary)
        # bulk insert in electors table.
        self.database.electors.insert_many(electors_list)

    def update_stats(self, database, id_to_find):
        """
        :param database: The database to update the stats information
        :param id_to_find: The id to find to search in electors count()
        :return: All the stats updated to the database received in the parameter
        """
        list_database = database.find()
        for item in list_database:
            states_male = self.database.electors.find({id_to_find: item['code'], 'gender': "1"}).count()
            states_female = self.database.electors.find({id_to_find: item['code'], 'gender': "2"}).count()
            database.update_one(
                {'code': item['code']},
                {"$set": {'stats_female': states_female, 'stats_male': states_male,
                          'stats_total': states_female + states_male}})

    def calculate_stats(self):
        """
        This function calculate all the stats for each district and save it
        :return: All the stats updated in mongo
        """
        # Call this function and you need to send the database name and the id to find
        self.update_stats(self.database.province, 'id_province')
        self.update_stats(self.database.canton, 'id_canton')
        self.update_stats(self.database.district, 'id_district')




