import requests
import pandas
import threading
import datetime
import os

url_r = '' # глобальная переменная с url адресом устройства

list_item = [] # список отсканированных данных
# получаем настройки из файла кофигурации config.txt
def getConfig(): 
    config_name = 'config.txt'
    global url_r # глобальная переменная с url адресом устройства
    # считываем настройки
    if os.path.exists(config_name): 
        print('Настройки применены!')
        url = open(config_name, 'r')
        url_r = url.read()
    else:
        print('Файл config.txt отсутсвует или неверно наименование файла.\nСоздайте файл и пропишите в нем url устройства')
        quit()

# сохраняем результаты сканирования
def save(list_item):
    data_file = datetime.datetime.today().strftime("%Y.%m.%d-%H.%M.%S") # текущая дата и время файла
    try:
        data = pandas.DataFrame(list_item)
        name_file = 'scancode-' + str(data_file) + '.csv'
        data.to_csv(name_file, sep=';', index=False)
        print('Данные измерений сохранены в файле ' + name_file)
    except Exception:
        print('Не удалось сохранить данные!\n' + Exception)

# получаем данные json
def scan(flag, interval=1):
    count_default = '' # счетчик сканирования
    
    while not flag.wait(interval):
        req = requests.get(url_r) # подключаемся к серверу
        info_scan = req.json() # вытягиваем данные
        count = info_scan.get('uniqueIndex') # вытягиваем id сканирования
        data = datetime.datetime.today().strftime("%Y.%m.%d-%H.%M.%S") # текущая дата и время
        data_time = {'datatime': data} # словарь с датой

        # проверка на уникальность сканирования
        if 'uniqueIndex' in info_scan and count != count_default:
            count_default = count
            print('Считывние габаритов №' + str(count) + ':')

            # выводим в консоль данные каждого сканирования
            for key, value in info_scan.items():
                print(f'{key}: {value}')

            info_scan.update(data_time) # добавляем дату к каждому сканированию
            list_item.append(info_scan) # создаем список со всеми проведенными сканированиями
            print('\n')
    


def main():
    getConfig()
    status = requests.get(url_r)
    if status.status_code == 200:
        flag = threading.Event()
        threading.Thread(target=scan, args=[flag], daemon=True).start()
        input('После сканирования нажмите Enter\n')
        flag.set()
        save(list_item)
    else:
        print('Сайт недоступен')

if __name__ == "__main__":
    main()