import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")

    SQLALCHEMY_TRACK_MODIFICATIONS = False    



#import os


#BASE_DIR = os.path.abspath(os.path.dirname(__file__))

#class Config:
    #SECRET_KEY = "alamkamal_1234578987"
    # For SQL LITE
    #SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR,"instance","mosque.db")

    # For PostgreSQL
    #SQLALCHEMY_DATABASE_URI = "postgresql://postgres:Alam1993@localhost:5432/dn_mosque_db"

    #SQLALCHEMY_TRACK_MODIFICATIONS = False


    