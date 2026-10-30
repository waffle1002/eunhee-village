# 은희 빌리지 배포 준비 (은희가 할 일)

## 1. GitHub
1. github.com 에서 New repository, 이름 예: eunhee-village, Public 으로 만들기
2. 저장소 이름을 Claude에게 알려주기 (나머지 올리기는 Claude가 해요)

## 2. Firebase (무료 Spark 요금제)
1. https://console.firebase.google.com 에서 프로젝트 추가 (애널리틱스는 꺼도 돼요)
2. 왼쪽 메뉴 빌드 > Authentication > 시작하기
   - 로그인 방법에서 "익명" 사용 설정
   - "Google" 도 사용 설정 (은희 연구소 로그인용)
3. 빌드 > Realtime Database > 데이터베이스 만들기
   - 위치는 싱가포르(asia-southeast1) 추천, "잠금 모드"로 시작
4. 프로젝트 설정(톱니바퀴) > 내 앱 > 웹(</>) 앱 추가, 호스팅 체크는 안 해도 돼요
5. 나오는 firebaseConfig 코드를 통째로 복사해서 Claude에게 보내기

보안 규칙(database.rules.json)과 GitHub Pages 주소 허용은 Claude가 안내하거나 대신 해요.
