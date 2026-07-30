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

-- Stores 정보 입력
INSERT INTO Stores (store_code, Name) VALUES
(100001, '대전 둔산 직영점'),
(100002, '천안 신부동 직영점');

-- users 정보 입력
INSERT INTO users (store_code, id, password) VALUES(100001, 'rldnd8105', '1234');

-- Items 정보 입력 (Items_code는 자동 생성되므로 지정하지 않음)
INSERT INTO Items (ProductCode, store_code, Name, Price, Number, MinStock, Stockdate, Expdate, Status) VALUES
('10203', 100001, '꼬북칩', 2000, 1, 5, '2026-07-29', '2027-07-29', TRUE);