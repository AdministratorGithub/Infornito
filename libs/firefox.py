import sqlite3
import os
import json

from datetime import datetime
from libs.general import general

class firefox(general):

    config = {
        'hisotry_database_name' : 'places.sqlite',
        'platform_profile_path' : {
            'windows' : 'AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\',
            'darwin' : 'Library/Application Support/Firefox/Profiles',
            'linux' : '.mozilla/firefox/Profiles/'
        }
    }

    def __init__(self):
        general.__init__(self)
        self.profiles_path = os.path.join(self.user_home, self.config['platform_profile_path'][self.platform_name])

    def history(self, profile_path, filters=None):
        query_filters = ""
        if filters:
            query_filters = " WHERE "
            if filters.get('domain'):
                query_filters += "url LIKE 'http'"

        query = "SELECT url, visit_count, datetime(last_visit_date/1000000,'unixepoch') FROM moz_places"+query_filters+' ORDER BY visit_count;'
        print(query)
        # try:
        connection = sqlite3.connect(os.path.join(profile_path, self.config['hisotry_database_name']))
        db_cursor = connection.cursor()
        db_cursor.execute(query)
        urls = db_cursor.fetchall()
        parsed_histories = []
        for url in urls:
            parsed_histories.append({
                'url' : url[0],
                'count' : str(url[1]),
                'last_visit' : str(url[2])
            })
        db_cursor.close()
        return parsed_histories        
        # except Exception as error:
        #     print('Error : ' + str(error))
        #     exit()

    def downloads(self, profile_path):
        try:
            connection = sqlite3.connect(os.path.join(profile_path, self.config['hisotry_database_name']))
            db_cursor = connection.cursor()
            downloaded_files = db_cursor.execute("SELECT places.url, basic_info.content, basic_info.dateAdded, extended_info.content FROM moz_annos AS basic_info JOIN moz_annos AS extended_info ON basic_info.place_id=extended_info.place_id JOIN moz_places as places ON basic_info.place_id=places.id WHERE basic_info.anno_attribute_id='4' AND extended_info.anno_attribute_id='6'").fetchall()
        
            downloads = []
            for url in downloaded_files:
                download_metadata = json.loads(url[3])

                is_fully_download = False
                if download_metadata['state'] == 1:
                    is_fully_download = True
                
                filesize = download_metadata.get('fileSize')
                downloads.append({
                    'url' : url[0],
                    'saved_in' : str(url[1][7:]),
                    'start_downloading_at' : datetime.fromtimestamp(float(url[2])/1000000.0).strftime('%Y-%m-%d %H:%M:%S'),
                    'filesize' : filesize,
                    'is_fully_download' : is_fully_download
                })

            db_cursor.close()
            return downloads

        except Exception as error:
            print('Error : ' + str(error))
            exit()
    
    def get_profiles(self):
        profiles = []
        if os.path.isdir(self.profiles_path):
            for profile in os.listdir(self.profiles_path):
                profiles.append({'path' : self.profiles_path + '/' + profile, 'name': profile, 'browser': self.__class__.__name__})
        return profiles

    def fingerprint(self, profile_path):
        output = {
            firefox.config['hisotry_database_name']: {
                'md5' : self.md5sum(os.path.join(profile_path, firefox.config['hisotry_database_name'])),
                'sha1' : self.sha1sum(os.path.join(profile_path, firefox.config['hisotry_database_name'])),
                'sha256' : self.sha256sum(os.path.join(profile_path, firefox.config['hisotry_database_name']))
            }
        }
        return output