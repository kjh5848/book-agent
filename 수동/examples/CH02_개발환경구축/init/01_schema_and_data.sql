-- init/01_schema_and_data.sql
-- AI 업무 비서 구축: RAG + MCP 실전 가이드 — 2장 개발 환경 구축
--
-- 역할: PostgreSQL 컨테이너 최초 실행 시 자동으로 실행되는 초기화 스크립트입니다.
--       사내 업무 비서 실습에 필요한 테이블과 샘플 데이터를 생성합니다.
--
-- 포함 내용:
--   1. employees     — 직원 정보
--   2. leave_balance — 직원별 연차 잔여 현황
--   3. sales         — 월별 매출 데이터

-- =========================================================
-- 1. 직원 테이블
-- =========================================================
CREATE TABLE IF NOT EXISTS employees (
    id         SERIAL PRIMARY KEY,
    name       VARCHAR(50)  NOT NULL,
    department VARCHAR(50)  NOT NULL,
    position   VARCHAR(50)  NOT NULL,
    hire_date  DATE         NOT NULL,
    email      VARCHAR(100) UNIQUE NOT NULL
);

-- =========================================================
-- 2. 연차 잔여 테이블
-- =========================================================
CREATE TABLE IF NOT EXISTS leave_balance (
    id             SERIAL PRIMARY KEY,
    employee_id    INTEGER REFERENCES employees(id) ON DELETE CASCADE,
    year           INTEGER NOT NULL,
    total_days     INTEGER NOT NULL DEFAULT 15,
    used_days      INTEGER NOT NULL DEFAULT 0,
    remaining_days INTEGER GENERATED ALWAYS AS (total_days - used_days) STORED,
    updated_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =========================================================
-- 3. 월별 매출 테이블
-- =========================================================
CREATE TABLE IF NOT EXISTS sales (
    id          SERIAL PRIMARY KEY,
    year_month  VARCHAR(7)  NOT NULL,  -- 형식: YYYY-MM
    department  VARCHAR(50) NOT NULL,
    revenue     BIGINT      NOT NULL,  -- 단위: 원
    target      BIGINT      NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =========================================================
-- 샘플 데이터 삽입
-- =========================================================

-- 직원 샘플 데이터 (5명)
INSERT INTO employees (name, department, position, hire_date, email) VALUES
    ('김철수', '개발팀',   '선임 개발자', '2020-03-02', 'chulsoo.kim@company.com'),
    ('이영희', '마케팅팀', '팀장',        '2018-07-15', 'younghee.lee@company.com'),
    ('박민준', '인사팀',   '사원',        '2023-01-09', 'minjun.park@company.com'),
    ('최수진', '개발팀',   '팀장',        '2016-09-01', 'sujin.choi@company.com'),
    ('정대한', '영업팀',   '주임',        '2021-05-20', 'daehan.jung@company.com')
ON CONFLICT (email) DO NOTHING;

-- 연차 잔여 샘플 데이터 (2025년 기준)
INSERT INTO leave_balance (employee_id, year, total_days, used_days) VALUES
    (1, 2025, 15, 3),   -- 김철수: 12일 잔여
    (2, 2025, 20, 8),   -- 이영희: 12일 잔여 (팀장 연차 가산)
    (3, 2025, 11, 0),   -- 박민준: 11일 잔여 (1년 미만 월 단위)
    (4, 2025, 20, 15),  -- 최수진: 5일 잔여
    (5, 2025, 15, 5)    -- 정대한: 10일 잔여
ON CONFLICT DO NOTHING;

-- 월별 매출 샘플 데이터
INSERT INTO sales (year_month, department, revenue, target) VALUES
    ('2025-01', '영업팀',   45000000, 50000000),
    ('2025-01', '개발팀',   12000000, 10000000),
    ('2025-02', '영업팀',   53000000, 50000000),
    ('2025-02', '개발팀',    9500000, 10000000),
    ('2025-03', '영업팀',   61000000, 55000000),
    ('2025-03', '마케팅팀', 18000000, 20000000)
ON CONFLICT DO NOTHING;
