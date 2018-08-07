import sqlite3


class Database(object):
    DB_LOCATION = "instruction_db.sqlite"

    def __init__(self):
        self.connection = sqlite3.connect(Database.DB_LOCATION)
        self.cur = self.connection.cursor()

        self.create_table()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cur.close()
        if isinstance(exc_val, Exception):
            self.connection.rollback()
        else:
            self.connection.commit()
        self.connection.close()

    def close(self):
        self.connection.close()

    def create_table(self):
        query = '''CREATE TABLE IF NOT EXISTS instructions(id INTEGER PRIMARY KEY, \
                                                           instruction TEXT UNIQUE,
                                                           trap INTEGER, 
                                                           from_file INTEGER,
                                                           on_line INTEGER)'''
        self.cur.execute(query)

    def save_instruction(self, instruction, trap, file_no, line_no):
        try:
            query = "INSERT INTO instructions (instruction, trap, from_file, on_line) VALUES (?, ?, ?, ?)"

            self.cur.execute(query, (instruction, trap, file_no, line_no))
        except sqlite3.Error as e:
            print("Database error: Instruction %s is duplicate" % instruction)
        except Exception as e:
            print("Exception in _query: %s" % e)

    def reset(self):
        query = "DROP TABLE instructions"
        self.cur.execute(query)

        self.create_table()
