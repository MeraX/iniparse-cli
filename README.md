iniparse-cli
============
iniparse-cli is a cli-wrapper tool for the python-library [iniparse](http://code.google.com/p/iniparse/)

All the credit of handling ini files is due to the creators of iniparser.

Usage
-----

 *  ```iniparse-cli.py config.ini```
    returns list of sections
 *  ```iniparse-cli.py config.ini SECTION```
    returns list of items in SECTION
 *  ```iniparse-cli.py config.ini SECTION OPTION```
    returns value of OPTION in SECTION
 *  ```iniparse-cli.py config.ini SECTION OPTION VALUE```
    sets VALUE of OPTION in SECTION
 *  ```iniparse-cli.py -d config.ini SECTION```
    deletes SECTION
 *  ```iniparse-cli.py -d config.ini SECTION OPTION```
    deletes OPTION in SECTION
 *  ```iniparse-cli.py -d config.ini SECTION OPTION VALUE```
    deletes value of OPTION in SECTION when VALUE matches


License & Copyright
-------------------
Copyright © 2013 - 2014 Marek Jacob

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, version 3 of the License only.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the [GNU General Public License](LICENSE) for more details.