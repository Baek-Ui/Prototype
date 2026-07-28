import reflex as rx

from .pages.home import home

# 라이트 시절에 localStorage["theme"]="light"를 저장한 브라우저는 기본값을
# 다크로 바꿔도 계속 라이트로 뜬다. Reflex의 개발용 last_compiled_theme
# 가드는 기본값이 바뀐 직후 딱 한 번만 동작하고 저장된 값을 지우지는 않아,
# 그 다음 새로고침부터 다시 옛 선택이 이긴다. 그래서 테마 정체성이 바뀐
# 시점을 epoch로 찍어 두고, 그보다 오래된 선택만 한 번 버린다. 이후
# 사용자가 직접 고른 테마는 정상적으로 유지된다.
_THEME_EPOCH_RESET = """
try {
  var epoch = 'baekui-dark-v1';
  if (localStorage.getItem('bu_theme_epoch') !== epoch) {
    localStorage.removeItem('theme');
    localStorage.removeItem('last_compiled_theme');
    localStorage.setItem('bu_theme_epoch', epoch);
  }
} catch (e) {}
"""

# 테마(기본 다크)는 rxconfig.py의 RadixThemesPlugin에서 설정한다 — App(theme=...)은 0.9.0에서 deprecated.
app = rx.App(
    stylesheets=["styles.css"],
    head_components=[rx.script(_THEME_EPOCH_RESET)],
)
# 랜딩 한 장이 곧 서비스다 — 입력·분석·리포트가 모두 "/" 안에서 일어난다.
app.add_page(home, route="/", title="백의 - 보이스피싱 문구 탐지")
