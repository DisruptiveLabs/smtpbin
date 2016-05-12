MIGRATIONS = [
    (1, ["CREATE TABLE _version (version INTEGER);",

         "CREATE TABLE inbox ("
         "    id INTEGER PRIMARY KEY AUTOINCREMENT,"
         "    name VARCHAR(255) UNIQUE,"
         "    apikey VARCHAR(255),"
         "    count INTEGER DEFAULT 0,"
         "    unread INTEGER DEFAULT 0"
         ");",

         "CREATE TABLE messages ("
         "    id INTEGER PRIMARY KEY AUTOINCREMENT,"
         "    inbox INTEGER,"
         "    received TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"
         "    read BOOLEAN DEFAULT 0,"
         "    fromaddr VARCHAR,"
         "    toaddr VARCHAR,"
         "    subject VARCHAR(255),"
         "    body TEXT,"
         "    FOREIGN KEY(inbox) REFERENCES inbox(id)"
         ");",

         "CREATE TRIGGER inbox_messages_insert_count AFTER INSERT ON messages FOR EACH ROW BEGIN"
         "  UPDATE inbox "
         "  SET count = (SELECT COUNT(*) FROM messages WHERE inbox = NEW.inbox),"
         "      unread = (SELECT COUNT(*) FROM messages WHERE inbox = NEW.inbox AND read = 0 )"
         "  WHERE id = NEW.inbox;"
         "END;",

         "CREATE TRIGGER inbox_messages_update_count AFTER UPDATE ON messages FOR EACH ROW BEGIN"
         "  UPDATE inbox "
         "  SET count = (SELECT COUNT(*) FROM messages WHERE inbox = NEW.inbox),"
         "      unread = (SELECT COUNT(*) FROM messages WHERE inbox = NEW.inbox AND read = 0 )"
         "  WHERE id = NEW.inbox;"
         "END;",

         "INSERT INTO _version (version) VALUES (1);"]),
]
