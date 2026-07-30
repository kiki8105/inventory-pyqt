import pymysql

DB_CONFIG = dict(
    host="localhost",
    user="root",
    password="0000",
    database="inventorydb",
    charset="utf8"
)

class DB:
    def __init__(self, **config):
        self.config = config

    def connect(self): 
        return pymysql.connect(**self.config)

# store_code/id/password 일치 여부로 로그인 검증
    def verify_user(self, store_code, id, password):  
        sql = "SELECT COUNT(*) FROM users WHERE store_code = %s AND id=%s AND password=%s"
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (store_code, id, password))
                count, = cur.fetchone()
                return count == 1

 # 점포 등록 여부 확인
    def store_exists(self, store_code): 
        sql = "SELECT COUNT(*) FROM Stores WHERE store_code = %s"
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (store_code,))
                count, = cur.fetchone()
                return count == 1

# 신규 점포 등록
    def create_store(self, store_code, name):  
        sql = "INSERT INTO Stores (store_code, Name) VALUES (%s, %s)"
        with self.connect() as conn:
            try:
                with conn.cursor() as cur:
                    cur.execute(sql, (store_code, name))
                conn.commit()
                return True
            except Exception:
                conn.rollback()
                return False

# 해당 점포에 등록된 계정 있는지 검증ㅇ
    def store_has_user(self, store_code):  
        sql = "SELECT COUNT(*) FROM users WHERE store_code = %s"
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (store_code,))
                count, = cur.fetchone()
                return count == 1

# 계정, 소속점포 삭제 (재고 있으면 외래키로 인해 안됨)
    def delete_user_and_store(self, store_code):  
        with self.connect() as conn:
            try:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM users WHERE store_code = %s", (store_code,))
                    cur.execute("DELETE FROM Stores WHERE store_code = %s", (store_code,))
                conn.commit()
                return True
            except Exception:
                conn.rollback()
                return False

# 아이디가 이미 등록되어 있는지 확인
    def id_exists(self, id):  
        sql = "SELECT COUNT(*) FROM users WHERE id = %s"
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (id,))
                count, = cur.fetchone()
                return count == 1

# 신규 사용자 등록 (id 중복 불가)
    def register_user(self, store_code, id, password):  
        sql = "INSERT INTO users (store_code, id, password) VALUES (%s, %s, %s)"
        with self.connect() as conn:
            try:
                with conn.cursor() as cur:
                    cur.execute(sql, (store_code, id, password))
                conn.commit()
                return True
            except Exception:
                conn.rollback()
                return False

    # 상품(Items) 전체 조회 (점포별)
    def fetch_items(self, store_code):
        sql = "SELECT Items_code, ProductCode, Name, Price, Number, MinStock, Stockdate, Expdate, Status FROM Items WHERE store_code = %s ORDER BY Items_code"
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (store_code,))
                return cur.fetchall() 
            # [(Items_code, ProductCode, Name, Price, Number, MinStock, Stockdate, Expdate, Status), ...]

    # 상품(Items) 추가 (Items_code는 자동 생성, 같은 ProductCode로 여러 배치 등록 가능)
    def insert_item(self, product_code, store_code, name, price, number, min_stock, stockdate, expdate, status):
        sql = "INSERT INTO Items (ProductCode, store_code, Name, Price, Number, MinStock, Stockdate, Expdate, Status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        with self.connect() as conn:
            try:
                with conn.cursor() as cur:
                    cur.execute(sql, (product_code, store_code, name, price, number, min_stock, stockdate, expdate, status))
                conn.commit()
                return True
            except Exception:
                conn.rollback()
                return False

    # 상품(Items) 단건 조회 (수정 폼 초기값용)
    def fetch_item(self, items_code):
        sql = "SELECT Items_code, ProductCode, Name, Price, Number, MinStock, Stockdate, Expdate, Status FROM Items WHERE Items_code = %s"
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (items_code,))
                return cur.fetchone()

    # 상품(Items) 수정 (일련번호는 고정, 나머지 항목만 갱신)
    def update_item(self, items_code, product_code, name, price, number, min_stock, stockdate, expdate, status):
        sql = "UPDATE Items SET ProductCode = %s, Name = %s, Price = %s, Number = %s, MinStock = %s, Stockdate = %s, Expdate = %s, Status = %s WHERE Items_code = %s"
        with self.connect() as conn:
            try:
                with conn.cursor() as cur:
                    cur.execute(sql, (product_code, name, price, number, min_stock, stockdate, expdate, status, items_code))
                conn.commit()
                return True
            except Exception:
                conn.rollback()
                return False

    # 상품(Items) 삭제 (일련번호 기준)
    def delete_item(self, items_code):
        sql = "DELETE FROM Items WHERE Items_code = %s"
        with self.connect() as conn:
            try:
                with conn.cursor() as cur:
                    cur.execute(sql, (items_code,))
                conn.commit()
                return True
            except Exception:
                conn.rollback()
                return False
            
    def stores(self):
            sql = "SELECT store_code, Name FROM Stores"
            with self.connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(sql)
                    return cur.fetchall()