# Gate Server

Python3 Flask website to controll the devices
When you deploy it or run locally, first run the "passenger_wsgi.py". It will create an SQLite database. The run the user_edit.py to add the users.

Once you create the hardware devices, they will try to access the website. Their ID will be added to device database, but only the last 2 unauthorized devices.
You will need to manually edit the database to add user email in the device/email column. Make sure to separate the emails with '|'. This is to prevent matching similar email adresses.

The user login is done using Google OAuth2, so the user emails must be GMail based. The upside is there is no password.

## TODO

Add device admin tool so you do not have to adit the DB manually.