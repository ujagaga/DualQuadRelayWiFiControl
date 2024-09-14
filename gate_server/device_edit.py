#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

import argparse
import sys
import database
import helper


def list_devices(connection, db_cursor, name: str = None):
    devices = database.get_device(connection, db_cursor, name=name)

    message = "INFO: Listing devices in database"

    if name:
        print(f'{message} with name "{name}":')
        if devices:
            print("\t", devices)
        else:
            print("\tINFO: No device found with specified name!")
    else:
        print(f'{message}:')
        if len(devices) == 0:
            print("\tINFO: No devices found in database.")
        else:
            for device_obj in devices:
                print("\t", device_obj)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--list", help="List devices", required=False, action='store_true')
    parser.add_argument("-d", "--delete", help="Delete specified device", required=False, action='store_true')
    parser.add_argument("-a", "--authorize", help="Authorize email", required=False)
    parser.add_argument("-u", "--unauthorize", help="Unauthorize email", required=False)
    parser.add_argument("-n", "--name", help="Specify device name", required=False)

    args = parser.parse_args()

    connection = database.open_db()

    if args.list:
        list_devices(connection)

    if args.delete:
        if not args.name:
            sys.exit("ERROR: Please provide name of the device to delete.")

        print(f"INFO: Deleting device with name: {args.name}")
        database.delete_device(connection, name=args.name)

        print("Checking result:")
        list_devices(connection, name=args.name)

    elif args.authorize:
        if not args.name:
            sys.exit("ERROR: Please provide device name.")
        new_email = args.authorize

        device = database.get_device(connection, name=args.name)

        user = database.get_user(connection, email=new_email)
        if not user:
            sys.exit("ERROR: Specified user is not found in database.")

        email_list = device["email"].split("|")
        for email in email_list:
            if email == new_email:
                sys.exit("Specified user is already authorized.")

        email_list.append(new_email)
        new_list = ""
        for email in email_list:
            new_list = f"{new_list}|{email}"
        new_list += "|"
        database.update_device(connection, name=args.name, email=new_list)

    elif args.unauthorize:
        if not args.name:
            sys.exit("ERROR: Please provide device name.")

        old_email = args.authorize

        device = database.get_device(connection, name=args.name)

        user = database.get_user(connection, email=old_email)

        if not user:
            sys.exit("ERROR: Specified user is not found in database.")

        email_list = device["email"].split("|")
        email_list.remove(old_email)

        new_list = ""
        for email in email_list:
            new_list = f"{new_list}|{email}"
        new_list += "|"
        database.update_device(connection, name=args.name, email=new_list)

    database.close_db(connection)
