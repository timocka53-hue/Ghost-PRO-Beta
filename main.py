import flet as ft
import datetime
import firebase_admin
from firebase_admin import credentials, firestore

def main(page: ft.Page):
    # НАСТРОЙКИ СИСТЕМЫ
    page.title = "Ghost PRO"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#000000"
    page.padding = 10
    
    # ПЕРЕМЕННЫЕ СОСТОЯНИЯ
    state = {
        "uid": None, 
        "role": "USER", 
        "active_chat": "GLOBAL",
        "db": None
    }

    # ГРАФИЧЕСКИЕ ЭЛЕМЕНТЫ
    chat_display = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True, spacing=10)
    msg_input = ft.TextField(
        hint_text="Введите зашифрованный сигнал...", 
        expand=True, 
        border_color="#00FF00",
        color="#00FF00"
    )

    # ИНИЦИАЛИЗАЦИЯ БАЗЫ (Защита от черного экрана)
    try:
        if not firebase_admin._apps:
            cred = credentials.Certificate("serviceAccountKey.json")
            firebase_admin.initialize_app(cred)
        state["db"] = firestore.client()
    except Exception as e:
        print(f"Критическая ошибка: {e}")

    # --- ФУНКЦИИ ПРИВЕЛЕГИЙ ---
    def send_message(e):
        if msg_input.value and state["db"]:
            state["db"].collection("messages").add({
                "user": state["uid"],
                "text": msg_input.value,
                "ts": firestore.SERVER_TIMESTAMP,
                "role": state["role"]
            })
            msg_input.value = ""
            page.update()

    def load_messages():
        if state["db"]:
            # Слушаем обновления в реальном времени
            def on_snapshot(docs, changes, read_time):
                chat_display.controls.clear()
                for doc in docs:
                    m = doc.to_dict()
                    is_admin = m.get("role") == "ADMIN"
                    chat_display.controls.append(
                        ft.Container(
                            content=ft.Column([
                                ft.Text(m.get("user"), size=10, color="#00FF00" if is_admin else "#555555"),
                                ft.Text(m.get("text"), color="white", size=16),
                            ]),
                            padding=10,
                            bgcolor="#0A0A0A",
                            border=ft.border.all(1, "#00FF00" if is_admin else "#222222"),
                            border_radius=10
                        )
                    )
                page.update()
            
            state["db"].collection("messages").order_by("ts", descending=False).limit_to_last(20).on_snapshot(on_snapshot)

    # --- ЭКРАНЫ ---
    def show_login():
        u_in = ft.TextField(label="USER ID", border_color="#00FF00")
        p_in = ft.TextField(label="ADMIN KEY (Optional)", password=True, border_color="#00FF00")
        
        def login_click(e):
            if u_in.value:
                state["uid"] = f"@{u_in.value}"
                # Твоя админка
                if u_in.value == "adminpan" and p_in.value == "TimaIssam2026":
                    state["role"] = "ADMIN"
                show_chat()
                load_messages()

        page.clean()
        page.add(
            ft.Container(
                content=ft.Column([
                    ft.Text("GHOST PRO", size=50, weight="bold", color="#00FF00"),
                    ft.Text("ENCRYPTED NETWORK V13", size=12, color="#00FF00"),
                    ft.Divider(height=40, color="transparent"),
                    u_in, p_in,
                    ft.ElevatedButton("CONNECT SYSTEM", on_click=login_click, bgcolor="#002200", color="#00FF00", width=300)
                ], horizontal_alignment="center"),
                alignment=ft.alignment.center, expand=True
            )
        )

    def show_chat():
        page.clean()
        page.add(
            ft.Column([
                ft.Row([
                    ft.Text(f"SYSTEM ACTIVE: {state['uid']}", color="#00FF00", weight="bold"),
                    ft.Icon(ft.icons.VERIFIED if state["role"] == "ADMIN" else ft.icons.PERSON, color="#00FF00")
                ], justify="spaceBetween"),
                ft.Container(content=chat_display, expand=True),
                ft.Row([
                    ft.IconButton(ft.icons.SEARCH, icon_color="#00FF00"), # Поиск юзеров
                    msg_input,
                    ft.IconButton(ft.icons.SEND_ROUNDED, icon_color="#00FF00", on_click=send_message)
                ])
            ], expand=True)
        )

    show_login()

ft.app(target=main)
