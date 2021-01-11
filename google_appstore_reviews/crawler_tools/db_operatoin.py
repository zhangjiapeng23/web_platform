import pymysql
import threading

class CrawlerDb:
    sql_insert_info = "insert into google_appstore_reviews_reviewinfo(review_id, author, platform, country)" \
                      " values (%s,%s,%s,%s)"
    sql_insert_detail = "insert into google_appstore_reviews_reviewdetail(review_info_id, title, content, rating," \
                        " version, create_time) values (%s,%s,%s,%s,%s,%s)"
    sql_select = "select nid from google_appstore_reviews_reviewinfo where review_id=%s"


    def __init__(self):
        self.conn = pymysql.connect(host='localhost', port=3306, user='root', password='lb15116188571j',
                                    db='web_platform', charset='utf8mb4')
        self.cursor = self.conn.cursor()

    def __str__(self):
        return 'db: web_platform'

    def insert_data_to_reviewinfo(self, data_info: tuple):
        try:
            self.cursor.execute(self.sql_insert_info, data_info)
        except pymysql.err.IntegrityError:
            return None
        else:
            self.cursor.execute(self.sql_select, data_info[0])
            nid = self.cursor.fetchone()[0]
            return nid

    def insert_data_to_reviewdetail(self, data_detail: tuple):
        self.cursor.execute(self.sql_insert_detail, data_detail)

    def commit(self):
        self.conn.commit()

    def cursor_close(self):
        self.cursor.close()

    def conn_colse(self):
        self.conn.close()



if __name__ == '__main__':

    data_info1 = ('31111', 'james', 0, 'us')
    data_info2 = ('4111', 'test', 1, 'au')
    data_info3 = ('31111', 'james2', 4, 'ch')
    data_total = [data_info1, data_info2, data_info3]

    t1 = threading.Thread(target=test, args=(data_total,))
    t2 = threading.Thread(target=test, args=(data_total,))

    t1.start()
    t2.start()
    t1.join()
    t2.join()







