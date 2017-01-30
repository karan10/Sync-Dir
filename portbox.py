
######################################################################################################
# By: Karan Dev                                                                                      #
# Date: Jan 31st, 2017                                                                               #
# Library required - sudo apt-get install python-pyinotify                                           #
# pass both system1 (local) and system2 (remote) path in argument (path can be anywhere in system)   #
# this file needs to run on both systems                                                             #
# system1 - python portbox.py /home/karan/Desktop/pp/both/local/ /home/karan/Desktop/pp/both/remote/ #
# system2 - python portbox.py /home/karan/Desktop/pp/both/remote/ /home/karan/Desktop/pp/both/local/ #
# As i don't have any remote machine, I am considering both location on same machine for now.        #
# Queries can be changed to call on remote machine.                                                  #
######################################################################################################

import asyncore
import pyinotify
import subprocess
from enum import Enum
import os
import time
import sys


if len(sys.argv) == 3:
    LOCAL_PATH  = sys.argv[1]
    REMOTE_PATH = sys.argv[2]
else:
    print "wrong path arguments"
    exit(0)


class portBox:

    def __init__(self):
        pass

    # idhar: scp here
    def _send_change_to_remote(self, data, change = Enum('CREATION', 'DELETION', 'UPDATION')):

        if change == 'CREATION':

            local = { k:[ i for i in v ] for k, v in self.__get_item_path_from_system(LOCAL_PATH).iteritems()}

            remote = { k:[ i for i in v ] for k, v in self.__get_item_path_from_system(REMOTE_PATH).iteritems()}

            # print os.path.commonprefix(local['dir'])
            # common_prefix = os.path.commonprefix(a)
            local_dir = [os.path.relpath(path, LOCAL_PATH) for path in local['dir']]
            remote_dir = [os.path.relpath(path, REMOTE_PATH) for path in remote['dir']]
            local_file = [os.path.relpath(path, LOCAL_PATH) for path in local['file']]
            remote_file = [os.path.relpath(path, REMOTE_PATH) for path in remote['file']]

            self.__upload_data_to_remote( list(set(local_dir)-set(remote_dir)), l_type='dir' )
            self.__upload_data_to_remote( list(set(local_file)-set(remote_file)), l_type='file' )


            
            self.__check_for_conflict( list(set(local_file).intersection(remote_file)) )


        elif change == 'DELETION':
            print data
            output = subprocess.Popen(["rm", '-r', REMOTE_PATH+data], stdout=subprocess.PIPE)
            output = subprocess.Popen(["rm", '-r', os.path.join('/.'.join(REMOTE_PATH[:-1].rsplit('/',1)),data)], stdout=subprocess.PIPE)
            output = subprocess.Popen(["rm", '-r', os.path.join('/.'.join(LOCAL_PATH[:-1].rsplit('/',1)),data)], stdout=subprocess.PIPE)

        elif change == 'FILE_UPDATION':
            self.__check_for_conflict([data])
        # out, err = output.communicate()


    def __get_item_path_from_system(self, root_path):

        folder_data, folders_path, files_path = [], [], []
        for root, dirs, files in os.walk(root_path):
            files = [f for f in files if not f[0] == '.']
            dirs[:] = [d for d in dirs if not d[0] == '.']
            # rel_dir = os.path.relpath(root)
            for name in files:
                files_path.append(os.path.join(root, name))
            for name in dirs:
                folders_path.append(os.path.join(root, name))

        return { 'dir': folders_path, 'file': files_path }

    # idhar: use scp
    def __upload_data_to_remote( self, path_list, l_type='file' ):

        for p in path_list:
            if l_type == 'dir':
                if not os.path.exists(p):
                    os.makedirs(REMOTE_PATH+p)
                    os.makedirs(os.path.join('/.'.join(REMOTE_PATH[:-1].rsplit('/',1)),p))
                    os.makedirs(os.path.join('/.'.join(LOCAL_PATH[:-1].rsplit('/',1)),p))
            else:
                print p
                if '/' in p:
                    temp_path, file_name = p.rsplit('/', 1)
                else:
                    temp_path = ''
                output = subprocess.Popen(["cp", '-r',LOCAL_PATH+p, REMOTE_PATH+temp_path], stdout=subprocess.PIPE)
                output = subprocess.Popen(["cp", '-r',LOCAL_PATH+p, os.path.join('/.'.join(REMOTE_PATH[:-1].rsplit('/',1)),p)], stdout=subprocess.PIPE)
                output = subprocess.Popen(["cp", '-r',LOCAL_PATH+p, os.path.join('/.'.join(LOCAL_PATH[:-1].rsplit('/',1)),p)], stdout=subprocess.PIPE)


    def __check_for_conflict(self, path_list):

        for p in path_list:
            output = subprocess.Popen(["diff", REMOTE_PATH+p, LOCAL_PATH+p ], stdout=subprocess.PIPE)
            local_diff, err = output.communicate()
            output = subprocess.Popen(["diff", REMOTE_PATH+p, os.path.join('/.'.join(REMOTE_PATH[:-1].rsplit('/',1)),p) ], stdout=subprocess.PIPE)
            remote_diff, err = output.communicate()
            # this if condition will work, when one file is changed after sync
            if local_diff and not remote_diff.strip():
                output = subprocess.Popen(["cp", '-r',LOCAL_PATH+p, REMOTE_PATH+p], stdout=subprocess.PIPE)
                output = subprocess.Popen(["cp", '-r',LOCAL_PATH+p, os.path.join('/.'.join(REMOTE_PATH[:-1].rsplit('/',1)),p)], stdout=subprocess.PIPE)
                output = subprocess.Popen(["cp", '-r',LOCAL_PATH+p, os.path.join('/.'.join(LOCAL_PATH[:-1].rsplit('/',1)),p)], stdout=subprocess.PIPE)

            # this condition will run when , both files are changed but sync is not yet done
            elif local_diff and remote_diff:
                fo = open(LOCAL_PATH+p, 'a')
                fo.write( '\n\n>>>>>>>>>> Resolve Conflict (help: http://www.computerhope.com/unix/udiff.htm) >>>>>>>>>>\n' + local_diff + '\n====================================================================' )
                fo.close()
                output = subprocess.Popen(["cp", '-r',LOCAL_PATH+p, REMOTE_PATH+p], stdout=subprocess.PIPE)
                output = subprocess.Popen(["cp", '-r',LOCAL_PATH+p, os.path.join('/.'.join(REMOTE_PATH[:-1].rsplit('/',1)),p)], stdout=subprocess.PIPE)
                output = subprocess.Popen(["cp", '-r',LOCAL_PATH+p, os.path.join('/.'.join(LOCAL_PATH[:-1].rsplit('/',1)),p)], stdout=subprocess.PIPE)



