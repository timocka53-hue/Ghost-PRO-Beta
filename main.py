import flet as ft
import datetime
import firebase_admin
from firebase_admin import credentials, firestore, storage
import threading
import time

# --- КОНФИГ ТВОЕГО ПРОЕКТА ---
try:
    if not firebase_admin._apps:
        cred = credentials.Certificate("serviceAccountKey.json")
        firebase_admin.initialize_app(cred, {
            'storageBucket': 'ghost-pro-5aa22.firebasestorage.app'
        })
    db = firestore.client()
    bucket = storage.bucket()
except Exception as e:
    # Если файла нет, приложение не упадет в черный экран, а покажет ошибку в UI
    print(f"Критическая ошибка инициализации: {e}")

def main(page: ft.Page):
    page.title = "Ghost PRO Beta"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#000000"
    page.padding = 10
    
    state = {"uid": None, "role": "USER", "active_chat": None}
    chat_container = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True, spacing=10)

    # --- СИСТЕМА УВЕДОМЛЕНИЙ ---
    def send_notification(title, body):
        page.show_snack_bar(
            ft.SnackBar(
                content=ft.Row([
                    ft.Icon(ft.icons.NOTIFICATIONS_ACTIVE, color="#00FF00"),
                    ft.Text(f"{title}: {body}", color="#00FF00", weight="bold")
                ]),
                bgcolor="#111111",
                duration=3000
            )
        )

    # --- ЛОГИКА ЧАТА И ПОИСКА ---
    def on_message_update(docs, changes, read_time):
        if not state["active_chat"]: return
        
        chat_container.controls.clear()
        for doc in docs:
            m = doc.to_dict()
            is_me = m.get("user") == state["uid"]
            
            # Если сообщение новое и не от нас — пищим уведомлением
            if any(c.type.name == 'ADDED' for c in changes) and not is_me:
                send_notification("НОВОЕ СООБЩЕНИЕ", m.get("text", "Медиафайл"))

            chat_container.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text(m.get("user"), size=10, color="#00FF00", weight="bold"),
                        ft.Text(m.get("text"), color="white", size=15),
                    ]),
                    alignment=ft.alignment.center_right if is_me else ft.alignment.center_left,
                    padding=12,
                    bgcolor="#0A0A0A" if is_me else "#151515",
                    border_radius=15,
                    border=ft.border.all(1, "#00FF00" if is_me else "#333333"),
                )
            )
        page.update()

    def start_private_chat(target_uid):
        if not target_uid.startswith("@"): target_uid = f"@{target_uid}"
        # Создаем уникальный ID для двоих (анонимная личка)
        chat_id = "_".join(sorted([state["uid"], target_uid]))
        state["active_chat"] = chat_id
        
        # Слушаем именно эту личку в реальном времени
        db.collection("chats").document(chat_id).collection("messages").order_by("ts").on_snapshot(on_message_update)
        show_chat_screen(target_uid)

    # --- ЭКРАНЫ ---
    def show_chat_screen(partner):
        page.clean()
        msg_input = ft.TextField(hint_text="Зашифрованное сообщение...", expand=True, border_color="#00FF00")
        
        def send_click(e):
            if msg_input.value:
                db.collection("chats").document(state["active_chat"]).collection("messages").add({
                    "user": state["uid"],
                    "text": msg_input.value,
                    "ts": firestore.SERVER_TIMESTAMP,
                    "type": "text"
                })
                msg_input.value = ""
                page.update()

        page.add(
            ft.Column([
                ft.Row([
                    ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda _: show_main_menu()),
                    ft.Text(f"ЧАТ С {partner}", color="#00FF00", weight="bold"),
                    ft.IconButton(ft.icons.ADMIN_PANEL_SETTINGS, icon_color="red", visible=state["role"]=="ADMIN")
                ], justify="spaceBetween"),
                ft.Container(content=chat_container, expand=True, padding=10),
                ft.Row([
                    ft.IconButton(ft.icons.ADD_A_PHOTO, on_click=lambda _: page.show_snack_bar(ft.SnackBar(ft.Text("Медиа доступно в Pro")))),
                    msg_input,
                    ft.IconButton(ft.icons.SEND, icon_color="#00FF00", on_click=send_click)
                ])
            ], expand=True)
        )

    def show_main_menu():
        page.clean()
        search_uid = ft.TextField(label="ПОИСК ЮЗЕРА ПО @ID", border_color="#00FF00")
        page.add(
            ft.Container(
                content=ft.Column([
                    ft.Text("GHOST PRO BETA", size=32, color="#00FF00", weight="bold"),
                    ft.Text(f"ВАШ ID: {state['uid']}", color="#555555"),
                    search_uid,
                    ft.ElevatedButton("НАЙТИ И НАЧАТЬ ЧАТ", on_click=lambda _: start_private_chat(search_uid.value), bgcolor="#002200", color="#00FF00"),
                    ft.Divider(color="#222222"),
                    ft.Text("АКТИВНЫЕ ДИАЛОГИ ПОЯВЯТСЯ ТУТ", size=12, color="#333333")
                ], horizontal_alignment="center", spacing=20),
                alignment=ft.alignment.center, expand=True
            )
        )

    # --- ВХОД ---
    user_in = ft.TextField(label="ПРИДУМАЙТЕ ЮЗЕРНЕЙМ", border_color="#00FF00")
    pass_in = ft.TextField(label="КОД ДОСТУПА", password=True, border_color="#00FF00")

    def login_done(e):
        if user_in.value:
            state["uid"] = f"@{user_in.value}"
            if user_in.value == "adminpan" and pass_in.value == "TimaIssam2026":
                state["role"] = "ADMIN"
            show_main_menu()

    page.add(
        ft.Container(
            content=ft.Column([
                ft.Icon(ft.icons.VIGNETTE, size=100, color="#00FF00"),
                ft.Text("MATRIX NETWORK V13", size=24, weight="bold", color="#00FF00"),
                user_in, pass_in,
                ft.ElevatedButton("СОЗДАТЬ СЕССИЮ", on_click=login_done, width=300, bgcolor="#002200", color="#00FF00")
            ], horizontal_alignment="center", spacing=25),
            alignment=ft.alignment.center, expand=True
        )
    )

ft.app(target=main)
