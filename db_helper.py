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

    # 상품 전체 조회 (점포별). 마지막 판매일(LastSaleDate)은 판매 이력이 없으면 NULL
    def fetch_items(self, store_code):
        sql = """
            SELECT Items_code, ProductCode, Name, Price, Number, MinStock, Stockdate, Expdate, Status,
                   (SELECT MAX(SaleDate) FROM Sales WHERE Sales.Items_code = Items.Items_code) AS LastSaleDate
            FROM Items WHERE store_code = %s ORDER BY Items_code
        """
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (store_code,))
                return cur.fetchall()
            # [(Items_code, ProductCode, Name, Price, Number, MinStock, Stockdate, Expdate, Status, LastSaleDate), ...]

    # 상품 추가 (Items_code는 자동 생성, 같은 ProductCode로 여러 배치 등록 가능)
    def insert_item(self, product_code, store_code, name, price, number, min_stock, stockdate, expdate, status):
        sql = "INSERT INTO Items (ProductCode, store_code, Name, Price, Number, MinStock, Stockdate, Expdate, Status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        with self.connect() as conn:
            try:
                with conn.cursor() as cur:
                    cur.execute(sql, (product_code, store_code, name, price, number, min_stock, stockdate, expdate, status))
                    new_items_code = cur.lastrowid
                    if number:  # 등록 시 입력한 초기 수량을 첫 입고 이력으로도 남김
                        cur.execute(
                            "INSERT INTO StockIn (Items_code, StockInDate, Quantity) VALUES (%s, %s, %s)",
                            (new_items_code, stockdate, number)
                        )
                conn.commit()
                return new_items_code
            except Exception:
                conn.rollback()
                return None

    # 상품 단건 조회
    def fetch_item(self, items_code):
        sql = "SELECT Items_code, ProductCode, Name, Price, Number, MinStock, Stockdate, Expdate, Status FROM Items WHERE Items_code = %s"
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (items_code,))
                return cur.fetchone()

    # 상품 수정 (일련번호는 고정, 나머지 항목만 갱신)
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

    # 상품 폐기: 남은 재고를 이번 달 매출에서 마이너스로 차감, 재고를 0으로
    def dispose_item(self, items_code):
        with self.connect() as conn:
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT Number, Price FROM Items WHERE Items_code = %s", (items_code,))
                    number, price = cur.fetchone()
                    if number:
                        cur.execute(
                            "INSERT INTO Sales (Items_code, SaleDate, Quantity, Price) VALUES (%s, NOW(), %s, %s)",
                            (items_code, -number, price)
                        )
                    cur.execute("UPDATE Items SET Number = 0 WHERE Items_code = %s", (items_code,))
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

    # 입고 이력 조회 (해당 배치의 입고 기록 전체)
    def fetch_stock_in_history(self, items_code):
        sql = "SELECT StockInDate, Quantity FROM StockIn WHERE Items_code = %s ORDER BY StockInDate"
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (items_code,))
                return cur.fetchall()

    # 입고 등록: 이력 추가 + 재고 수량 증가 + 입고일을 이력 중 가장 빠른 날짜로 갱신
    def add_stock_in(self, items_code, stock_in_date, quantity):
        with self.connect() as conn:
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO StockIn (Items_code, StockInDate, Quantity) VALUES (%s, %s, %s)",
                        (items_code, stock_in_date, quantity)
                    )
                    cur.execute(
                        "UPDATE Items SET Number = Number + %s, Stockdate = LEAST(Stockdate, %s) WHERE Items_code = %s",
                        (quantity, stock_in_date, items_code)
                    )
                conn.commit()
                return True
            except Exception:
                conn.rollback()
                return False

    # 판매 이력 조회 (해당 배치의 판매 기록 전체)
    def fetch_sale_history(self, items_code):
        sql = "SELECT SaleDate, Quantity, Price FROM Sales WHERE Items_code = %s ORDER BY SaleDate"
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (items_code,))
                return cur.fetchall()

    # 판매 등록: 이력 추가 + 재고 수량 감소 (재고 부족 여부는 호출하는 쪽에서 미리 검증)
    def add_sale(self, items_code, sale_date, quantity, price):
        with self.connect() as conn:
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO Sales (Items_code, SaleDate, Quantity, Price) VALUES (%s, %s, %s, %s)",
                        (items_code, sale_date, quantity, price)
                    )
                    cur.execute(
                        "UPDATE Items SET Number = Number - %s WHERE Items_code = %s",
                        (quantity, items_code)
                    )
                conn.commit()
                return True
            except Exception:
                conn.rollback()
                return False

    # 해당 점포의 이번 달 매출 (판매 시점 가격 x 수량 합계)
    def fetch_monthly_revenue(self, store_code, year, month):
        sql = """
            SELECT COALESCE(SUM(Sales.Quantity * Sales.Price), 0)
            FROM Sales
            JOIN Items ON Sales.Items_code = Items.Items_code
            WHERE Items.store_code = %s AND YEAR(Sales.SaleDate) = %s AND MONTH(Sales.SaleDate) = %s
        """
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (store_code, year, month))
                total, = cur.fetchone()
                return total


    def fetch_daily_revenue(self, store_code, year, month, day):
        sql = """
            SELECT COALESCE(SUM(Sales.Quantity * Sales.Price), 0)
            FROM Sales
            JOIN Items ON Sales.Items_code = Items.Items_code
            WHERE Items.store_code = %s AND YEAR(Sales.SaleDate) = %s AND MONTH(Sales.SaleDate) = %s AND DAY(Sales.SaleDate) = %s
        """
        with self. connect() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (store_code, year, month, day))
                total, = cur.fetchone()
                return total