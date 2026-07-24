# Tiny Market

Flask와 SQLite로 구현한 교육용 소규모 중고거래 플랫폼입니다.  
회원가입, 로그인, 상품 CRUD, 구매 요청, 판매자 승인·거절 기능을 제공합니다.

## 주요 기능

- 회원가입 / 로그인 / 로그아웃
- 상품 등록 / 목록 / 상세 / 수정 / 삭제
- 상품 검색 및 페이지네이션
- 구매 요청
- 판매자의 구매 요청 승인 / 거절
- 판매 완료 상품 상태 관리
- 판매 내역 / 구매 요청 내역 조회
- CSRF, 비밀번호 해시, 권한 검증, XSS 이스케이프

## WSL 실행 방법

### 1. 프로젝트 준비

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git

cd ~/projects
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd tiny-market-flask
```

압축 파일로 받은 경우:

```bash
mkdir -p ~/projects/tiny-market-flask
unzip tiny-market-flask.zip -d ~/projects/tiny-market-flask
cd ~/projects/tiny-market-flask
```

### 2. 가상환경 및 패키지 설치

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. 환경변수 설정

```bash
cp .env.example .env
python3 -c "import secrets; print(secrets.token_hex(32))"
```

출력된 값을 `.env`의 `SECRET_KEY`에 입력합니다.

```env
SECRET_KEY=<생성한 긴 랜덤 문자열>
FLASK_DEBUG=1
COOKIE_SECURE=0
```

### 4. 실행

```bash
python run.py
```

브라우저에서 `http://127.0.0.1:5000`에 접속합니다.


## 테스트

```bash
source .venv/bin/activate
pytest -q
```

## 프로젝트 구조

```text
tiny-market-flask/
├── app/
│   ├── __init__.py
│   ├── auth.py
│   ├── forms.py
│   ├── models.py
│   ├── products.py
│   ├── transactions.py
│   ├── static/
│   └── templates/
├── tests/
├── docs/
├── run.py
├── requirements.txt
├── Dockerfile
├── compose.yaml
└── README.md
```

## 보안 설계

| 항목 | 적용 내용 |
|---|---|
| 비밀번호 보호 | Werkzeug PBKDF 기반 비밀번호 해시 |
| 인증 | Flask-Login 세션 인증 |
| 접근 통제 | 상품 수정·삭제 및 거래 승인 시 소유권 검사 |
| IDOR 방지 | URL의 객체 ID뿐 아니라 현재 사용자와 소유자 관계 검증 |
| CSRF 방지 | Flask-WTF CSRF 토큰 적용 |
| SQL Injection 방지 | SQLAlchemy ORM 사용 |
| XSS 방지 | Jinja2 자동 이스케이프 유지, `safe` 필터 미사용 |
| Open Redirect 방지 | 로그인 후 이동 URL의 호스트 검증 |
| 입력값 검증 | WTForms 길이, 형식, 가격 범위 검증 |
| 세션 쿠키 | HttpOnly와 SameSite=Lax 설정 |
| 비밀정보 관리 | `.env` 제외 및 `.env.example` 제공 |
| 중복 요청 | DB 유일 제약과 서버 측 중복 확인 |
| 거래 무결성 | 판매자만 승인 가능, 승인 시 나머지 요청 자동 거절 |


