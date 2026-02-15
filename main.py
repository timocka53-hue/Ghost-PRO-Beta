import flet as ft
import datetime
import firebase_admin
from firebase_admin import credentials, firestore

def main(page: ft.Page):
    # УСТАНОВКА НАЗВАНИЯ И ДИЗАЙНА
    page.title = "Ghost PRO"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#000000"
    page.padding = 0
    page.window_resizable = False

    # Инициализация Firebase (с защитой от вылета)
    db = None
    try:
        if not firebase_admin._apps:
            cred = credentials.Certificate("serviceAccountKey.json")
            firebase_admin.initialize_app(cred)
        db = firestore.client()
    except Exception as e:
        print(f"Firebase Offline: {e}")

    state = {"uid": None, "active_chat": None}

    # ГРАФИКА: ЭКРАН ВХОДА
    def login_screen():
        page.clean()
        user_in = ft.TextField(label="USER_ID", border_color="#00FF00", width=280)
        pass_in = ft.TextField(label="ACCESS_KEY", password=True, border_color="#00FF00", width=280)
        
        def connect_click(e):
            if user_in.value:
                state["uid"] = f"@{user_in.value}"
                messenger_ui()

        page.add(
            ft.Container(
                content=ft.Column([
                    ft.Text("GHOST PRO", size=45, weight="bold", color="#00FF00", italic=True),
                    ft.Text("MATRIX ENCRYPTED NETWORK", size=12, color="#00FF00"),
                    ft.Divider(height=20, color="transparent"),
                    user_in, pass_in,
                    ft.ElevatedButton("INITIALIZE", on_click=connect_click, bgcolor="#002200", color="#00FF00", width=280)
                ], horizontal_alignment="center"),
                alignment=ft.alignment.center, expand=True
            )
        )

    # ГРАФИКА: ОСНОВНОЙ МЕССЕНДЖЕР (ДИЗАЙН)
    def messenger_ui():
        page.clean()
        chat_area = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True)
        msg_input = ft.TextField(hint_text="CRYPT_MSG...", expand=True, border_color="#00FF00")

        def send_msg(e):
            if msg_input.value and db:
                db.collection("public_chat").add({
                    "user": state["uid"],
                    "text": msg_input.value,
                    "ts": firestore.SERVER_TIMESTAMP
                })
                msg_input.value = ""
                page.update()

        page.add(
            ft.Column([
                ft.Container(
                    content=ft.Row([
                        ft.Text("GHOST PRO V13", color="#00FF00", weight="bold"),
                        ft.Icon(ft.icons.CIRCLE, color="green", size=10)
                    ], justify="spaceBetween"),
                    padding=15, bgcolor="#111111"
                ),
                ft.Container(content=chat_area, expand=True, padding=20),
                ft.Container(
                    content=ft.Row([
                        ft.IconButton(ft.icons.ADD_BOX_OUTLINED, icon_color="#00FF00"),
                        msg_input,
                        ft.IconButton(ft.icons.SEND_ROUNDED, icon_color="#00FF00", on_click=send_msg)
                    ]),
                    padding=10, bgcolor="#050505"
                )
            ], expand=True)
        )

    login_screen()

ft.app(target=main)
