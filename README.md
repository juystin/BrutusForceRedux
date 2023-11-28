# BrutusForceRedux
A scraper for OSU's public-facing APIs.

Outputs to user's choice of local SQLite file, remote MySQL server, or Firestore.

Collects information about classes, classrooms, buildings, instructors, and libraries.

### How to Use

Download and run the package. Follow on-screen prompt for commands.

### SQLite Integration

The .db file will automatically save into /data.

### Remote MySQL Integration

Type in your username, password, and hostname. A database will automatically be created by the script.

### Firestore Integration

This script integrates with Firestore. Configure a service account and place the .json key into /data/keys.