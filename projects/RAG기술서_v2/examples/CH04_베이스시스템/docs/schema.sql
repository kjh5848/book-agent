-- ============================================================
-- 커넥트HR 사내 데이터베이스 스키마
-- 챕터 4: 베이스 시스템 확보
-- ============================================================

-- 데이터베이스 초기화 (기존 테이블 삭제 후 재생성)
DROP TABLE IF EXISTS sales_monthly CASCADE;
DROP TABLE IF EXISTS leave_balance CASCADE;
DROP TABLE IF EXISTS leave_requests CASCADE;
DROP TABLE IF EXISTS employees CASCADE;

-- ============================================================
-- 1. 직원 테이블 (employees)
-- ============================================================
CREATE TABLE employees (
    id            SERIAL PRIMARY KEY,
    name          VARCHAR(100) NOT NULL,
    department    VARCHAR(100) NOT NULL,
    hire_date     DATE         NOT NULL,
    base_salary   NUMERIC(12, 2) NOT NULL,
    email         VARCHAR(200) UNIQUE,
    is_active     BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE employees IS '커넥트HR 직원 기본 정보';
COMMENT ON COLUMN employees.id IS '직원 고유 식별자';
COMMENT ON COLUMN employees.name IS '직원 이름';
COMMENT ON COLUMN employees.department IS '소속 부서명';
COMMENT ON COLUMN employees.hire_date IS '입사일';
COMMENT ON COLUMN employees.base_salary IS '기본급 (원)';
COMMENT ON COLUMN employees.email IS '회사 이메일';
COMMENT ON COLUMN employees.is_active IS '재직 여부 (퇴사자 = FALSE)';

-- ============================================================
-- 2. 휴가 신청 테이블 (leave_requests)
-- ============================================================
CREATE TABLE leave_requests (
    id            SERIAL PRIMARY KEY,
    employee_id   INT          NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    leave_type    VARCHAR(50)  NOT NULL,  -- annual(연차), sick(병가), half(반차), special(특별휴가)
    start_date    DATE         NOT NULL,
    end_date      DATE         NOT NULL,
    status        VARCHAR(20)  NOT NULL DEFAULT 'pending',  -- pending, approved, rejected
    reason        TEXT,
    approved_by   INT          REFERENCES employees(id),
    created_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_date_order CHECK (end_date >= start_date),
    CONSTRAINT chk_status     CHECK (status IN ('pending', 'approved', 'rejected')),
    CONSTRAINT chk_leave_type CHECK (leave_type IN ('annual', 'sick', 'half', 'special'))
);

COMMENT ON TABLE leave_requests IS '직원 휴가 신청 내역';
COMMENT ON COLUMN leave_requests.leave_type IS '휴가 유형: annual(연차), sick(병가), half(반차), special(특별휴가)';
COMMENT ON COLUMN leave_requests.status IS '처리 상태: pending(대기), approved(승인), rejected(반려)';

-- ============================================================
-- 3. 연차 잔액 테이블 (leave_balance)
-- ============================================================
CREATE TABLE leave_balance (
    id            SERIAL PRIMARY KEY,
    employee_id   INT          NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    year          INT          NOT NULL,
    total_days    NUMERIC(5,1) NOT NULL DEFAULT 15.0,
    used_days     NUMERIC(5,1) NOT NULL DEFAULT 0.0,
    created_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    UNIQUE(employee_id, year),
    CONSTRAINT chk_used_days  CHECK (used_days <= total_days),
    CONSTRAINT chk_total_days CHECK (total_days > 0)
);

COMMENT ON TABLE leave_balance IS '직원 연도별 연차 잔액';
COMMENT ON COLUMN leave_balance.total_days IS '연도별 총 연차 일수';
COMMENT ON COLUMN leave_balance.used_days IS '사용한 연차 일수';

-- ============================================================
-- 4. 월별 매출 테이블 (sales_monthly)
-- ============================================================
CREATE TABLE sales_monthly (
    id            SERIAL PRIMARY KEY,
    department    VARCHAR(100) NOT NULL,
    year          INT          NOT NULL,
    month         INT          NOT NULL,
    revenue       NUMERIC(15, 2) NOT NULL DEFAULT 0,
    target        NUMERIC(15, 2),
    created_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    UNIQUE(department, year, month),
    CONSTRAINT chk_month CHECK (month BETWEEN 1 AND 12),
    CONSTRAINT chk_year  CHECK (year BETWEEN 2000 AND 2100)
);

COMMENT ON TABLE sales_monthly IS '부서별 월별 매출 실적';
COMMENT ON COLUMN sales_monthly.revenue IS '실제 매출액 (원)';
COMMENT ON COLUMN sales_monthly.target IS '목표 매출액 (원)';

-- ============================================================
-- 샘플 데이터 INSERT
-- ============================================================

-- 1) 직원 샘플 데이터 (15명)
INSERT INTO employees (name, department, hire_date, base_salary, email) VALUES
    ('김도현',   '개발팀',   '2019-03-01', 5800000, 'dohyun.kim@connecthr.io'),
    ('이서연',   '개발팀',   '2022-06-15', 3600000, 'seoyeon.lee@connecthr.io'),
    ('박민준',   '데이터팀', '2020-09-01', 4800000, 'minjun.park@connecthr.io'),
    ('최예진',   '인사팀',   '2018-01-10', 4200000, 'yejin.choi@connecthr.io'),
    ('정하준',   '영업팀',   '2021-04-20', 4000000, 'hajun.jung@connecthr.io'),
    ('윤소희',   '마케팅팀', '2020-11-05', 3900000, 'sohee.yoon@connecthr.io'),
    ('임재원',   '개발팀',   '2021-07-12', 4100000, 'jaewon.lim@connecthr.io'),
    ('강민서',   '데이터팀', '2022-02-28', 3750000, 'minseo.kang@connecthr.io'),
    ('오지훈',   '영업팀',   '2019-08-15', 4500000, 'jihoon.oh@connecthr.io'),
    ('신아라',   '인사팀',   '2023-01-02', 3400000, 'ara.shin@connecthr.io'),
    ('한동욱',   '마케팅팀', '2017-05-22', 5200000, 'dongwook.han@connecthr.io'),
    ('배수진',   '개발팀',   '2023-03-15', 3500000, 'sujin.bae@connecthr.io'),
    ('구본철',   '데이터팀', '2018-12-01', 5500000, 'boncheol.koo@connecthr.io'),
    ('류지민',   '영업팀',   '2022-09-01', 3800000, 'jimin.ryu@connecthr.io'),
    ('문채원',   '마케팅팀', '2021-01-11', 4300000, 'chaewon.moon@connecthr.io');

