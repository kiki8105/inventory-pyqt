# claud.md

이 프로젝트에서 진행하는 모든 변경 사항을 기록하는 문서입니다.
새 요청을 시작하기 전에 이 문서를 먼저 읽고, 작업이 끝나면 반드시 이 문서에 변경 내용을 반영합니다.
불필요해진 코드는 주석 처리로 남기지 않고 삭제합니다.

## 프로젝트 구조 파악

- `app.py` : 실행 진입점. LoginDialog 실행 → 로그인 성공 시 Mainwindow(store_code) 실행
- `login_dialog.py` : 로그인 다이얼로그. 로그인 성공 시 `logged_in_store_code` 속성에 점포번호 저장
- `signup_dialog.py` : 회원가입 다이얼로그. 점포번호가 Stores에 없으면 점포명을 입력받아 신규 점포도 함께 등록
- `main.py` : 메인 윈도우. 재고 목록 테이블, 검색/필터, 등록/수정/삭제 UI, 입고일/판매일 이력 창 연결
- `edit_item_dialog.py` : 상품 수정 팝업 폼
- `history_dialog.py` : 입고/판매 이력 목록 + 등록 팝업 (mode="stockin" 또는 "sale"로 공용 사용)
- `db_helper.py` : 모든 DB 접근 로직 (pymysql 기반)
- `inventorydb.sql` : 스키마 및 초기 시드 데이터

## DB 스키마 (현재)

- `Stores(store_code PK, Name)`
- `users(store_code PK/FK->Stores, id UNIQUE, password)`
- `Items(Items_code PK AUTO_INCREMENT, ProductCode, store_code FK->Stores, Name, Price, Number, MinStock, Stockdate, Expdate, Status)`
  - `ProductCode`: 같은 상품이면 여러 배치(Items_code)에 재사용 가능 (반복 입고 시 배치별로 새 행 생성)
  - `Items_code`: 배치 단위 고유 일련번호, 자동 생성
  - `Number`/`Stockdate`: 등록 시 초기값이 들어가고, 이후 입고/판매 등록 시 `StockIn`/`Sales` 이력과 함께 자동 갱신됨 (직접 계산해서 넣지 않음)
- `StockIn(id PK AUTO_INCREMENT, Items_code FK->Items, StockInDate, Quantity)` : 배치 하나에 여러 번 입고 가능한 이력
- `Sales(id PK AUTO_INCREMENT, Items_code FK->Items, SaleDate, Quantity, Price)` : 판매(출고) 이력. `Price`는 판매 시점의 상품 가격을 그대로 저장 (매출 계산 기준)

## 핵심 동작 규칙

- **입고/판매 이력은 Items_code(배치) 단위**로 관리한다. 상품코드(ProductCode) 단위가 아님.
- 상품 등록(`add_item`) 시 입력한 초기 수량은 `Items.Number`에 반영되는 동시에 `StockIn`에도 첫 이력으로 자동 기록된다 (`db_helper.insert_item`이 한 트랜잭션에서 같이 처리).
- 추가 입고 등록(`HistoryDialog`, mode="stockin")은 `Items.Number`를 더하고, `Items.Stockdate`를 `LEAST(기존값, 새 입고일)`로 갱신한다 → 테이블에 표시되는 입고일은 항상 이력 중 가장 빠른 날짜.
- 판매 등록(mode="sale")은 현재 재고보다 많은 수량을 판매할 수 없도록 등록 전에 검증하고, 통과 시 `Items.Number`를 차감한다. 판매가는 사용자가 입력하지 않고 등록 시점의 `Items.Price`를 그대로 사용한다.
- 메인 테이블의 "판매일" 열은 해당 배치의 가장 최근 판매일(`MAX(Sales.SaleDate)`), 없으면 빈 값.
- "이번 달 매출" 라벨은 로그인한 점포의 이번 달(오늘 기준 연/월) `Sales` 합계(`Quantity x Price`)를 표시하며, 목록을 새로고침할 때마다 갱신된다.
- 입고일/판매일 셀을 더블클릭하면 `HistoryDialog`가 뜨고, 여기서 등록/조회한 내용은 다이얼로그가 닫히자마자 메인 목록에 자동 반영된다.
- **삭제는 두 종류다: "폐기"와 "완전삭제".**
  - 폐기(`dispose_item`/`dispose_selected_item`): Items 행은 남기고 `Number`만 0으로 만들며, 남은 수량만큼 `Sales`에 음수 수량으로 기록해서 재고자산/월매출/일매출에서 자동으로 차감되게 한다. 유통기한이 남아있고 판매가능 상태인 상품을 폐기하려 하면 한 번 더 확인 메시지를 띄운다.
  - 완전삭제(`hard_delete_item`/`hard_delete_selected_item`): Items 행과 그 `StockIn`/`Sales` 이력을 통째로 `TrashItems`/`TrashStockIn`/`TrashSales`에 복사한 뒤 원본에서 삭제한다. 이력이 있어도 항상 가능하다 (이력을 먼저 지우고 Items를 지우므로 외래키 제약에 안 걸림).
