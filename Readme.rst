Costa Rican registry management
==================================

How to run
------------

Before start install requirements and run migrations:

::

    pip install -r requirements.txt
    python manage.py migrate

Try to import the registry.

Download from http://www.tse.go.cr/zip/padron/padron_completo.zip the complete registry file
Unzip the file and run

:warning:   Do not open the file 'PADRON_ELECTORAL_COMPLETO.txt', computer could freeze.

::

   python loadData.py <diselect path>  <registry path>

This command create the files:

- querysProvince.sql
- querysCanton.sql
- querysDistrict.sql
- querys.sql

Using mysql client import those files in the same order as show after

:important: You must need to change the database credentials

::

   mysql -u solvo -psolvop4ss -D padron < querysProvince.sql
   mysql -u solvo -psolvop4ss -D padron < querysCanton.sql
   mysql -u solvo -psolvop4ss -D padron < querysDistrict.sql
   mysql -u solvo -psolvop4ss -D padron < querysElector.sql



To run
--------

::

   python manage.py runserver