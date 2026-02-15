import flet as ft
import datetime
import firebase_admin
from firebase_admin import credentials, firestore

def main(page: ft.Page):
    # Чистое название без лишних знаков
    page.title = "Ghost PRO"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#000000"
    page.padding = 10

    # Защита от черного экрана: рисуем фон сразу
    container = ft.Column(expand=True)
    page.add(container)

    # Тихая инициализация базы
    db = None
    try:
        if not firebase_admin._apps:
            cred = credentials.Certificate("serviceAccountKey.json")
            firebase_admin.initialize_app(cred)
        db = firestore.client()
    except Exception as e:
        container.controls.append(ft.Text(f"Offline Mode: {e}", color="red"))
        page.update()

    state = {"uid": None}

    def login_view():
        user_in = ft.TextField(label="USER_ID", border_color="#00FF00")
        
        def start(e):
            if user_in.value:
                state["uid"] = f"@{user_in.value}"
                chat_view()

        container.controls.clear()
        container.controls.append(
            ft.Column([
                ft.Text("GHOST PRO", size=40, color="#00FF00", weight="bold"),
                user_in,
                ft.ElevatedButton("CONNECT", on_click=start, bgcolor="#002200", color="#00FF00")
            ], horizontal_alignment="center")
        )
        page.update()

    def chat_view():
        chat_list = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True)
        msg_in = ft.TextField(hint_text="Message...", expand=True)

        def send(e):
            if msg_in.value and db:
                db.collection("public").add({
                    "user": state["uid"],
                    "text": msg_in.value,
                    "ts": firestore.SERVER_TIMESTAMP
                })
                msg_in.value = ""
                page.update()

        container.controls.clear()
        container.controls.append(
            ft.Column([
                ft.Text(f"LOGGED AS: {state['uid']}", color="#00FF00"),
                ft.Container(content=chat_list, expand=True),
                ft.Row([msg_in, ft.IconButton(ft.icons.SEND, on_click=send)])
            ], expand=True)
        )
        page.update()

    login_view()

ft.app(target=main)