- **상품 등록 시 중복 자동 병합**: 상품코드+상품명+가격+만료일이 모두 기존 배치와 같으면, 새 행을 만들지 않고 그 배치에 입고(`add_stock_in`)로 처리한다 (`db_helper.find_matching_item`). 넷 중 하나라도 다르면 새 배치로 등록된다.

## 변경 이력

### 2026-07-30 이전 (기존 세션)
- DB/UI 기본 골격 구축: 회원가입/로그인, 점포별 재고 목록/등록/수정/삭제, 적정재고 기준 부족재고 표시+필터, 상품명·상품코드·가격 검색 필터, 재고자산 합계, 상품코드/일련번호 분리(배치별 관리), 입고일시 지원

### 2026-07-30 - AI TASK 반영
- `claud.md` 신설 및 변경 이력 관리 규칙 도입 (앞으로 작업 전 필독, 작업 후 갱신)
- DB에 `StockIn`(입고이력), `Sales`(판매이력) 테이블 추가 (`inventorydb.sql` + 실 DB 반영)
- `db_helper.py`: `fetch_stock_in_history`, `add_stock_in`, `fetch_sale_history`, `add_sale`, `fetch_monthly_revenue` 추가. `fetch_items`에 `LastSaleDate`(최근 판매일) 서브쿼리 컬럼 추가. `insert_item`이 신규 배치 등록 시 첫 입고 이력을 함께 생성하도록 변경, 반환값도 성공 여부(True/False)에서 생성된 `Items_code`(실패 시 None)로 변경
- `history_dialog.py` 신규 작성: 입고/판매 이력을 하나의 다이얼로그 클래스(mode 파라미터)로 공용 처리 — 이력 목록 표시 + 날짜/수량 입력 후 등록
- `main.py`: 테이블에 "판매일" 열 추가(11열), 입고일/판매일 셀 더블클릭 시 `HistoryDialog` 오픈, "이번 달 매출" 라벨 추가, `load_items`가 새 컬럼(LastSaleDate) 반영
- 정리: 이전에 주석 처리만 해두고 쓰지 않던 가격 범위 검색(`search_price_min/max`) 관련 코드를 전부 삭제 (주석 처리 대신 실제 삭제 원칙 적용)

### 2026-08-03
- "삭제"와 "폐기" 기능이 별도로 있었으나(삭제는 이력 있으면 차단, 폐기는 미완성) 로직이 겹쳐서 하나로 통합
- `db_helper.py`: `has_history`, `delete_item`, (미완성이던) `drop_item`을 제거하고 `dispose_item` 하나로 대체. 재고를 0으로 만들면서 남은 수량을 `Sales`에 음수 수량 이력으로 남겨 매출/재고자산에서 자동 차감되게 함
- `main.py`: `delete_selected_item`/`drop_selected_item`을 `dispose_selected_item` 하나로 통합. 버튼도 "삭제"+"폐기" 2개에서 "폐기" 1개로 축소. 유통기한이 남아있고 판매가능한 상품을 폐기하려 하면 별도 확인 메시지로 한 번 더 경고
- "판매 가능한 상품만 보기" 체크박스(`chk_sellable_only`) 추가, 유통기한 임박(만료일 지남) 행 배경색 강조(`SHORT_DATE_COLOR`) 추가, 만료일 지났거나 상태가 판매불가면 "판매불가"로 표시하도록 `status_text` 계산 로직 반영
- 상품 등록 폼을 `QVBoxLayout`에서 `QGridLayout`으로 변경해 필드를 2열로 배치 (상품코드|상품명, 재고|적정재고, 가격, 입고일|만료일, 상태)
- 재고가 0개가 되면 상태를 자동으로 판매불가로 전환 (`db_helper.disable_zero_stock_items`, `load_items` 맨 앞에서 호출해 같은 새로고침에 바로 반영)
- DB에 `TrashItems`/`TrashStockIn`/`TrashSales` 테이블 추가 (`inventorydb.sql` + 실 DB 반영) — 완전삭제된 상품/이력 보관용, 외래키 없음
- `db_helper.py`: `find_matching_item`(상품코드+이름+가격+만료일 일치하는 기존 배치 조회), `hard_delete_item`(이력까지 휴지통으로 이동 후 완전삭제) 추가
- `main.py`: `add_item`이 등록 전에 `find_matching_item`으로 중복 여부를 확인해 일치하면 `add_stock_in`으로 처리하도록 변경. "완전삭제" 버튼/`hard_delete_selected_item` 추가 (폐기와 별개로 항상 사용 가능)
