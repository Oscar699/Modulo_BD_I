import oracledb
import os
from conf.config import Config
oracledb.init_oracle_client(lib_dir="C:/oraclexe/app/oracle/product/11.2.0/server/bin")
os.environ["NLS_LANG"] = "SPANISH_SPAIN.UTF8"

class Conexion:
    def __init__(self):
        self.__connection = oracledb.connect(
            user=Config.USUARIO,
            password=Config.PASSWORD,
            dsn=Config.DNS,
            encoding='AL16UTF16', nencoding='AL16UTF16')

        self.__cursor = self.__connection.cursor()
        print("Successfully connected to Oracle Database")

    def getCursor(self):
        return self.__cursor

    def commit(self):
        self.__connection.commit()
