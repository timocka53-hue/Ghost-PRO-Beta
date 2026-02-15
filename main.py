import flet as ft
import datetime
import firebase_admin
from firebase_admin import credentials, firestore, storage

# КОНФИГ ТВОЕГО ПРОЕКТА
try:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred, {
        'storageBucket': 'ghost-pro-5aa22.firebasestorage.app'
    })
    db = firestore.client()
    bucket = storage.bucket()
except:
    print("Ошибка: Добавь serviceAccountKey.json!")

def main(page: ft.Page):
    page.title = "GHOST PRO V13: PRIVATE"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#000000"
    page.padding = 0

    state = {"uid": None, "role": "USER", "active_chat": None}

    # --- МЕДИА (ФОТО / ВИДЕО / ГС) ---
    def upload_media(e: ft.FilePickerResultEvent):
        if e.files and state["active_chat"]:
            for f in e.files:
                blob = bucket.blob(f"chats/{state['active_chat']}/{f.name}")
                blob.upload_from_filename(f.path)
                blob.make_public()
                
                db.collection("chats").document(state["active_chat"]).collection("messages").add({
                    "user": state["uid"],
                    "type": "media",
                    "url": blob.public_url,
                    "ts": firestore.SERVER_TIMESTAMP
                })

    picker = ft.FilePicker(on_result=upload_media)
    page.overlay.append(picker)

    # --- СПИСОК ЧАТОВ (ИКОНКИ СЛЕВА) ---
    side_bar = ft.Column(spacing=10, width=70)
    chat_area = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True)

    def load_chat(chat_id):
        state["active_chat"] = chat_id
        chat_area.controls.clear()
        page.update()
        
        # Слушаем сообщения только этого чата
        db.collection("chats").document(chat_id).collection("messages").order_by("ts").on_snapshot(render_messages)

    def render_messages(docs, changes, time):
        chat_area.controls.clear()
        for d in docs:
            m = d.to_dict()
            is_me = m.get("user") == state["uid"]
            content = ft.Text(m.get("text"), color="white") if m.get("type")=="text" else ft.Image(src=m.get("url"), width=200)
            
            chat_area.controls.append(
                ft.Container(
                    content=content,
                    alignment=ft.alignment.center_right if is_me else ft.alignment.center_left,
                    padding=10, bgcolor="#111111" if is_me else "#002200",
                    border_radius=10, border=ft.border.all(1, "#00FF00" if is_me else "#333333")
                )
            )
        page.update()

    # --- ПОИСК И СОЗДАНИЕ ЧАТА ---
    def start_new_chat(target_uid):
        if not target_uid.startswith("@"): target_uid = f"@{target_uid}"
        # Создаем уникальный ID чата (сортируем ники, чтобы ID был один для двоих)
        uids = sorted([state["uid"], target_uid])
        chat_id = f"{uids[0]}_{uids[1]}"
        
        # Добавляем иконку чата в сайдбар
        side_bar.controls.append(
            ft.IconButton(ft.icons.PERSON, icon_color="#00FF00", tooltip=target_uid, on_click=lambda _: load_chat(chat_id))
        )
        load_chat(chat_id)
        page.update()

    # --- ИНТЕРФЕЙС ГЛАВНОГО ЭКРАНА ---
    def show_messenger():
        page.clean()
        msg_in = ft.TextField(hint_text="Сообщение...", expand=True, border_color="#00FF00")
        search_in = ft.TextField(label="Найти @юз", border_color="#00FF00", width=200)

        def send(e):
            if msg_in.value and state["active_chat"]:
                db.collection("chats").document(state["active_chat"]).collection("messages").add({
                    "user": state["uid"], "text": msg_in.value, "type": "text", "ts": firestore.SERVER_TIMESTAMP
                })
                msg_in.value = ""
                page.update()

        page.add(
            ft.Row([
                # Левая панель (Чаты)
                ft.Container(content=side_bar, width=80, bgcolor="#050505", padding=10),
                # Правая панель (Переписка)
                ft.Column([
                    ft.Row([
                        search_in,
                        ft.IconButton(ft.icons.SEARCH, on_click=lambda _: start_new_chat(search_in.value)),
                        ft.IconButton(ft.icons.ADMIN_PANEL_SETTINGS, icon_color="red", visible=state["role"]=="ADMIN")
                    ]),
                    ft.Container(content=chat_area, expand=True),
                    ft.Row([
                        ft.IconButton(ft.icons.ADD_A_PHOTO, on_click=lambda _: picker.pick_files()),
                        msg_in,
                        ft.IconButton(ft.icons.SEND, on_click=send)
                    ])
                ], expand=True, padding=15)
            ], expand=True)
        )

    # --- ВХОД ---
    def login_go(e):
        if user_in.value:
            state["uid"] = f"@{user_in.value}"
            if user_in.value == "adminpan" and pass_in.value == "TimaIssam2026":
                state["role"] = "ADMIN"
            show_messenger()

    user_in = ft.TextField(label="ВАШ ЮЗЕРНЕЙМ", border_color="#00FF00")
    pass_in = ft.TextField(label="ПАРОЛЬ", password=True, border_color="#00FF00")
    page.add(
        ft.Container(
            content=ft.Column([
                ft.Icon(ft.icons.PHONELINK_LOCK, size=100, color="#00FF00"),
                ft.Text("GHOST PRIVATE NETWORK", size=30, weight="bold"),
                user_in, pass_in,
                ft.ElevatedButton("ВОЙТИ", on_click=login_go, width=300, bgcolor="#002200", color="#00FF00")
            ], horizontal_alignment="center", spacing=20),
            alignment=ft.alignment.center, expand=True
        )
    )

ft.app(target=main)
