import pandas as pd
from datetime import datetime, timedelta
import random
import os

# 폴더 생성 확인
os.makedirs('data', exist_ok=True)

# 1. 직원 데이터 구성
departments = ['인사팀', '개발팀', '영업팀', '마케팅팀', '기술지원팀']
names = ['홍길동', '이민수', '박지은', '최동훈', '정소연', '한지형', '윤준호', '송미경', '조현우', '강민주']
employees = []
for i, name in enumerate(names):
    employees.append({
        'id': i + 1,
        'name': name,
        'dept': random.choice(departments),
        'email': f"user{i+1}@metacoding.com",
        'hire_date': (datetime.now() - timedelta(days=random.randint(300, 2000))).strftime('%Y-%m-%d')
    })
df_emp = pd.DataFrame(employees)

# 2. 휴가 데이터 구성
leaves = []
for emp in employees:
    total = 15.0
    used = float(random.randint(0, 10))
    leaves.append({
        'employee_id': emp['id'],
        'employee_name': emp['name'],
        'year': 2024,
        'total': total,
        'used': used,
        'remaining': total - used
    })
df_leave = pd.DataFrame(leaves)

# 3. 매출 데이터 구성
sales = []
for _ in range(20):
    dept = random.choice(departments)
    sales.append({
        'dept': dept,
        'amount': random.randint(100, 5000) * 10000,
        'date': (datetime.now() - timedelta(days=random.randint(0, 90))).strftime('%Y-%m-%d'),
        'description': f"{dept} 프로젝트 수입"
    })
df_sales = pd.DataFrame(sales)

# 엑셀 저장
try:
    with pd.ExcelWriter('data/db_dump_sample.xlsx', engine='openpyxl') as writer:
        df_emp.to_excel(writer, sheet_name='Employees', index=False)
        df_leave.to_excel(writer, sheet_name='LeaveBalance', index=False)
        df_sales.to_excel(writer, sheet_name='Sales', index=False)
    print('✅ Excel 파일 생성 완료: data/db_dump_sample.xlsx')
except Exception as e:
    print(f'❌ Excel 생성 실패: {e}')

# CSV 버전으로도 저장 (PDF 대신 활용 가능)
df_emp.to_csv('data/employees.csv', index=False)
df_leave.to_csv('data/leave_balance.csv', index=False)
df_sales.to_csv('data/sales_history.csv', index=False)
print('✅ CSV 파일들 생성 완료')
