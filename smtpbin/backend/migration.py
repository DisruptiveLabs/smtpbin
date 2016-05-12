MIGRATIONS = [
    (1, ["CREATE TABLE _version (version integer);",

         "CREATE TABLE inbox ("
         "    id INTEGER PRIMARY KEY AUTOINCREMENT,"
         "    name VARCHAR(255) UNIQUE,"
         "    apikey VARCHAR(255)"
         ");",

         "CREATE TABLE messages ("
         "    id INTEGER PRIMARY KEY AUTOINCREMENT,"
         "    inbox INTEGER,"
         "    received TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"
         "    fromaddr VARCHAR,"
         "    toaddr VARCHAR,"
         "    subject VARCHAR(255),"
         "    body TEXT,"
         "    FOREIGN KEY(inbox) REFERENCES inbox(id)"
         ");",

         "INSERT INTO _version (version) VALUES (1);"]),
]
