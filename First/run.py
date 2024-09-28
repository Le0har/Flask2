from my_app import app
from config import DevelopmentConfig


#print(app.default_config)
app.config.from_object('config.DevelopmentConfig')

#print('\n============= after loading ==========\n')
#print(app.config) #Словарь настроек для запуска приложения Flask


if __name__ == '__main__':
    app.run(port=DevelopmentConfig.PORT)