class EventHandler(pyinotify.ProcessEvent):
    def process_IN_CREATE(self, event):
        print "Creating:", event.pathname
        time.sleep(2)
        port_box_obj = portBox()
        port_box_obj._send_change_to_remote( (event.pathname).split(LOCAL_PATH)[1], change='CREATION')

    def process_IN_DELETE(self, event):
        print "Removing:", event.pathname
        time.sleep(2)
        print event.pathname
        port_box_obj = portBox()
        port_box_obj._send_change_to_remote( (event.pathname).split(LOCAL_PATH)[1], change='DELETION')

    def process_IN_CLOSE_WRITE(self, event):
        print "Changed:", event.pathname
        time.sleep(2)
        port_box_obj = portBox()
        port_box_obj._send_change_to_remote( (event.pathname).split(LOCAL_PATH)[1], change='FILE_UPDATION' )


if __name__ == '__main__' :

    wm = pyinotify.WatchManager()  # Watch Manager
    mask = pyinotify.IN_DELETE | pyinotify.IN_CREATE | pyinotify.IN_CLOSE_WRITE # watched events
    
    notifier = pyinotify.AsyncNotifier(wm, EventHandler())
    wdd = wm.add_watch(LOCAL_PATH, mask, rec=True)
    asyncore.loop()

