'''
Folder sync using rsync
By - Karan Dev
Date - 08 Jan 2017
'''
# if intracting with remote, set your ssh key on remote server
# so that it does not ask for password.
# Library used: https://linux.die.net/man/1/rsync
# apt-get(or yum) install rsync 
# Setup:
# Run this file in crontab of both the systems
# * * * * * /usr/bin/python PATH_TO_FILE/code.py LOCAL_LOCATION_OF_FOLDER ADDRESS_OF_REMOTE_FOLDER
# LOCAL_LOCATION_OF_FOLDER - /home/karan/local1/
# ADDRESS_OF_REMOTE_FOLDER - remote.example.com:/home/karan/local2/
# This will run every minute to sync send the changes from local to remote

import sys
import subprocess

class SyncDir :

    def __init__ (self):
        self.__system_1 = ''
        self.__system_2 = ''
        

    def index(self):
        self.__get_source_and_dest_file()
        self.__sync_data()


    def __get_source_and_dest_file(self):
        if len(sys.argv) != 3:
            print "Wrong no. of arguments, Please specify SYSTEM_1 and SYSTEM_2 paths respectively"
            exit(0)
        else:
            self.__system_1 = sys.argv[1] if (sys.argv[1][-1:] == '/') else (sys.argv[1] + '/')
            self.__system_2 = sys.argv[2] if (sys.argv[2][-1:] == '/') else (sys.argv[2] + '/')

    def __sync_data(self):

        output = subprocess.Popen(["rsync", "-avzr", self.__system_1, self.__system_2], stdout=subprocess.PIPE)
        out, err = output.communicate()
        print "Error: " + str(err) + " occured." if ( err ) else out
        print "Cron Completed"


if __name__ == '__main__' :
    syn_dir_obj = SyncDir()
    syn_dir_obj.index()