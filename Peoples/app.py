from flask import Flask, render_template, abort
import faker


app = Flask(__name__)
fake = faker.Faker('ru_RU')


def create_files():
    with open('./Peoples/files/humans.txt', 'w', encoding='utf-8') as humans_f:
        for i in range(10):
            fio = fake.name()
            new_fio = fio.replace(' ', ',')
            print(new_fio, file=humans_f)
    with open('./Peoples/files/names.txt', 'w', encoding='utf-8') as names_f:
        for i in range(10):
            name = fake.first_name()
            print(name, file=names_f)
    with open('./Peoples/files/users.txt', 'w', encoding='utf-8') as users_f:
        for i in range(10):
            profile = fake.simple_profile()
            for element in profile:
                print(profile[element], end=';', file=users_f)
            print(file=users_f)   


@app.route("/")
def hello():
    return render_template('index.html')


@app.route('/names')
def get_names():
    names = []
    with open('./files/names.txt', encoding='utf-8') as f:
        for raw_line in f:
            names.append(raw_line.strip())
    return render_template('names.html', people_names=names)


@app.route('/table')
def get_table():
    datas = []
    with open('./files/humans.txt', encoding='utf-8') as f:
        keys = ['surname', 'name', 'middle_name']
        for raw_line in f:
            data = raw_line.strip().split(',')
            element = {}
            for i in range(len(data)):
                element[keys[i]] = data[i]
            datas.append(element)
    return render_template('table.html', people_datas=datas)


@app.route('/users')
def get_users_list():
    datas = []
    with open('./files/users.txt', encoding='utf-8') as f:
        for raw_line in f:
            data = raw_line.strip().split(';')
            fio = data[1].split()
            surname = fio[0]
            name = fio[1]
            middle_name = fio[2]
            birth_date = data[5].split('-')     # делаю красивую дату
            birth_date.reverse()                # делаю красивую дату
            birth_date = '.'.join(birth_date)   # делаю красивую дату
            datas.append({'login': data[0], 'surname': surname,
                          'name': name, 'middle_name': middle_name,
                          'birth_date': birth_date, 'email': data[4]})
    return render_template('users_list.html', users_datas=datas)


@app.route("/users/<login>")
def get_user_info(login):
    element = None
    with open('./files/users.txt', encoding='utf-8') as f:
        for raw_line in f:
            data = raw_line.strip().split(';')
            if data[0] == login:
                fio = data[1].split()
                surname = fio[0]
                name = fio[1]
                middle_name = fio[2]
                birth_date = data[5].split('-')     # делаю красивую дату
                birth_date.reverse()                # делаю красивую дату
                birth_date = '.'.join(birth_date)   # делаю красивую дату
                element = {'login': data[0], 'surname': surname,
                           'name': name, 'middle_name': middle_name,
                           'birth_date': birth_date, 'email': data[4]}
                break
    if element is None:
        abort(404)
    return render_template('user_info.html', user_info=element)


if __name__ == '__main__':
    # create_files()
    app.run(debug=True)

    
