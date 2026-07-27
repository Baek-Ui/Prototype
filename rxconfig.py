import reflex as rx

config = rx.Config(
    app_name="workspaces",
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
        # 라이트 테마 단일 팔레트(Task 7 확정). 지정하지 않으면 Radix 기본
        # 컴포넌트가 시스템 설정을 따라 다크로 렌더링되어 토큰과 어긋난다.
        rx.plugins.RadixThemesPlugin(
            theme=rx.theme(appearance="light", accent_color="blue")
        ),
    ]
)