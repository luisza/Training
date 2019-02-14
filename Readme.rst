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

   python manage.py  importregistry  <registry path> <diselect path>




To run
--------

::

   python manage.py runserver