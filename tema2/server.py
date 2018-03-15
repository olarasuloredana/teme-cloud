import http.server
import sqlite3
import json

class MyServer(http.server.BaseHTTPRequestHandler):
    def set_headers(self, code, size):
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Content-Length', size)
        self.end_headers()

    def send_json(self, result):
        try:
            result_json = json.dumps(result)
        except:
            self.send_error(500, explain = "Eroare la codificarea json!")
        else:
            size = len(result_json.encode())
            self.set_headers(200, size)
            self.wfile.write(result_json.encode())

    def get_colectie(self, colectie):
        c.execute("SELECT * FROM " + colectie)
        result = c.fetchall()
        if len(result) == 0:
            self.send_error(404, explain='Colectia e goala!!')
        else:
            self.send_json(result)
        

    def get_item(self, colectie, item):
        cmd = "SELECT * FROM " + colectie

        # try:
        #     row_id = int(item)
        # except:
        #     try:
        #         c.execute(cmd + " WHERE replace(lower(nume), ' ', '') = ?", (item,))
        #     except:
        #         self.send_error(500, explain = "Coloana nume nu exista in colectia data!")
        #     else:
        #         result = c.fetchall()
        #         if len(result) == 0:
        #             self.send_error(404, explain='Itemul nu exista!!')
        #         else:
        #             self.send_json(result)
        
        try:
            c.execute(cmd + " WHERE id = ?", (item,))
        except:
            self.send_error(500, explain = "Coloana id nu exista in colectia data!")
        else:
            result = c.fetchall()
            if len(result) == 0:
                self.send_error(404, explain='Itemul nu exista!!')
            else:
                self.send_json(result)

    def do_GET(self):
        self.path = self.path[1:]
        if len(self.path) > 0:
            if self.path[-1] == '/':
                self.path = self.path[:-1]
        commands = self.path.split('/')

        if (len(commands) == 1 or len(commands) == 2) and commands[0] != '':
            colectie = commands[0].lower()
            c.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (colectie,))
            rows = c.fetchall()
            if len(rows) == 0:
                mesaj = 'Colectia %s nu exista!!' % colectie
                self.send_error(404, explain=mesaj)

            elif len(commands) == 1 or commands[1] == '':
                self.get_colectie(colectie)
            else:
                self.get_item(colectie, commands[1].lower())

        else:
            self.send_error(400, explain="Nu ati introdus un url corect! Folositi variantele:  /colectie    sau    /colectie/item")


    def delete_colectie(self, colectie):
        c.execute("DELETE FROM " + colectie)
        conn.commit()
        result = {"raspuns": "Colectia " + colectie + " a fost stearsa."}
        self.send_json(result)

    def delete_item(self, colectie, item):
        cmd = "SELECT * FROM " + colectie
        try:
            c.execute(cmd + " WHERE id = ?", (item,))
        except:
            self.send_error(500, explain = "Coloana id nu exista in colectia data!")
        else:
            result = c.fetchall()
            if len(result) == 0:
                self.send_error(404, explain='Itemul nu exista!!')
                return

        cmd = "DELETE FROM " + colectie

        # try:
        #     row_id = int(item)
        # except:
        #     try:
        #         c.execute(cmd + " WHERE replace(lower(nume), ' ', '') = ?", (item,))
        #         conn.commit()
        #     except:
        #         self.send_error(500, explain = "Coloana nume nu exista in colectia data!")
        #     else:
        #         if conn.total_changes == 0:
        #             self.send_error(404, explain='Itemul nu exista!!')
        #         else:
        #             result = {"raspuns": "Itemul a fost sters."}
        #             self.send_json(result)
        # else:
        try:
            c.execute(cmd + " WHERE id = ?", (item,))
            conn.commit()
        except:
            self.send_error(500, explain = "Coloana id nu exista in colectia data!")
        else:
            if conn.total_changes == 0:
                self.send_error(404, explain='Itemul nu exista!!')
            else:
                result = {"raspuns": "Itemul a fost sters."}
                self.send_json(result)

    def do_DELETE(self):
        self.path = self.path[1:]
        if len(self.path) > 0:
            if self.path[-1] == '/':
                self.path = self.path[:-1]
        commands = self.path.split('/')

        if (len(commands) == 1 or len(commands) == 2) and commands[0] != '':
            colectie = commands[0].lower()
            c.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (colectie,))
            rows = c.fetchall()
            if len(rows) == 0:
                mesaj = 'Colectia %s nu exista!!' % colectie
                self.send_error(404, explain=mesaj)

            elif len(commands) == 1 or commands[1] == '':
                self.delete_colectie(colectie)
            else:
                self.delete_item(colectie, commands[1].lower())

        else:
            self.send_error(400, explain="Nu ati introdus un url corect! Folositi variantele:  /colectie    sau    /colectie/item")
        
    
    def suprascrie_sau_creeaza_colectie(self, colectie):
        content_length = int(self.headers['Content-Length'])
        content_type = self.headers['Content-type']

        if content_type != 'application/json':
            self.send_error(400, explain="Nu ati introdus un json!")
        else:
            put_data = self.rfile.read(content_length)
            try:
                put_json = json.loads(put_data.decode())
            except:
                self.send_error(400, explain="Nu ati introdus un json corect!")
            else:

                if type(put_json) != list:
                    self.send_error(400, explain="Nu ati introdus o lista de intrari!")
                else:
                    if len(put_json) == 0:
                        self.send_error(400, explain="Ati introdus o lista goala!")
                        return

                    columns = put_json[0].keys()
                    print(columns)
                    for i in range(1, len(put_json)):
                        if put_json[i].keys() != columns:
                            self.send_error(400, explain="Coloanele nu sunt la fel pentru toate intrarile!")
                            return

                    if 'id' not in columns:
                        self.send_error(400, explain="Coloana id este obligatorie!")
                        return

                    c.execute("DROP TABLE IF EXISTS " + colectie)
                    
                    cmd = "CREATE TABLE " + colectie + " ("
                    columns = list(columns)
                    for column in columns[:-1]:
                        if type(put_json[0][column]) == int or type(put_json[0][column]) == float:
                            cmd += column + " real, "
                        else:
                            cmd += column + " text, "
                    if type(put_json[0][columns[-1]]) == int or type(put_json[0][columns[-1]]) == float:
                        cmd += columns[-1] + " real) "
                    else:
                        cmd += columns[-1] + " text) "

                    print(cmd)
                    try:
                        c.execute(cmd)
                        conn.commit()
                    except:
                        self.send_error(400, explain="Tabelul nu a putut fi creat!")
                    else:
                        for entry in put_json:
                            cmd = "INSERT INTO " + colectie + " VALUES("
                            for column in columns[:-1]:
                                if type(entry[column]) == str:
                                    cmd += "'" + entry[column] + "'"
                                else:
                                    cmd += str(entry[column])
                                cmd += ','

                            if type(entry[columns[-1]]) == str:
                                cmd += "'" + entry[columns[-1]] + "'"
                            else:
                                cmd += str(entry[columns[-1]])
                            cmd += ')'

                            print(cmd)
                            try:
                                c.execute(cmd)
                            except:
                                self.send_error(400, explain="Nu s-a putut insera in tabel!")
                                return

                        conn.commit()
                        result = {"raspuns": "Colectia a fost adaugata/suprascrisa."}
                        self.send_json(result)

    def put_item(self, colectie, item):
        content_length = int(self.headers['Content-Length'])
        content_type = self.headers['Content-type']

        if content_type != 'application/json':
            self.send_error(400, explain="Nu ati introdus un json!")
        else:
            put_data = self.rfile.read(content_length)
            try:
                put_json = json.loads(put_data.decode())
            except:
                self.send_error(400, explain="Nu ati introdus un json corect!")
            else:

                if type(put_json) != dict:
                    self.send_error(400, explain="Nu ati introdus un dictionar!")
                else:
                    if len(put_json) == 0:
                        self.send_error(400, explain="Ati introdus o intrare goala!")
                        return

                    c.execute("select * from " + colectie + " where 1=0")
                    columns = [d[0] for d in c.description]
                    columns_entered = list(put_json.keys())
                    if sorted(columns) != sorted(columns_entered):
                        self.send_error(400, explain="Nu ati introdus toate coloanele!")
                        return

                    if item != str(put_json['id']):
                        self.send_error(400, explain="Id-ul nu corespunde!")
                        return

                    column_list = '('
                    values_list = '('
                    for column in columns[:-1]:
                        column_list += column + ','
                        if type(put_json[column]) == str:
                            values_list += "'" + put_json[column] + "',"
                        else:
                            values_list += str(put_json[column]) + ","
                
                    column_list += columns[-1] + ')'
                    if type(put_json[columns[-1]]) == str:
                        values_list += "'" + put_json[columns[-1]] + "')"
                    else:
                        values_list += str(put_json[columns[-1]]) + ')'
                    cmd = "REPLACE into " + colectie + column_list + " VALUES " + values_list
                    try:
                        c.execute(cmd)
                        conn.commit()
                    except:
                        self.send_error(400, explain="Nu s-a putut adauga/suprascrie obiectul!")
                        return

                    result = {"raspuns": "Itemul a fost adaugat/suprascris."}
                    self.send_json(result)


    def do_PUT(self):
        self.path = self.path[1:]
        if len(self.path) > 0:
            if self.path[-1] == '/':
                self.path = self.path[:-1]
        commands = self.path.split('/')

        if (len(commands) == 1 or len(commands) == 2) and commands[0] != '':
            colectie = commands[0].lower()

            if len(commands) == 1 or commands[1] == '':
                self.suprascrie_sau_creeaza_colectie(colectie)
            else:
                c.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (colectie,))
                rows = c.fetchall()
                if len(rows) == 0:
                    mesaj = 'Colectia %s nu exista!!' % colectie
                    self.send_error(404, explain=mesaj)
                else:
                    self.put_item(colectie, commands[1])

        else:
            self.send_error(400, explain="Nu ati introdus un url corect! Folositi variantele:  /colectie    sau    /colectie/item")


    def post_colectie(self, colectie):
        content_length = int(self.headers['Content-Length'])
        content_type = self.headers['Content-type']

        if content_type != 'application/json':
            self.send_error(400, explain="Nu ati introdus un json!")
        else:
            post_data = self.rfile.read(content_length)
            try:
                post_json = json.loads(post_data.decode())
            except:
                self.send_error(400, explain="Nu ati introdus un json corect!")
            else:

                if type(post_json) != dict:
                    self.send_error(400, explain="Nu ati introdus un dictionar!")
                else:
                    if len(post_json) == 0:
                        self.send_error(400, explain="Ati introdus o intrare goala!")
                        return

                    c.execute("select * from " + colectie + " where 1=0")
                    columns = [d[0] for d in c.description]
                    columns_entered = list(post_json.keys())
                    if sorted(columns) != sorted(columns_entered):
                        self.send_error(400, explain="Nu ati introdus toate coloanele!")
                        return

                    cmd = "SELECT * FROM " + colectie
                    try:
                        c.execute(cmd + " WHERE id = ?", (str(post_json['id']),))
                    except:
                        self.send_error(500, explain = "Coloana id nu exista in colectia data!")
                    else:
                        result = c.fetchall()
                        if len(result) != 0:
                            self.send_error(409, explain='Itemul cu id-ul dat deja exista!!')
                            return

                    column_list = '('
                    values_list = '('
                    for column in columns[:-1]:
                        column_list += column + ','
                        if type(post_json[column]) == str:
                            values_list += "'" + post_json[column] + "',"
                        else:
                            values_list += str(post_json[column]) + ","
                
                    column_list += columns[-1] + ')'
                    if type(post_json[columns[-1]]) == str:
                        values_list += "'" + post_json[columns[-1]] + "')"
                    else:
                        values_list += str(post_json[columns[-1]]) + ')'
                    cmd = "INSERT into " + colectie + column_list + " VALUES " + values_list
                    #try:
                    c.execute(cmd)
                    conn.commit()
                    #except:
                    #    self.send_error(400, explain="Nu s-a putut adauga obiectul!")
                    #    return

                    result = {"raspuns": "Itemul cu id-ul " + str(post_json['id']) + " a fost adaugat."}
                    self.send_json(result)


    def post_item(self, colectie, item):
        # content_length = int(self.headers['Content-Length'])
        # content_type = self.headers['Content-type']

        # if content_type != 'application/json':
        #     self.send_error(400, explain="Nu ati introdus un json!")
        # else:
        #     post_data = self.rfile.read(content_length)
        #     try:
        #         post_json = json.loads(post_data.decode())
        #     except:
        #         self.send_error(400, explain="Nu ati introdus un json corect!")
        #     else:

        #         if type(post_json) != dict:
        #             self.send_error(400, explain="Nu ati introdus un dictionar!")
        #         else:
        #             if len(post_json) == 0:
        #                 self.send_error(400, explain="Ati introdus o intrare goala!")
        #                 return


        #             cmd = "SELECT * FROM " + colectie
        #             try:
        #                 c.execute(cmd + " WHERE id = ?", (item,))
        #             except:
        #                 self.send_error(500, explain = "Coloana id nu exista in colectia data!")
        #             else:
        #                 result = c.fetchall()
        #                 if len(result) == 0:
        #                     self.send_error(404, explain='Itemul cu id-ul dat nu exista!!')
        #                     return

        #             columns = list(post_json.keys())

        #             cmd = "UPDATE " + colectie + " SET "

        #             for column in columns[:-1]:
        #                 cmd += column + "="
        #                 if type(post_json[column]) == str:
        #                     cmd += "'" + post_json[column] + "',"
        #                 else:
        #                     cmd += str(post_json[column]) + ","
                
        #             cmd += columns[-1] + "="
        #             if type(post_json[columns[-1]]) == str:
        #                 cmd += "'" + post_json[columns[-1]] + "'"
        #             else:
        #                 cmd += str(post_json[columns[-1]])
                    
        #             cmd += " WHERE id = " + item

        #             try:
        #                 c.execute(cmd)
        #                 conn.commit()
        #             except:
        #                 self.send_error(400, explain="Nu s-a putut updata obiectul!")
        #                 return

        #             result = {"raspuns": "Itemul cu id-ul " + item + " a fost updatat."}
        #             self.send_json(result)

        self.send_error(400, explain="Post pentru item nu exista!")


    def do_POST(self):
        self.path = self.path[1:]
        if len(self.path) > 0:
            if self.path[-1] == '/':
                self.path = self.path[:-1]
        commands = self.path.split('/')

        if (len(commands) == 1 or len(commands) == 2) and commands[0] != '':
            colectie = commands[0].lower()
            c.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (colectie,))
            rows = c.fetchall()
            if len(rows) == 0:
                mesaj = 'Colectia %s nu exista!!' % colectie
                self.send_error(404, explain=mesaj)

            elif len(commands) == 1 or commands[1] == '':
                self.post_colectie(colectie)
            else:
                self.post_item(colectie, commands[1])

        else:
            self.send_error(400, explain="Nu ati introdus un url corect! Folositi variantele:  /colectie    sau    /colectie/item")
        
        
def run():
    server_address = ('', 8000)
    my_server = http.server.HTTPServer(server_address, MyServer)
    print('Starting server...')
    try:
        my_server.serve_forever()
    except KeyboardInterrupt:
        print('Stopping server...')
        conn.close()

def dict_factory(cursor, row):
    d = {}
    for index, coloana in enumerate(cursor.description):
        d[coloana[0]] = row[index]
    return d


conn = sqlite3.connect('tema2.db')
conn.row_factory = dict_factory
c = conn.cursor()


run()
