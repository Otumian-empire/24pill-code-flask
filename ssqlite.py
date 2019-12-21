import sqlite3


class ssqlite:
    """ This is an Abstraction layer on sqlite3.
    It is limited to executing one query at a go."""

    def __init__(self, database_name=None):
        """ connect to database, by passing the database name as an argument """

        self.connection = None
        self.cursor = None

        # check if the database_name is not None
        if not database_name == None or not database_name:
            self.connection = sqlite3.connect(database_name)
            self.cursor = self.connection.cursor()
        else:
            raise BaseException(
                "No database selected, pass name in constructor")

    def run_query(self, sql_query='', *parameters):
        """
        return the cursor object if a query was executed successfull, else may raise an exception.
        You may call fetchone, fetchall or fetchmany to read your data.
        """

        if not self.cursor:
            raise BaseException("Database not selected")

        return self.cursor.execute(sql_query, parameters)

    def stamp(self):
        """ commit and close the connection to the database.
        Do not call this method in the middle of your code when you would run more queries with the same cursor, though you can still create a new object of ssqlite """
        self.connection.commit()
        self.cursor.close()
        self.connection.close()
