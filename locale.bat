D:\Python27\Scripts\pybabel.exe extract -F .\locale\babel.cfg -o ./locale/messages.pot .

D:\Python27\Scripts\pybabel.exe update -l eu_ES -d ./locale -i ./locale/messages.pot
D:\Python27\Scripts\pybabel.exe update -l es_ES -d ./locale -i ./locale/messages.pot
D:\Python27\Scripts\pybabel.exe update -l en_US -d ./locale -i ./locale/messages.pot

D:\Python27\Scripts\pybabel.exe compile -f -d ./locale