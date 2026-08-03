-- DROP TABLE IF EXISTS Items;
-- DROP TABLE IF EXISTS users;
-- DROP TABLE IF EXISTS Stores;

CREATE TABLE Stores (
	store_code INT PRIMARY KEY,
    Name VARCHAR(50) NOT NULL
);

CREATE TABLE users (
	store_code INT PRIMARY KEY,
    id VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL,
    FOREIGN KEY (store_code)
        REFERENCES Stores(store_code)
);

CREATE TABLE Items (
	Items_code INT PRIMARY KEY AUTO_INCREMENT, -- 배치별 고유 일련번호 자동 생성되게
    ProductCode VARCHAR(50) NOT NULL, -- 상품 코드로 중복 가능 (동일 상품인데 유통기한 다르면 일련번호가 다르게 등록됨)
    store_code INT NOT NULL, -- 점포 코드
    Name VARCHAR(50) NOT NULL, -- 품명
    Price INT, -- 가격
    Number INT, -- 갯수
    MinStock INT, -- 적정재고
    Stockdate  DATETIME, -- 입고일
    Expdate DATETIME, -- 만료일
    Status BOOLEAN, -- 폐기, 훼손 등 상태
    FOREIGN KEY (store_code)
        REFERENCES Stores(store_code)
);

CREATE TABLE StockIn ( -- 입고 이력 (배치 하나에 여러 번 입고될 수 있음)
    id INT PRIMARY KEY AUTO_INCREMENT,
    Items_code INT NOT NULL, -- 어느 배치의 입고인지
    StockInDate DATETIME NOT NULL, -- 입고일시
    Quantity INT NOT NULL, -- 입고 수량
    FOREIGN KEY (Items_code)
        REFERENCES Items(Items_code)
);

CREATE TABLE Sales ( -- 판매(출고) 이력
    id INT PRIMARY KEY AUTO_INCREMENT,
    Items_code INT NOT NULL, -- 어느 배치에서 판매됐는지
    SaleDate DATETIME NOT NULL, -- 판매일시
    Quantity INT NOT NULL, -- 판매 수량
    Price INT NOT NULL, -- 판매 시점의 상품 가격 (매출 계산용)
    FOREIGN KEY (Items_code)
        REFERENCES Items(Items_code)
);

CREATE TABLE TrashItems ( -- 완전삭제된 상품 보관 (원래 Items_code 값을 그대로 유지, 외래키 없음)
    Items_code INT PRIMARY KEY,
    ProductCode VARCHAR(50),
    store_code INT,
    Name VARCHAR(50),
    Price INT,
    Number INT,
    MinStock INT,
    Stockdate DATETIME,
    Expdate DATETIME,
    Status BOOLEAN,
    DeletedAt DATETIME -- 삭제된 시각
);

CREATE TABLE TrashStockIn ( -- 완전삭제된 상품의 입고 이력 보관
    id INT PRIMARY KEY,
    Items_code INT,
    StockInDate DATETIME,
    Quantity INT
);

CREATE TABLE TrashSales ( -- 완전삭제된 상품의 판매 이력 보관
    id INT PRIMARY KEY,
    Items_code INT,
    SaleDate DATETIME,
    Quantity INT,
    Price INT
);

-- Stores 정보 입력
INSERT INTO Stores (store_code, Name) VALUES
(100001, '대전 둔산 직영점'),
(100002, '천안 신부동 직영점');

-- users 정보 입력
INSERT INTO users (store_code, id, password) VALUES(100001, 'rldnd8105', '1234');

-- Items 정보 입력 (Items_code는 자동 생성되므로 지정하지 않음)
INSERT INTO Items (ProductCode, store_code, Name, Price, Number, MinStock, Stockdate, Expdate, Status) VALUES
('10203', 100001, '꼬북칩', 2000, 1, 5, '2026-07-29', '2027-07-29', TRUE);