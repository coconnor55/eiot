""" Module Configuration """
##Copyright 2016 Clint H. O'Connor
##
##   Licensed under the Apache License, Version 2.0 (the "License");
##   you may not use this file except in compliance with the License.
##   You may obtain a copy of the License at
##
##       http://www.apache.org/licenses/LICENSE-2.0
##
##   Unless required by applicable law or agreed to in writing, software
##   distributed under the License is distributed on an "AS IS" BASIS,
##   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
##   See the License for the specific language governing permissions and
##   limitations under the License.
   

##----- imports -----------------------------------------------------------------
import json
import sys


##----- classes --------------------------------------------------------------------

class Configuration(object):

    def __init__(self, filename, default_configuration):
        self.filename = filename
        self.configuration = default_configuration

    def read(self):
        try:
            with open(self.filename, 'r') as filein:
                self.configuration = json.load(filein)
                return self.configuration
        except:
            try:
                self.write()
                return self.configuration
            except:
                raise Exception(thisdoc + ".read crashed")

    def write(self):
            with open(self.filename, 'w') as fileout:
                json.dump(self.configuration, fileout)
        
        
