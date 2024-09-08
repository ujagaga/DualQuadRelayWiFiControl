#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import sys
import database
import helper


def list_users(db_obj, email: str = None):
    users = database.get_user(db=db_obj, email=email)
    message = "INFO: Listing users in database"

    if email:
        print(f'{message} with e-mail "{email}":')
        if users:
            print("\t", users)
        else:
            print("\tINFO: No user found with specified e-mail!")
    else:
        print(f'{message}:')
        if not users:
            print("\tINFO: No users found in database.")
        else:
            for user_obj in users:
                print("\t", user_obj)


def validate_email(email: str):
    if not helper.validate_email(email):
        sys.exit(f"ERROR: Invalid e-mail: {email}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--email", help="E-mail", required=False)
    parser.add_argument("-o", "--operation", help="Operation", required=True,
                        choices=['add', 'delete', 'list'])

    args = parser.parse_args()

    db = database.open_db()

    if args.operation == 'list':
        list_users(db_obj=db)

    elif args.operation == 'add':
        if not args.email:
            sys.exit("ERROR: Please provide email to create a new user")

        # Check if user with same username exists
        user = database.get_user(db=db, email=args.email)
        if user:
            sys.exit(f"ERROR: User exists: {user}")

        validate_email(args.email)

        database.add_user(db=db, email=args.email)
        print("Checking result:")
        list_users(db_obj=db, email=args.email)

    elif args.operation == 'delete':
        if not args.email:
            sys.exit("ERROR: Please provide email of the user to delete.")

        print(f"INFO: Deleting user with email: {args.email}")
        database.delete_user(db=db, email=args.email)

        print("Checking result:")
        list_users(db_obj=db, email=args.email)

    database.close_db(db)
