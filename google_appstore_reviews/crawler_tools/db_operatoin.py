import pymysql

from mobile_QA_web_platform.settings.dev import DATABASES


class CrawlerDb:
    sql_insert_info = "insert into google_appstore_reviews_reviewinfo(project_name_id, review_id, author, platform, country)" \
                      " values (%s,%s,%s,%s,%s)"
    sql_insert_detail = "insert into google_appstore_reviews_reviewdetail(review_info_id, title, content, rating," \
                        " version, create_time) values (%s,%s,%s,%s,%s,%s)"
    sql_select = "select nid from google_appstore_reviews_reviewinfo where review_id=%s"

    sql_select_project = "select * from google_appstore_reviews_project"

    def __init__(self):
        self.__db = DATABASES.get('default')
        self.__host = self.__db.get('HOST')
        self.__port = self.__db.get('PORT')
        self.__user = self.__db.get('USER')
        self.__password = self.__db.get('PASSWORD')
        self.__db_name = self.__db.get('NAME')
        self.conn = pymysql.connect(host=self.__host, port=self.__port, user=self.__user, password=self.__password,
                                    db=self.__db_name, charset='utf8mb4')
        self.cursor = self.conn.cursor(cursor=pymysql.cursors.DictCursor)

    def __str__(self):
        return 'db: web_platform'

    def insert_data_to_reviewinfo(self, data_info: tuple):
        try:
            self.cursor.execute(self.sql_insert_info, data_info)
        # except pymysql.err.IntegrityError:
        except Exception as e:
            print(e)
            return None
        else:
            self.cursor.execute(self.sql_select, data_info[1])
            nid = self.cursor.fetchone()['nid']
            return nid

    def insert_data_to_reviewdetail(self, data_detail: tuple):
        self.cursor.execute(self.sql_insert_detail, data_detail)

    def get_project_list(self):
        self.cursor.execute(self.sql_select_project)
        project_list = self.cursor.fetchall()
        return project_list

    def commit(self):
        self.conn.commit()

    def cursor_close(self):
        self.cursor.close()

    def conn_close(self):
        self.conn.close()



if __name__ == '__main__':
    db = CrawlerDb()
    res = db.get_project_list()
    print(res)
