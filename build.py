"""아티팩트용 ../index.html 을 배포용 index.html 로 바꿔요. python3 build.py"""
import pathlib
here = pathlib.Path(__file__).parent
s = (here.parent / 'index.html').read_text(encoding='utf-8')

head = '''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="description" content="은희를 소개합니다. 픽셀 마을 은희 빌리지">
<meta property="og:title" content="은희 빌리지">
<meta property="og:description" content="놀다 가요 ~ 캐릭터 만들고 방명록 남기기">
'''
s = s.replace('<meta name="claude:viewport-fit-sides" content="cover">\n', '')
fb = '''<script src="https://www.gstatic.com/firebasejs/10.12.2/firebase-app-compat.js"></script>
<script src="https://www.gstatic.com/firebasejs/10.12.2/firebase-auth-compat.js"></script>
<script src="https://www.gstatic.com/firebasejs/10.12.2/firebase-database-compat.js"></script>
<script src="firebase-config.js"></script>
<script src="firebase-shim.js"></script>
'''
i = s.index('<script>')
style_end = s.index('</style>') + len('</style>')
s = head + s[:style_end] + '\n</head>\n<body>\n' + s[style_end:i] + fb + s[i:] + '\n</body>\n</html>\n'

# 은희 로그인 / 로그아웃 버튼
old = '<p class="small" id="lab-msg"></p>'
assert old in s
s = s.replace(old, old + '\n      ${window.villageOwnerLogin ? `<p class="small"><button type="button" class="linkbtn" onclick="villageOwnerLogin()">주인장 로그인</button></p>` : \'\'}')
old = '<p class="owner-only">${pixIcon(\'star\')}은희만 보이는 화면이에요</p>'
assert old in s
s = s.replace(old, old + '\n    ${window.villageLogout ? `<p class="small"><button type="button" class="linkbtn" onclick="villageLogout()">로그아웃</button></p>` : \'\'}')

(here / 'index.html').write_text(s, encoding='utf-8')
print('built', len(s))
