'''
    DESCRIPTION:
    ------------
    * The purpose of this class is create a folder for Insta scrapper
    * Export the json file to Folder
'''
import json
import os
class Exportjson:
    def __init__(self, file_name, json_data, folder_name=None):
        self.file_name=file_name
        self.data=json_data
        self.path=os.getcwd()+"/data/reddit"

    def dump_json(self):
        with open(f'{self.path}/{self.file_name}.json', 'w') as json_file:
            json.dump(self.data, json_file, indent=4)
    def make_dir(self):
        try:
            if not os.path.exists(self.path):
                os.mkdir(self.path)
        except OSError as e:
            print (e) 