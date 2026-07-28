import reflex as rx

config = rx.Config(
    app_name="workspaces",
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
        # 기본 다크. 사용자가 네비바에서 라이트로 바꿀 수 있고 선택은
        # localStorage에 남는다. appearance를 "inherit"으로 두면 Radix
        # 컴포넌트가 시스템 설정을 따라가 우리 토큰과 어긋나므로 명시한다.
        # accent_color는 Radix 자체 컴포넌트(callout 등)용 — DESIGN.md의
        # 인디고/퍼플에 가장 가까운 iris를 쓴다.
        rx.plugins.RadixThemesPlugin(
            theme=rx.theme(appearance="dark", accent_color="iris")
        ),
    ]
)