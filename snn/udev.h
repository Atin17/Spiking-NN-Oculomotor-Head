#include <libudev.h>
#include <stdio.h>
#include <stdlib.h>
#include <locale.h>
#include <unistd.h>
#include <vector>
#include <string>
#include <string.h>

using namespace std;

string list_udev(const char* subsystem)
{
    struct udev *udev;
    struct udev_enumerate *enumerate;
    struct udev_list_entry *devices, *dev_list_entry;
    struct udev_device *dev, *parent_dev;
    
    /* Create the udev object */
    udev = udev_new();
    if (!udev) {
        printf("Can't create udev\n");
        exit(1);
    }

    vector<string> serial, busnum, sysnum, sysname;
    
    /* Create a list of the devices in the 'hidraw' subsystem. */
    enumerate = udev_enumerate_new(udev);
    udev_enumerate_add_match_subsystem(enumerate, subsystem);
    udev_enumerate_scan_devices(enumerate);
    devices = udev_enumerate_get_list_entry(enumerate);
    /* For each item enumerated, print out its information.
       udev_list_entry_foreach is a macro which expands to
       a loop. The loop will be executed for each member in
       devices, setting dev_list_entry to a list entry
       which contains the device's path in /sys. */
    udev_list_entry_foreach(dev_list_entry, devices) {
        const char *path;
        
        /* Get the filename of the /sys entry for the device
           and create a udev_device object (dev) representing it */
        path = udev_list_entry_get_name(dev_list_entry);
        parent_dev = udev_device_new_from_syspath(udev, path);

        /* usb_device_get_devnode() returns the path to the device node
           itself in /dev. */
        
        /* The device pointed to by dev contains information about
           the hidraw device. In order to get information about the
           USB device, get the parent device with the
           subsystem/devtype pair of "usb"/"usb_device". This will
           be several levels up the tree, but the function will find
           it.*/
        dev = udev_device_get_parent_with_subsystem_devtype(
               parent_dev,
               "usb",
               "usb_device");
        if (!dev) {
            // printf("Unable to find parent usb device.");
            continue;
        }
        printf("Device Node Path: %s\n", udev_device_get_devnode(dev));
    
        /* From here, we can call get_sysattr_value() for each file
           in the device's /sys entry. The strings passed into these
           functions (idProduct, idVendor, serial, etc.) correspond
           directly to the files in the directory which represents
           the USB device. Note that USB strings are Unicode, UCS2
           encoded, but the strings returned from
           udev_device_get_sysattr_value() are UTF-8 encoded. */
        printf("  VID/PID: %s %s\n",
                udev_device_get_sysattr_value(dev,"idVendor"),
                udev_device_get_sysattr_value(dev, "idProduct"));
        printf("  %s - %s\n",
                udev_device_get_sysattr_value(dev,"manufacturer"),
                udev_device_get_sysattr_value(dev,"product"));

        const char* ser = udev_device_get_sysattr_value(dev, "serial");
        printf("  serial: %s\n", ser);
        if(ser != NULL)
          serial.push_back(ser);

        const char* bnum = udev_device_get_sysattr_value(dev, "busnum");
        printf("  busnum: %s\n", bnum);
        busnum.push_back(bnum);
        
        const char* sname = udev_device_get_sysname(parent_dev);
        printf("  sysname: %s \n", sname);
        sysname.push_back(sname);

        const char* snum = udev_device_get_sysnum(parent_dev);
        printf("  sysnum: %s \n", snum);
        sysnum.push_back(snum);
        
        udev_device_unref(dev);
    }
    /* Free the enumerator object */
    udev_enumerate_unref(enumerate);

    udev_unref(udev);

    if(strcmp(subsystem, "tty") == 0) {
      int i = 0;
      for(string ser : serial) {
        if(strcmp(ser.c_str(), "AL00CJYJ") == 0) {
          return sysname[i];
        }
        i++;
      }
    }

    if(strcmp(subsystem, "video4linux") == 0) {
      int left = -1, right = -1;
      string resp = "";
      int i = 0;
      for(string bnum : busnum) {
        if(bnum == "1")
          left = stoi(sysnum[i]);
        if(bnum == "2")
          right = stoi(sysnum[i]);
        i++;
      }
      resp = to_string(left) + "," + to_string(right);
      return resp;
    }

    return "";
}