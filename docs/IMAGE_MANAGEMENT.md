# PyLadies Seoul 이미지 관리 가이드

이 문서는 PyLadies Seoul 웹사이트의 이미지 업로드, 관리 및 사용 방법에 대한 완전한 가이드입니다.

## 📋 목차

- [기본 이미지 업로드](#기본-이미지-업로드)
- [이미지 블록 사용법](#이미지-블록-사용법)
- [이미지 최적화](#이미지-최적화)
- [접근성 가이드라인](#접근성-가이드라인)
- [트러블슈팅](#트러블슈팅)
- [개발자 정보](#개발자-정보)

## 🖼️ 기본 이미지 업로드

### 1. 관리자 패널에서 이미지 업로드

1. **관리자 로그인**
   ```
   URL: http://localhost:8000/admin/
   ```

2. **Images 메뉴 접근**
   - 좌측 메뉴에서 "Images" 클릭
   - "Add Image" 버튼 클릭

3. **이미지 업로드**
   - 파일 선택 또는 드래그앤드롭
   - **제목** 입력 (필수)
   - **태그** 추가 (선택사항)
   - **Alt text** 입력 (접근성을 위해 강력 권장)

### 2. 지원되는 파일 형식

| 형식 | 확장자 | 최대 크기 | 권장 사용처 |
|------|--------|-----------|-------------|
| **JPEG** | .jpg, .jpeg | 10MB | 사진, 복잡한 이미지 |
| **PNG** | .png | 10MB | 로고, 투명 배경 |
| **WebP** | .webp | 10MB | 최적화된 웹 이미지 |
| **GIF** | .gif | 10MB | 애니메이션, 단순한 그래픽 |

### 3. 이미지 명명 규칙

```
권장 형식: [카테고리]_[설명]_[날짜].확장자

예시:
- event_python_workshop_20241201.jpg
- team_member_jane_doe.png  
- logo_pyladies_seoul.png
- gallery_meetup_2024.jpg
```

## 🎨 이미지 블록 사용법

PyLadies Seoul 웹사이트에서는 3가지 주요 이미지 블록을 제공합니다:

### 1. Full Width Image (전체 폭 이미지)

**사용 목적:** 페이지의 주요 이미지, 헤더 이미지, 강조하고 싶은 단일 이미지

**설정 방법:**
1. 페이지 편집 → Body StreamField
2. "Full Width Image" 블록 선택
3. 필드 설정:
   - **Image:** 업로드된 이미지 선택
   - **Caption:** 이미지 설명 (선택사항)
   - **Alt Text:** 접근성을 위한 대체 텍스트

**예시 사용 사례:**
```
✅ 이벤트 메인 사진
✅ 팀 단체 사진
✅ 워크샵 현장 사진
✅ 주요 발표 슬라이드
```

### 2. Image with Text (이미지와 텍스트)

**사용 목적:** 이미지와 설명 텍스트를 함께 배치할 때

**설정 방법:**
1. "Image with Text" 블록 선택
2. 필드 설정:
   - **Image:** 이미지 선택
   - **Image Position:** 좌측 또는 우측 선택
   - **Title:** 섹션 제목 (선택사항)
   - **Text:** 설명 텍스트 (RichText 지원)
   - **Alt Text:** 대체 텍스트

**레이아웃 옵션:**
```
[이미지] [텍스트]  ← 이미지가 좌측
[텍스트] [이미지]  ← 이미지가 우측
```

**예시 사용 사례:**
```
✅ 멤버 소개 (프로필 사진 + 자기소개)
✅ 프로젝트 설명 (스크린샷 + 설명)
✅ 이벤트 후기 (현장 사진 + 후기 텍스트)
✅ 도구/기술 소개 (로고 + 설명)
```

### 3. Image Gallery (이미지 갤러리)

**사용 목적:** 여러 이미지를 갤러리 형태로 표시

**설정 방법:**
1. "Image Gallery" 블록 선택
2. 필드 설정:
   - **Title:** 갤러리 제목 (선택사항)
   - **Images:** "Add Image" 버튼으로 이미지 추가
   
3. 각 이미지별 설정:
   - **Image:** 이미지 선택
   - **Caption:** 이미지별 캡션
   - **Alt Text:** 각 이미지의 대체 텍스트

**특별 기능:**
- 🔍 **라이트박스:** 이미지 클릭하면 확대 보기
- 📱 **반응형:** 화면 크기에 따라 자동 조정
- ⌨️ **키보드 지원:** ESC 키로 라이트박스 닫기

**예시 사용 사례:**
```
✅ 이벤트 현장 사진들
✅ 워크샵 진행 과정
✅ 팀 멤버들의 사진
✅ 프로젝트 스크린샷 모음
✅ 오피스/공간 소개 사진들
```

## ⚡ 이미지 최적화

### 자동 최적화 기능

시스템에서 자동으로 처리되는 기능들:

1. **자동 리사이징**
   - 최대 4000x4000 픽셀로 제한
   - 웹 최적화된 크기로 자동 조정

2. **포맷 최적화**
   - WebP 형식 자동 생성 (지원 브라우저용)
   - JPEG 품질 자동 조정 (85% 품질)

3. **반응형 이미지**
   - 다양한 화면 크기용 렌디션 자동 생성
   - 지연 로딩 (Lazy Loading) 적용

### 업로드 전 권장사항

| 용도 | 권장 해상도 | 권장 형식 | 파일 크기 목표 |
|------|-------------|-----------|----------------|
| **프로필 사진** | 500x500px | PNG/JPEG | < 200KB |
| **이벤트 사진** | 1200x800px | JPEG/WebP | < 500KB |
| **갤러리 사진** | 800x600px | JPEG/WebP | < 300KB |
| **로고/아이콘** | 512x512px | PNG | < 100KB |
| **배너 이미지** | 1920x600px | JPEG/WebP | < 800KB |

## ♿ 접근성 가이드라인

### Alt Text 작성 가이드

**DO ✅**
```
"PyLadies Seoul 2024년 Python 워크샵에서 참가자들이 코딩하는 모습"
"Jane Doe, PyLadies Seoul 오거나이저, 웃고 있는 프로필 사진"  
"Django 웹 애플리케이션 대시보드 스크린샷"
```

**DON'T ❌**
```
"이미지", "사진", "img_001.jpg"
"클릭하세요", "여기를 보세요"
너무 길거나 불필요한 설명
```

### Alt Text 작성 원칙

1. **구체적이고 간결하게** (50-100자 내외)
2. **맥락 고려** - 주변 텍스트와 중복 피하기
3. **중요 정보 우선** - 핵심 내용 먼저 언급
4. **장식용 이미지** - 빈 alt="" 사용 (매우 제한적)

## 🔧 트러블슈팅

### 자주 발생하는 문제들

#### 1. "업로드 실패" 오류

**원인과 해결책:**
```
❌ 파일 크기 초과 (10MB 제한)
   → 이미지 압축 또는 리사이징

❌ 지원하지 않는 형식
   → JPEG, PNG, WebP, GIF만 사용

❌ 파일명에 특수문자
   → 영문, 숫자, 하이픈, 언더스코어만 사용
```

#### 2. "이미지가 표시되지 않음"

**확인 사항:**
```
1. 이미지가 올바르게 업로드되었는지 확인
2. Alt Text가 설정되었는지 확인  
3. 브라우저 캐시 새로고침 (Ctrl+F5)
4. 다른 브라우저에서 테스트
```

#### 3. "갤러리 라이트박스 작동 안함"

**해결 방법:**
```
1. JavaScript 오류 확인 (개발자 도구)
2. 페이지 완전히 로드된 후 테스트
3. 다른 이미지로 테스트
4. 브라우저 호환성 확인
```

### 성능 관련 이슈

#### 페이지 로딩 속도 최적화

1. **이미지 개수 제한**
   - 갤러리: 최대 20개 이미지 권장
   - 페이지당 총 이미지: 10MB 이하

2. **적절한 블록 선택**
   - 단일 이미지: Full Width Image
   - 설명이 긴 경우: Image with Text  
   - 여러 이미지: Gallery (꼭 필요한 경우만)

## 👨‍💻 개발자 정보

### 기술 스택

```python
# 이미지 처리 관련 패키지
- Pillow>=10.1.0          # 이미지 처리
- willow[heif]>=1.8.0     # Wagtail 이미지 엔진
- wagtail>=6.2            # CMS 플랫폼

# 설정 파일 위치
- config/settings/base.py  # 이미지 관련 설정
- apps/pages/models.py     # 이미지 블록 정의
- templates/blocks/        # 이미지 블록 템플릿
```

### 이미지 설정 (settings/base.py)

```python
# 최대 업로드 크기
WAGTAILIMAGES_MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB

# 지원 형식
WAGTAILIMAGES_FORMAT_CONVERSIONS = {
    'bmp': 'jpeg',
    'webp': 'webp'
}

# 렌디션 형식
WAGTAILIMAGES_RENDITION_FORMATS = ['webp', 'jpeg', 'png']
```

### 파일 구조

```
apps/pages/
├── models.py              # 이미지 블록 정의
│   ├── ImageBlock
│   ├── ImageWithTextBlock
│   └── GalleryBlock
│
templates/blocks/
├── image_block.html       # 전체 폭 이미지 템플릿
├── image_with_text_block.html  # 이미지+텍스트 템플릿
└── gallery_block.html     # 갤러리 템플릿

media/
└── original_images/       # 업로드된 원본 이미지
```

### 커스터마이제이션

#### 새로운 이미지 블록 추가

```python
# apps/pages/models.py
class CustomImageBlock(StructBlock):
    image = ImageChooserBlock()
    custom_field = CharBlock(max_length=255)
    
    class Meta:
        template = "blocks/custom_image_block.html"
        icon = "image"
        label = "Custom Image"
```

#### 이미지 처리 훅 추가

```python
# apps/common/wagtail_hooks.py
@hooks.register('after_create_image')
def custom_image_processing(request, image):
    # 커스텀 이미지 처리 로직
    pass
```

### API 엔드포인트

```
GET  /admin/images/                    # 이미지 목록
POST /admin/images/create/             # 이미지 업로드
GET  /admin/images/{id}/               # 이미지 상세
PUT  /admin/images/{id}/edit/          # 이미지 수정
DEL  /admin/images/{id}/delete/        # 이미지 삭제
```

## 📝 변경 로그

### v1.0.0 (2024-12-24)
- ✅ 기본 이미지 업로드 기능
- ✅ 3가지 이미지 블록 (Full Width, Image with Text, Gallery)
- ✅ 라이트박스 갤러리 기능
- ✅ 자동 이미지 최적화
- ✅ 접근성 지원 (Alt Text)
- ✅ 반응형 디자인
- ✅ Font Awesome 아이콘 지원

## 🤝 기여하기

이미지 관리 기능 개선에 기여하고 싶다면:

1. **버그 리포트:** 발견된 문제점 보고
2. **기능 제안:** 새로운 이미지 블록이나 기능 아이디어
3. **문서 개선:** 사용법이나 가이드 보완
4. **코드 기여:** 새로운 이미지 처리 기능 개발

## 📞 지원

문의사항이나 도움이 필요한 경우:

- **GitHub Issues:** [pyladies-seoul/issues](https://github.com/pyladies-seoul/pyladies-seoul-new/issues)
- **이메일:** seoul@pyladies.com
- **Slack:** #tech-support 채널

---

**마지막 업데이트:** 2024년 12월 24일  
**문서 버전:** 1.0.0  
**작성자:** PyLadies Seoul Tech Team