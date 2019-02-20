# !/usr/bin/python3

from pymongo import *
from django.conf import settings


class MongoDB:
    def __init__(self):
        self.client = MongoClient(settings.MONGOSERVER,
                                  username=settings.MONGOUSERNAME,
                                  password=settings.MONGOPASSWORD)
        self.database = self.client.admin

    def get_values_from_file(self, options):
        print("get values from MongoDB")

    def clean_tables(self):
        """
        This function drop all the data in each table
        :return:
        """
        self.database.province.drop()
        self.database.canton.drop()
        self.database.district.drop()
        self.database.electors.drop()
        self.database.cantons.drop()
        self.database.districts.drop()
        self.database.provinces.drop()

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
            district_dictionary = {'code': code, 'canton': code[:3], 'name': distr, 'stats_female': 0, 'stats_male': 0,
                                   'stats_total': 0}
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
            electors_dictionary = {'idCard': idCard, 'id_district': codelec, 'id_province': codelec[0],
                                   'id_canton': codelec[:3], 'gender': gender, 'cad_date': cad_date,
                                   'board': board, 'full_name': full_name}
            electors_list.append(electors_dictionary)
        # bulk insert in electors table.
        self.database.electors.insert_many(electors_list)

    def calculate_stats(self):
        """
        This function calculate all the stats for each district and save it
        :return:
        """
        # all existing districts
        district_list = self.database.district.find()
        canton_list = self.database.canton.find()
        province_list = self.database.province.find()

        stats_males = self.database.electors.aggregate(
            {'$match': {'gender': '1'}},
            {'$group': {'id_district': "$id_district"}}
        ).count()

        stats_females = self.database.electors.aggregate(
            {'$match': {'gender': '2'}},
            {'$group': {'id_district': "$id_district"}}
        ).count()

        for district in district_list:
            # keep the electors that correspond to each id_district
            total_males = stats_males[district['code']]
            total_females = stats_females[district['code']]
            total_electors = total_females + total_males
            # update each district with electors count
            self.database.district.update_one(
                {'code': district['code']},
                {"$set": {'stats_female': total_females, 'stats_male': total_males,
                          'stats_total': total_electors}})
        print('Calculating stats...Please Wait...')

        for canton in canton_list:
            districts_canton = self.database.district.find({'canton': canton['code']})
            total_males = 0
            total_female = 0

            for dist in districts_canton:
                total_males += dist['stats_male']
                total_female += dist['stats_female']

            total_electors = total_males + total_female

            self.database.canton.update_one(
                {'code': canton['code']},
                {'$set': {'stats_male': total_males, 'stats_female': total_female, 'stats_total': total_electors}}
            )

        print('Processing canton stats...Please Wait...')

        for prov in province_list:
            province_cantons = self.database.canton.find({'province': prov['code']})
            total_males = 0
            total_female = 0

            for cant in province_cantons:
                total_males += cant['stats_male']
                total_female += cant['stats_female']
                total_electors = total_males + total_female

            self.database.province.update_one(
                {'code': prov['code']},
                {'$set': {'stats_male': total_males, 'stats_female': total_female, 'stats_total': total_electors}}
            )

            print('Calculating province stats...Please Wait...')