-- 2) 휴가 신청 샘플 데이터 (15건)
INSERT INTO leave_requests (employee_id, leave_type, start_date, end_date, status, reason, approved_by) VALUES
    (2,  'annual',  '2025-01-06', '2025-01-08', 'approved', '개인 일정', 1),
    (3,  'sick',    '2025-01-15', '2025-01-16', 'approved', '독감 치료', 1),
    (5,  'annual',  '2025-02-03', '2025-02-05', 'approved', '가족 여행', 9),
    (7,  'half',    '2025-02-14', '2025-02-14', 'approved', '병원 방문', 1),
    (4,  'annual',  '2025-03-10', '2025-03-14', 'approved', '해외 출장 전 준비', 4),
    (8,  'special', '2025-03-20', '2025-03-21', 'approved', '결혼기념일', 3),
    (2,  'annual',  '2025-04-07', '2025-04-11', 'pending',  '해외여행', NULL),
    (10, 'sick',    '2025-04-14', '2025-04-14', 'approved', '감기', 4),
    (12, 'annual',  '2025-05-02', '2025-05-02', 'approved', '개인 일정', 1),
    (6,  'annual',  '2025-05-19', '2025-05-23', 'rejected', '프로젝트 마감 기간', 11),
    (14, 'half',    '2025-06-04', '2025-06-04', 'approved', '관공서 방문', 9),
    (9,  'annual',  '2025-06-16', '2025-06-20', 'approved', '여름 휴가', 9),
    (13, 'special', '2025-07-07', '2025-07-07', 'approved', '가족 행사', 3),
    (3,  'annual',  '2025-07-21', '2025-07-25', 'pending',  '여름 휴가', NULL),
    (15, 'annual',  '2025-08-11', '2025-08-15', 'pending',  '개인 여행', NULL);

-- 3) 연차 잔액 샘플 데이터 (직원별 2025년)
INSERT INTO leave_balance (employee_id, year, total_days, used_days) VALUES
    (1,  2025, 20.0, 5.0),
    (2,  2025, 15.0, 8.0),
    (3,  2025, 18.0, 6.0),
    (4,  2025, 20.0, 7.0),
    (5,  2025, 15.0, 3.0),
    (6,  2025, 18.0, 5.0),
    (7,  2025, 15.0, 1.5),
    (8,  2025, 15.0, 2.0),
    (9,  2025, 20.0, 5.0),
    (10, 2025, 12.0, 1.0),
    (11, 2025, 22.0, 10.0),
    (12, 2025, 12.0, 1.0),
    (13, 2025, 20.0, 3.0),
    (14, 2025, 15.0, 1.5),
    (15, 2025, 15.0, 5.0);

-- 4) 월별 매출 샘플 데이터 (부서별, 2024~2025)
INSERT INTO sales_monthly (department, year, month, revenue, target) VALUES
    -- 개발팀 (2025)
    ('개발팀', 2025, 1,  85000000,  90000000),
    ('개발팀', 2025, 2,  92000000,  90000000),
    ('개발팀', 2025, 3,  88000000,  90000000),
    ('개발팀', 2025, 4,  95000000,  95000000),
    ('개발팀', 2025, 5,  97000000,  95000000),
    ('개발팀', 2025, 6, 103000000, 100000000),
    -- 영업팀 (2025)
    ('영업팀', 2025, 1, 120000000, 130000000),
    ('영업팀', 2025, 2, 135000000, 130000000),
    ('영업팀', 2025, 3, 128000000, 130000000),
    ('영업팀', 2025, 4, 142000000, 140000000),
    ('영업팀', 2025, 5, 138000000, 140000000),
    ('영업팀', 2025, 6, 155000000, 150000000),
    -- 마케팅팀 (2025)
    ('마케팅팀', 2025, 1,  45000000, 50000000),
    ('마케팅팀', 2025, 2,  52000000, 50000000),
    ('마케팅팀', 2025, 3,  48000000, 50000000),
    ('마케팅팀', 2025, 4,  53000000, 55000000),
    ('마케팅팀', 2025, 5,  57000000, 55000000),
    ('마케팅팀', 2025, 6,  60000000, 58000000),
    -- 데이터팀 (2024 하반기 비교용)
    ('데이터팀', 2024, 7,  35000000, 38000000),
    ('데이터팀', 2024, 8,  38000000, 38000000),
    ('데이터팀', 2024, 9,  40000000, 40000000),
    ('데이터팀', 2024, 10, 42000000, 40000000),
    ('데이터팀', 2024, 11, 39000000, 42000000),
    ('데이터팀', 2024, 12, 44000000, 42000000);
