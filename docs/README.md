# PyLadies Seoul 문서 센터

PyLladies Seoul 웹사이트 운영 및 개발에 필요한 모든 문서들을 한 곳에 모았습니다.

## 📚 문서 목록

### 🎯 사용자 가이드
| 문서 | 설명 | 대상 |
|------|------|------|
| **[이미지 업로드 퀵 가이드](IMAGE_QUICK_GUIDE.md)** | 이미지 업로드 및 사용 간단 가이드 | 콘텐츠 관리자 |
| **[이미지 관리 완전 가이드](IMAGE_MANAGEMENT.md)** | 이미지 기능의 모든 것 | 관리자, 개발자 |

### 🏗️ 시스템 & 운영 
| 문서 | 설명 | 대상 |
|------|------|------|
| **[배포 런북](DEPLOYMENT_RUNBOOK.md)** | 프로덕션 배포 절차 및 체크리스트 | DevOps, 시스템 관리자 |
| **[재해 복구 계획](DISASTER_RECOVERY.md)** | 장애 상황 대응 및 복구 절차 | DevOps, 시스템 관리자 |

### 📋 프로젝트 문서
| 문서 | 설명 | 위치 |
|------|------|------|
| **[아키텍처 가이드](../ARCHITECTURE.md)** | 시스템 구조 및 기술 스택 | 루트 디렉토리 |
| **[개발 워크플로우](../DEVELOPMENT_WORKFLOW.md)** | 개발 프로세스 및 Git 플로우 | 루트 디렉토리 |
| **[구현 계획](../IMPLEMENTATION_PLAN.md)** | 단계별 구현 로드맵 | 루트 디렉토리 |
| **[리스크 분석](../RISK_ANALYSIS.md)** | 프로젝트 리스크 및 대응 방안 | 루트 디렉토리 |
| **[PRD](../PRD.md)** | 제품 요구사항 문서 | 루트 디렉토리 |
| **[상세 PRD](../PRD_DETAILED.md)** | 세부 기능 명세서 | 루트 디렉토리 |

### 🤖 개발자 가이드
| 문서 | 설명 | 위치 |  
|------|------|------|
| **[Claude 지시사항](../CLAUDE.md)** | AI 개발 어시스턴트 가이드라인 | 루트 디렉토리 |
| **[README](../README.md)** | 프로젝트 개요 및 시작 가이드 | 루트 디렉토리 |

## 🚀 빠른 시작

### 콘텐츠 관리자라면
1. **[이미지 업로드 퀵 가이드](IMAGE_QUICK_GUIDE.md)** 📸
2. 웹사이트 관리자 패널 접속
3. 필요시 [상세 이미지 관리 가이드](IMAGE_MANAGEMENT.md) 참고

### 개발자라면  
1. **[README](../README.md)** - 프로젝트 설정 방법
2. **[CLAUDE.md](../CLAUDE.md)** - 개발 가이드라인  
3. **[ARCHITECTURE.md](../ARCHITECTURE.md)** - 시스템 아키텍처

### DevOps/시스템 관리자라면
1. **[배포 런북](DEPLOYMENT_RUNBOOK.md)** - 배포 절차
2. **[재해 복구 계획](DISASTER_RECOVERY.md)** - 장애 대응
3. **[리스크 분석](../RISK_ANALYSIS.md)** - 리스크 관리

## 📖 문서 사용법

### 문서 읽는 순서

#### 새로운 팀 멤버
```
1. README.md (프로젝트 개요)
2. ARCHITECTURE.md (기술 스택 이해)  
3. 역할별 전문 문서들
```

#### 콘텐츠 업데이트할 때
```
1. IMAGE_QUICK_GUIDE.md (기본 사용법)
2. 필요시 IMAGE_MANAGEMENT.md (고급 기능)
```

#### 새 기능 개발할 때
```
1. CLAUDE.md (개발 가이드라인)
2. DEVELOPMENT_WORKFLOW.md (개발 프로세스)
3. IMPLEMENTATION_PLAN.md (구현 계획)
```

### 문서 기여하기

문서 개선에 참여하려면:

1. **오타/오류 수정**: 즉시 수정 후 PR
2. **내용 추가**: 이슈 생성 후 논의
3. **새 문서**: 팀과 상의 후 작성

## 🔍 자주 찾는 정보

### 이미지 관련
- **이미지 업로드 방법**: [IMAGE_QUICK_GUIDE.md](IMAGE_QUICK_GUIDE.md)
- **지원 파일 형식**: JPG, PNG, WebP, GIF (최대 10MB)
- **이미지 블록 종류**: Full Width, Image with Text, Gallery

### 개발 환경
- **로컬 개발**: `docker-compose up`
- **관리자 접속**: http://localhost:8000/admin/
- **프론트엔드**: http://localhost:8000/

### 배포 관련
- **배포 절차**: [DEPLOYMENT_RUNBOOK.md](DEPLOYMENT_RUNBOOK.md)
- **환경별 설정**: `config/settings/`
- **장애 대응**: [DISASTER_RECOVERY.md](DISASTER_RECOVERY.md)

## 📞 지원 및 연락처

### 도움이 필요한 경우

| 이슈 유형 | 연락 방법 | 응답 시간 |
|-----------|-----------|-----------|
| **긴급 장애** | Slack #emergency | 즉시 |
| **기능 문의** | GitHub Issues | 24시간 내 |
| **문서 관련** | seoul@pyladies.com | 48시간 내 |

### 팀 연락처
- **Tech Lead**: tech-lead@pyladies.com
- **Content Manager**: content@pyladies.com  
- **DevOps**: devops@pyladies.com

## 📋 문서 상태

| 문서 | 상태 | 마지막 업데이트 | 담당자 |
|------|------|----------------|--------|
| IMAGE_QUICK_GUIDE.md | ✅ 완료 | 2024-12-24 | Tech Team |
| IMAGE_MANAGEMENT.md | ✅ 완료 | 2024-12-24 | Tech Team |  
| DEPLOYMENT_RUNBOOK.md | ✅ 완료 | 2024-12-24 | DevOps Team |
| DISASTER_RECOVERY.md | ✅ 완료 | 2024-12-24 | DevOps Team |

---

**📅 마지막 업데이트**: 2024년 12월 24일  
**👥 관리팀**: PyLadies Seoul Tech Team  
**📧 문의**: seoul@pyladies.com