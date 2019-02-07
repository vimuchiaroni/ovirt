import logging
import time
import subprocess
import ovirtsdk4 as sdk
import ovirtsdk4.types as types
import config_rhev as configsrc
import logging
import sys
import datetime

class Init(object):

    logging.basicConfig(filename='/tmp/move.log', level=logging.DEBUG)


    def __init__(self):
        """just update dictionary to make a copy"""
        self.rhev_manager = "https://%s/ovirt-engine/api" % configsrc.RHEV_MANAGER_LAB
        self.rhev_username = configsrc.RHEV_USERNAME
        self.rhev_password = subprocess.getoutput(
            f'echo {configsrc.RHEV_PASSWORD} | openssl enc -aes-128-cbc -a -d -salt -pass pass:wtf')
        self.vms = configsrc.vms


    def move_disks(self,storage,vm):

        try:
            api = sdk.Connection(url=self.rhev_manager,
                                 username=self.rhev_username,
                                 password=self.rhev_password,
                                 insecure=True)

            system_service = api.system_service()
            vms_service = system_service.vms_service()
            server = vms_service.list(search="%s" % vm)
            vm_service = vms_service.vm_service(server[0].id)
            snaps_service = vm_service.snapshots_service()
            disks_service = api.system_service().disks_service()
            my_disks = disks_service.list(search='name=%s*' %vm)
            for disk in my_disks:

                now = datetime.datetime.now()


                my_disk = disk.id
                disk_name = disk.alias
                logging.info("Starting to move disk %s to %s at %s" % (disk_name, storage, now))

                disk_service = disks_service.disk_service(my_disk)
                disk_service.move(storage_domain=types.StorageDomain(
                name=storage))
                while True:

                    time.sleep(60)
                    disk = disk_service.get()
                    if disk.status == types.DiskStatus.OK and len(snaps_service.list()) < 2:
                        logging.info("Finished to move disk %s to %s at %s" % (disk_name, storage, now))
                        break

                time.sleep(60)
        except Exception as ex:

            logging.error("Unexpected error: %s" % ex)
        api.close()

def main():

    rhev = Init()

    #Get the argument
    #arg = sys.argv[1]
    #arg1 = sys.argv[2]


    rhev.move_disks(<YourStorageDomain>,<YourVM>)



if __name__ == '__main__':
    main()
