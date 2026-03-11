-- CH08 통합 에이전트 — 커넥트HR 데이터베이스 스키마
-- CH04와 동일한 스키마 구조를 사용합니다.
-- docker-compose up -d 로 자동 실행됩니다.

-- ============================================================
-- 기존 테이블 초기화
-- ============================================================

DROP TABLE IF EXISTS sales_monthly CASCADE;
DROP TABLE IF EXISTS leave_balance CASCADE;
DROP TABLE IF EXISTS leave_requests CASCADE;
DROP TABLE IF EXISTS employees CASCADE;

-- ============================================================
-- 테이블 생성
-- ============================================================

-- 직원 테이블
CREATE TABLE employees (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(50)  NOT NULL,
    department  VARCHAR(50)  NOT NULL,
    position    VARCHAR(50)  NOT NULL,
    hire_date   DATE         NOT NULL,
    base_salary NUMERIC(12, 0) NOT NULL,
    email       VARCHAR(100) UNIQUE NOT NULL,
    is_active   BOOLEAN      NOT NULL DEFAULT TRUE
);

-- 연차 잔액 테이블
CREATE TABLE leave_balance (
    id          SERIAL PRIMARY KEY,
    employee_id INTEGER      NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    year        INTEGER      NOT NULL,
    total_days  INTEGER      NOT NULL DEFAULT 15,
    used_days   INTEGER      NOT NULL DEFAULT 0,
    UNIQUE (employee_id, year)
);

-- 연차 신청 테이블
CREATE TABLE leave_requests (
    id          SERIAL PRIMARY KEY,
    employee_id INTEGER      NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    start_date  DATE         NOT NULL,
    end_date    DATE         NOT NULL,
    reason      TEXT,
    status      VARCHAR(20)  NOT NULL DEFAULT 'pending'  -- pending / approved / rejected
);

-- 월별 매출 테이블
CREATE TABLE sales_monthly (
    id          SERIAL PRIMARY KEY,
    department  VARCHAR(50)  NOT NULL,
    year        INTEGER      NOT NULL,
    month       INTEGER      NOT NULL CHECK (month BETWEEN 1 AND 12),
    revenue     NUMERIC(15, 0) NOT NULL DEFAULT 0,
    target      NUMERIC(15, 0),
    UNIQUE (department, year, month)
);

-- ============================================================
-- 샘플 데이터 삽입
-- ============================================================

-- 직원 데이터
INSERT INTO employees (name, department, position, hire_date, base_salary, email) VALUES
    ('김도현',  '개발팀',  '팀장',  '2020-03-02', 6500000, 'dohyun.kim@connecthr.io'),
    ('이서연',  '개발팀',  '개발자', '2023-01-16', 3800000, 'seoyeon.lee@connecthr.io'),
    ('박민준',  '데이터팀', '과장',  '2021-07-05', 5200000, 'minjun.park@connecthr.io'),
    ('최지은',  '영업팀',  '팀장',  '2019-09-01', 6200000, 'jieun.choi@connecthr.io'),
    ('정다희',  '인사팀',  '사원',  '2024-02-20', 3500000, 'dahee.jung@connecthr.io'),
    ('한재원',  '개발팀',  '개발자', '2022-06-13', 4300000, 'jaewon.han@connecthr.io'),
    ('오수빈',  '영업팀',  '대리',  '2022-11-07', 4100000, 'subin.oh@connecthr.io'),
    ('윤성민',  '데이터팀', '팀장',  '2018-04-15', 7000000, 'sungmin.yoon@connecthr.io');

-- 연차 잔액 데이터 (2024년)
INSERT INTO leave_balance (employee_id, year, total_days, used_days) VALUES
    (1, 2024, 15, 7),   -- 김도현: 잔여 8일
    (2, 2024, 15, 12),  -- 이서연: 잔여 3일
    (3, 2024, 15, 5),   -- 박민준: 잔여 10일
    (4, 2024, 15, 9),   -- 최지은: 잔여 6일
    (5, 2024, 10, 2),   -- 정다희: 잔여 8일 (1년 미만 비례)
    (6, 2024, 15, 6),   -- 한재원: 잔여 9일
    (7, 2024, 15, 11),  -- 오수빈: 잔여 4일
    (8, 2024, 20, 8);   -- 윤성민: 잔여 12일 (5년 이상 가산)

-- 월별 매출 데이터 (2024년 개발팀)
INSERT INTO sales_monthly (department, year, month, revenue, target) VALUES
    ('개발팀', 2024, 1,  85000000,  90000000),
    ('개발팀', 2024, 2,  92000000,  90000000),
    ('개발팀', 2024, 3,  88000000,  90000000),
    ('개발팀', 2024, 4,  95000000,  92000000),
    ('개발팀', 2024, 10, 97000000,  95000000),
    ('개발팀', 2024, 11, 103000000, 95000000),
    ('개발팀', 2024, 12, 108000000, 100000000);

-- 월별 매출 데이터 (2024년 영업팀)
INSERT INTO sales_monthly (department, year, month, revenue, target) VALUES
    ('영업팀', 2024, 1,  120000000, 130000000),
    ('영업팀', 2024, 2,  135000000, 130000000),
    ('영업팀', 2024, 3,  128000000, 130000000),
    ('영업팀', 2024, 10, 142000000, 140000000),
    ('영업팀', 2024, 11, 155000000, 145000000),
    ('영업팀', 2024, 12, 162000000, 150000000);

-- 월별 매출 데이터 (2024년 데이터팀)
INSERT INTO sales_monthly (department, year, month, revenue, target) VALUES
    ('데이터팀', 2024, 1,  45000000, 50000000),
    ('데이터팀', 2024, 2,  52000000, 50000000),
    ('데이터팀', 2024, 10, 63000000, 60000000),
    ('데이터팀', 2024, 11, 68000000, 65000000),
    ('데이터팀', 2024, 12, 72000000, 70000000);

-- ============================================================
-- 인덱스
-- ============================================================

CREATE INDEX idx_employees_name       ON employees (name);
CREATE INDEX idx_employees_department ON employees (department);
CREATE INDEX idx_leave_balance_emp    ON leave_balance (employee_id, year);
CREATE INDEX idx_sales_dept_year      ON sales_monthly (department, year, month);
