






class Config:
    secret_key = 'tu_clave_secreta_aqui'



class DevelopmentConfig(Config):
    DEBUG = True
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = ''
    MYSQL_DB = 'test'


config = {
    'development': DevelopmentConfig
}

