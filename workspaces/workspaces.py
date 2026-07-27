import reflex as rx

from .pages.home import home
from .pages.result import result

# 테마(라이트 고정)는 rxconfig.py의 RadixThemesPlugin에서 설정한다 — App(theme=...)은 0.9.0에서 deprecated.
app = rx.App(stylesheets=["styles.css"])
app.add_page(home, route="/", title="백의 - 보이스피싱 문구 탐지")
app.add_page(result, route="/result", title="분석 결과 - 백의")
