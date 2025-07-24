# 🐍 PyLadies Seoul Official Homepage

<div align="center">

![PyLadies Seoul Logo](https://github.com/PyLadiesKorea/pyladies-seoul/assets/160496301/dc7564ff-8b6a-4270-af97-c4a4c208418a)

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![Django Version](https://img.shields.io/badge/django-5.2+-green.svg)](https://djangoproject.com)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

</div>

## 📖 프로젝트 소개

PyLadies Seoul은 한국의 여성 Python 사용자를 위한 커뮤니티입니다. 이 프로젝트는 PyLadies Seoul의 공식 홈페이지로, 커뮤니티 소개, 활동 정보, 기여 방법 등을 제공합니다.

### 🎯 프로젝트 목표

- **커뮤니티 홍보**: PyLadies Seoul의 비전과 미션을 널리 알리기
- **참여 유도**: 새로운 멤버들의 참여를 장려하고 활동 정보 제공
- **활동 관리**: 세미나, 워크샵, 스터디그룹 등 다양한 활동 관리
- **효율적 운영**: 오거나이저들의 콘텐츠 관리 지원

### ✨ 주요 기능

- 🌐 **다국어 지원**: 한국어/영어 완전 지원
- 📅 **활동 관리**: 세미나, 워크샵, 밋업, 스터디그룹 통합 관리
- 👥 **오거나이저 소개**: 커뮤니티 운영진 프로필 관리
- ❓ **FAQ 시스템**: 자주 묻는 질문과 답변 관리
- 🤝 **기여 기회**: 다양한 참여 방법 안내
- 📱 **반응형 디자인**: 모바일/태블릿/데스크톱 완벽 지원
- 🔗 **소셜 미디어 연동**: Discord, GitHub 등 외부 플랫폼 연결

## 🛠️ 기술 스택

### Backend
- **Python 3.11+**: 최신 Python 기능 활용
- **Django 5.2**: 강력한 웹 프레임워크
- **SQLite**: 간단하고 효율적인 데이터베이스
- **Django Extensions**: 개발 생산성 향상

### Frontend
- **HTMX**: 동적 사용자 인터페이스
- **TailwindCSS**: 유틸리티 기반 CSS 프레임워크
- **Responsive Design**: 모든 디바이스 지원

### Development Tools
- **uv**: 빠른 Python 패키지 관리자
- **Black**: 코드 포매터
- **isort**: Import 정렬
- **Flake8**: 코드 스타일 검사
- **mypy**: 타입 검사
- **pre-commit**: 커밋 전 자동 검사

### DevOps & Infrastructure
- **Docker**: 컨테이너화
- **Docker Compose**: 로컬 개발 환경
- **Kubernetes**: 운영 환경 배포
- **Helm**: Kubernetes 패키지 관리
- **Terraform**: 인프라 관리

## 🚀 빠른 시작

### 전제 조건

- Python 3.11 이상
- uv 패키지 관리자
- Git

### 설치 방법

1. **저장소 클론**
   ```bash
   git clone https://github.com/pyladies-seoul/pyladies-seoul.git
   cd pyladies-seoul
   ```

2. **가상 환경 생성 및 활성화**
   ```bash
   uv venv
   source .venv/bin/activate  # Linux/macOS
   # 또는
   .venv\Scripts\activate     # Windows
   ```

3. **의존성 설치**
   ```bash
   uv sync
   ```

4. **데이터베이스 마이그레이션**
   ```bash
   python manage.py migrate
   ```

5. **정적 파일 수집**
   ```bash
   python manage.py collectstatic
   ```

6. **슈퍼유저 생성 (선택사항)**
   ```bash
   python manage.py createsuperuser
   ```

7. **개발 서버 실행**
   ```bash
   python manage.py runserver
   ```

8. **브라우저에서 확인**
   - 메인 사이트: http://127.0.0.1:8000/

### Docker를 사용한 실행

#### 개발 환경 (Django runserver 사용)

1. **Docker Compose로 개발 환경 실행**
   ```bash
   # 백그라운드에서 실행
   docker-compose up -d

   # 로그 확인
   docker-compose logs -f

   # 서비스 중지
   docker-compose down
   ```

2. **데이터베이스 마이그레이션 (최초 실행 시)**
   ```bash
   # 컨테이너가 실행 중일 때
   docker-compose exec web uv run python manage.py migrate
   docker-compose exec web uv run python manage.py createsuperuser
   ```

3. **브라우저에서 확인**
   - 메인 사이트: http://localhost:8000/
   - 관리자 페이지: http://localhost:8000/organizer/

#### 프로덕션 환경 (Gunicorn + Nginx 사용)

1. **환경 변수 설정**
   ```bash
   # .env.example을 .env로 복사하고 값 수정
   cp .env.example .env
   ```

2. **프로덕션 환경 실행**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

#### Docker 단독 사용

```bash
# 이미지 빌드
docker build -t pyladies-seoul .

# 컨테이너 실행
docker run -p 8000:8000 pyladies-seoul
```

## 📁 프로젝트 구조

```
pyladies-seoul/
├── 📁 config/                 # Django 설정
│   ├── settings.py            # 메인 설정 파일
│   ├── urls.py               # 루트 URL 설정
│   ├── wsgi.py               # WSGI 설정
│   └── asgi.py               # ASGI 설정
├── 📁 main/                   # 메인 애플리케이션
│   ├── models.py             # 데이터 모델
│   ├── views.py              # 뷰 로직
│   ├── admin.py              # 관리자 인터페이스
│   ├── urls.py               # URL 라우팅
│   └── migrations/           # 데이터베이스 마이그레이션
├── 📁 templates/              # HTML 템플릿
│   ├── base.html             # 기본 레이아웃
│   ├── index.html            # 메인 페이지
│   ├── contribute.html       # 기여 페이지
│   └── faq.html              # FAQ 페이지
├── 📁 theme/                  # TailwindCSS 테마
│   ├── static/               # 정적 파일
│   └── templates/            # 테마 템플릿
├── 📁 media/                  # 업로드된 미디어 파일
├── 📁 docs/                   # 문서화
│   └── wiki/                 # Wiki 문서
├── 📁 scripts/                # 유틸리티 스크립트
│   └── sync-wiki.sh          # Wiki 동기화 스크립트
├── 📁 .github/                # GitHub 설정
│   ├── ISSUE_TEMPLATE/       # 이슈 템플릿
│   └── pull_request_template.md
├── pyproject.toml            # 프로젝트 설정
├── uv.lock                   # 의존성 잠금 파일
├── docker-compose.yml        # Docker Compose 설정
├── Dockerfile                # Docker 이미지 정의
└── .pre-commit-config.yaml   # Pre-commit 훅 설정
```

## 🗄️ 데이터베이스 스키마

### 주요 모델 구조

#### 🎯 Activity (활동)
- **목적**: 세미나, 워크샵, 밋업, 스터디그룹 등 모든 활동 관리
- **주요 필드**:
  - `title_ko/en`: 활동 제목 (한/영)
  - `description_ko/en`: 활동 설명 (한/영)
  - `activity_type`: 활동 유형 (세미나, 워크샵, 밋업, 네트워킹, 스터디그룹)
  - `start_datetime/end_datetime`: 시작/종료 시간
  - `location_*`: 장소 정보
  - `meeting_schedule_*`: 정기 모임 일정 (스터디그룹용)
  - `is_recruiting`: 모집 중 여부
  - `is_public/is_featured`: 공개/추천 여부

#### 👥 Organizer (오거나이저)
- **목적**: 커뮤니티 운영진 정보 관리
- **주요 필드**:
  - `name_ko/en`: 이름 (한/영)
  - `role_ko/en`: 역할 (한/영)
  - `bio_ko/en`: 소개 (한/영)
  - `photo`: 프로필 사진
  - `email/github/linkedin`: 연락처 정보
  - `order`: 표시 순서

#### ❓ FAQ (자주 묻는 질문)
- **목적**: 자주 묻는 질문과 답변 관리
- **주요 필드**:
  - `category`: 카테고리 (일반, 참여, 활동, 기술, 연락처)
  - `question_ko/en`: 질문 (한/영)
  - `answer_ko/en`: 답변 (한/영)
  - `order`: 표시 순서

#### 🔗 SocialMediaPlatform (소셜 미디어)
- **목적**: Discord, GitHub 등 외부 플랫폼 링크 관리
- **주요 필드**:
  - `name_ko/en`: 플랫폼명 (한/영)
  - `url`: 링크 URL
  - `icon/icon_class`: 아이콘 정보
  - `is_active`: 활성 상태

#### 🤝 ContributionOpportunity (기여 기회)
- **목적**: 커뮤니티 기여 방법 안내
- **주요 필드**:
  - `type`: 기여 유형 (메이커, 스피커, 스터디 리더, 스폰서 등)
  - `title_ko/en`: 제목 (한/영)
  - `description_ko/en`: 설명 (한/영)
  - `requirements_ko/en`: 요구사항 (한/영)
  - `contact_method_ko/en`: 연락 방법 (한/영)
  - `is_open`: 모집 중 여부

### 공통 특징
- **다국어 지원**: 모든 텍스트 필드는 한국어/영어 버전 제공
- **타임스탬프**: 모든 모델에 생성/수정 시간 자동 기록
- **공개 설정**: 대부분 모델에 공개 여부 설정 가능
- **순서 관리**: 표시 순서 커스터마이징 지원

## 🧪 테스트 실행

```bash
# 모든 테스트 실행
python manage.py test

# 특정 앱 테스트
python manage.py test main

# 커버리지 포함 테스트
pytest --cov=main --cov-report=html
```

## 🔧 개발 도구

### Pre-commit 훅 설정

```bash
# pre-commit 설치 및 설정
uv add --dev pre-commit
pre-commit install

# 수동 실행
pre-commit run --all-files
```

### 코드 품질 검사

```bash
# 코드 포매팅
black .
isort .

# 타입 검사
mypy .

# 스타일 검사
flake8 .

# Django 시스템 검사
python manage.py check
```

## 🤝 기여하기

PyLadies Seoul 프로젝트에 기여해주셔서 감사합니다! 다음과 같은 방법으로 참여할 수 있습니다:

### 🐛 버그 리포트

버그를 발견하셨나요? [이슈](https://github.com/pyladies-seoul/pyladies-seoul/issues/new?template=bug_report.md)를 생성해주세요.

### 💡 기능 제안

새로운 기능을 제안하고 싶으시다면 [기능 요청](https://github.com/pyladies-seoul/pyladies-seoul/issues/new?template=feature_request.md)을 생성해주세요.

### 🔧 개발 기여

1. **저장소 포크**
2. **기능 브랜치 생성**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **변경사항 커밋**
   ```bash
   git commit -m "feat: Add amazing feature"
   ```
4. **브랜치 푸시**
   ```bash
   git push origin feature/amazing-feature
   ```
5. **Pull Request 생성**

### 📝 코딩 스타일 가이드

- **Python**: PEP 8 준수, Black 포매터 사용
- **타입 힌트**: 모든 함수에 타입 힌트 적용
- **Django**: Django 모범 사례 준수
- **커밋 메시지**: [Conventional Commits](https://www.conventionalcommits.org/) 형식 사용
- **테스트**: 새로운 기능에 대한 테스트 작성 권장

## 📚 문서화

### Wiki 관리

프로젝트 Wiki는 `docs/wiki/` 디렉토리에서 관리됩니다:

```bash
# Wiki 동기화
./scripts/sync-wiki.sh
```

### API 문서

Django Admin을 통해 데이터를 관리할 수 있습니다:
- 관리자 페이지: `/admin/`
- API 엔드포인트: 추후 DRF 적용 예정

## 🚀 배포

### 환경 변수 설정

```bash
# .env 파일 생성
cp .env.example .env

# 필요한 환경 변수 설정
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=your-domain.com
```

### Docker 배포

```bash
# 프로덕션 빌드
docker build -t pyladies-seoul:latest .

# 컨테이너 실행
docker run -d -p 80:8000 --env-file .env pyladies-seoul:latest
```

### Kubernetes 배포

```bash
# Helm을 사용한 배포
helm install pyladies-seoul ./helm-chart/

# 또는 kubectl 사용
kubectl apply -f k8s/
```

## 🆘 문제 해결

### 자주 발생하는 문제들

1. **모듈을 찾을 수 없음**
   ```bash
   # 가상 환경 활성화 확인
   source .venv/bin/activate
   uv sync
   ```

2. **데이터베이스 오류**
   ```bash
   # 마이그레이션 재실행
   python manage.py migrate --run-syncdb
   ```

3. **정적 파일 문제**
   ```bash
   # 정적 파일 다시 수집
   python manage.py collectstatic --clear
   ```

### 도움이 필요하신가요?

- 📧 이메일: [seoul@pyladies.com](mailto:seoul@pyladies.com)
- 💬 Discord: [PyLadies Seoul 서버](https://discord.gg/pyladies-seoul)
- 🐛 이슈: [GitHub Issues](https://github.com/pyladies-seoul/pyladies-seoul/issues)

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 👥 기여자

이 프로젝트는 PyLadies Seoul 커뮤니티의 많은 기여자들 덕분에 만들어졌습니다.

<div align="center">

### 🌟 PyLadies Seoul과 함께하세요!

Python을 사랑하는 모든 여성분들을 환영합니다.

[🔗 Discord 참여하기](https://discord.gg/pyladies-seoul) | [📧 이메일 보내기](mailto:seoul@pyladies.com) | [🐙 GitHub 팔로우](https://github.com/pyladies-seoul)

</div>

---

## 📋 Code of Conduct

### 행동 강령

PyLadies는 모든 사람에게 존중받고 괴롭힘 없는 커뮤니티를 제공하기 위해 최선을 다하고 있습니다. 우리는 어떤 형태의 괴롭힘이나 괴롭힘도 용납하지 않습니다. 이는 지역 PyLadies 커뮤니티의 구성원뿐만 아니라 이벤트나 상호 작용을 통해 더 큰 PyLadies 사용자, 개발자 및 통합자 커뮤니티에 참여하기로 선택한 모든 사람에게 적용됩니다.

괴롭힘에는 개인적 특성이나 선택과 관련된 공격적인 언어적/전자적 댓글, 공공 또는 온라인 공간에서의 성적 이미지나 댓글, 고의적 위협, 괴롭힘, 스토킹, 따라다니기, 괴롭힘 사진 촬영 또는 녹음, 지속적인 대화 방해, IRC 채팅, 전자 회의, 물리적 회의 또는 기타 이벤트, 부적절한 신체 접촉 또는 원치 않는 성적 관심이 포함됩니다.

괴롭힘이나 괴롭힘 행위를 중단하도록 요청받은 참가자는 즉시 준수해야 합니다.

참가자가 괴롭힘 행위에 가담하는 경우, 커뮤니티 대표자는 가해자에 대한 경고, PyLadies 이벤트에서의 추방, 메일링 리스트에서의 추방, IRC 채팅, 토론 게시판 및 기타 전자 통신 채널에서의 추방을 포함하여 문제를 해결하기 위해 적절하다고 판단되는 합리적인 조치를 취할 수 있습니다. 여기에는 PyLadies Meetup 그룹 멤버십에서의 추방이 포함될 수 있습니다.

괴롭힘을 당하고 있거나, 다른 사람이 괴롭힘을 당하고 있음을 발견했거나, 기타 우려사항이 있는 경우, PyLadies 커뮤니티의 구성원, IRC 채팅 관리자, 웹사이트 관리자 또는 PyLadies 후원 하에 개최되는 물리적 이벤트의 주최자/대표자에게 중재를 요청하거나 도움을 요청하시기 바랍니다.

이 행동 강령은 [Plone Foundation](https://plone.org/foundation/materials/foundation-resolutions/code-of-conduct)에서 채택되었으며 [Creative Commons Attribution-Share Alike 3.0 Unported license](https://plone.org/foundation/about/materials/foundation-resolutions/code-of-conduct) 하에 라이선스가 부여됩니다.

## 📅 정기 모임

매월 최소 한 번 이상 정기 모임을 개최합니다. 모임 기록은 [Meeting Logs](https://github.com/PyLadiesKorea/pyladies-seoul/wiki/Meeting-Log)에서 확인할 수 있습니다.
