# step by step deployment djwiki on mysql #

  1. install mysql
> > Get it from here (for eg.) http://www.mysql.ru/download/
  1. create database for djwiki
> > `mysql\bin\mysqladmin.exe -u login -ppswd create djwiki`
  1. dump current db  (optional)
> > `manage.py dumpdata > wiki.json`
  1. change settings.py
```
    ...
      DATABASE_ENGINE = 'mysql' 
      DATABASE_NAME = 'djwiki'
      DATABASE_USER = 'login'             
      DATABASE_PASSWORD = 'pswd'       
      DATABASE_HOST = 'localhost'     
      DATABASE_PORT = '3306'  
    ...
```
  1. create tables in mysql db
> > `manage.py syncdb`
> > > NOTE: Python module MySQLdb should be installed to run this command successfull
> > > download it: http://sourceforge.net/project/showfiles.php?group_id=22307
  1. load data from dump (optional)

> > `manage.py loaddata wiki.json`
  1. run the server
> > `manage.py runserver`
  1. **have fun**