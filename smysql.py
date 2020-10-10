import mysql.connector


class smysql:
    """ This is an Abstraction layer on mysql.
    It is limited to executing one query at a go."""

    def __init__(self, host="", user="", password="", database=""):
        """ connect to database, by passing the database name as an argument """

        try:
            self.connection = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database
            )
            self.cursor = self.connection.cursor(buffered=True)

        except Exception as e:
            print(e)

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
