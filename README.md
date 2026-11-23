# 보건 데일리 — 인터넷 접속형

## 기능
8개 분야 키워드 기반 Google 뉴스 RSS 수집, 중복 제거, 90일 저장, 기간/분야/검색 필터, 브라우저별 즐겨찾기·읽음 표시. **AI 요약 및 법령 검증 기능은 포함하지 않습니다.** RSS가 제공하는 설명만 표시합니다. 채용 등 일부 검색 결과는 누락되거나 오분류될 수 있습니다.

## GitHub에 올리기 (회사 정책상 외부 서비스 이용이 허용된 경우에만)
1. https://github.com 에 로그인하고 **New repository** 선택.
2. Repository name: `health-daily` / **Public** / Create repository. Public 저장소의 코드와 수집 데이터는 누구나 볼 수 있습니다. 개인·회사 기밀은 올리지 마세요.
3. 생성한 저장소에서 **uploading an existing file** 또는 **Add file → Upload files**를 클릭합니다.
4. 압축을 풀어 나온 `health_daily_cloud` 폴더 **안의 파일과 `.github` 폴더**를 업로드합니다. `.github/workflows/update.yml`이 정확한 경로에 있어야 합니다. (Windows에서 숨김 폴더가 안 보이면 파일 탐색기 보기 → 숨긴 항목 표시.) `Commit changes` 클릭.
5. 저장소 **Settings → Pages → Build and deployment → Source: Deploy from a branch → Branch: main / (root) → Save**.
6. 저장소 **Actions → Update health news → Run workflow**를 눌러 최초 수집을 실행합니다. 실행 후 `news.json`이 갱신되는지 확인합니다.
7. 웹앱 주소는 `https://사용자이름.github.io/health-daily/` 형식입니다. Pages 게시까지 수 분 걸릴 수 있습니다.
8. **Settings → Actions → General → Workflow permissions**에서 `Read and write permissions`를 허용해야 데이터 자동 커밋이 가능한 저장소 설정도 있습니다. 조직 정책이 이를 막으면 관리자 승인이 필요합니다.

## 자동수집
GitHub Actions의 cron `0 23 * * *`는 **한국시간 다음 날 오전 8시**에 해당합니다. GitHub 예약 작업은 부하로 인해 지연되거나 누락될 수 있어 정시 실행을 보장하지 않습니다. 공개 저장소에서 장기간 활동이 없으면 예약 작업이 비활성화될 수 있습니다. `Actions` 탭에서 마지막 실행과 실패 여부를 주기적으로 확인하세요.

## 주의사항
- PC를 꺼도 GitHub에서 수집을 실행하지만, GitHub 서비스/네트워크 및 RSS 제공자의 정상 동작에 의존합니다.
- Google 뉴스 RSS는 공식 정부기관 원문 API가 아니며 검색 결과가 정확하거나 완전하다고 보장하지 않습니다.
- 수집된 링크가 Google 뉴스 중간 페이지를 거칠 수 있습니다.
- 즐겨찾기/읽음은 사용 중인 **브라우저에만** 저장되며 다른 기기와 동기화되지 않습니다.
- 보건관리자 개인용 공개자료 열람을 전제로 설계되었습니다. 개인정보, 직원 건강정보, 회사 기밀은 업로드하지 마세요.
- GitHub Pages가 사내 보안 정책상 허용되는지 확인하세요.
- 기존 PC의 `health_daily_app` 폴더를 덮어쓰지 마세요. 이전 뉴스 7건은 자동으로 이전되지 않습니다.

## 비용
기본 기능은 GitHub의 무료 범위 내에서 운영할 수 있지만 서비스 정책과 사용량에 따라 제한이 달라질 수 있습니다.
