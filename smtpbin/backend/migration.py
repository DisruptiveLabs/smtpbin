MIGRATIONS = [
    (1, ["CREATE TABLE _version (version integer);",
         "CREATE TABLE messages ("
         "    id INTEGER PRIMARY KEY AUTOINCREMENT,"
         "    received TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"
         "    fromaddr VARCHAR,"
         "    toaddr VARCHAR,"
         "    subject VARCHAR(255),"
         "    body TEXT"
         ");",
         "INSERT INTO _version (version) VALUES (1);"]),
]
