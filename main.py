import flet as ft
import datetime
import base64
import firebase_admin
from firebase_admin import credentials, firestore, storage, auth

# ПОДКЛЮЧЕНИЕ FIREBASE
try:
    # Файл serviceAccountKey.json должен быть в корне репозитория!
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred, {
        'storageBucket': 'ghost-pro-5aa22.firebasestorage.app'
    })
    db = firestore.client()
    bucket = storage.bucket()
except Exception as e:
    print(f"Ошибка связи с Firebase: {e}")

def main(page: ft.Page):
    page.title = "GHOST PRO V13"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#000000"
    page.padding = 0

    state = {"uid": None, "role": "USER", "email": ""}

    # РАБОТА С МЕДИА (ФОТО, ГС, ВИДЕО)
    def upload_media(e: ft.FilePickerResultEvent):
        if e.files:
            for f in e.files:
                blob = bucket.blob(f"vault/{state['uid']}/{f.name}")
                blob.upload_from_filename(f.path)
                blob.make_public()
                db.collection("messages").add({
                    "user": state["uid"],
                    "url": blob.public_url,
                    "type": "media",
                    "time": datetime.datetime.now().strftime("%H:%M"),
                    "ts": firestore.SERVER_TIMESTAMP
                })

    picker = ft.FilePicker(on_result=upload_media)
    page.overlay.append(picker)

    # ЧАТ И АДМИНКА
    chat_list = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True)

    def show_admin():
        page.clean()
        page.add(ft.Column([
            ft.Text("ADMIN_PANEL", size=30, color="red", weight="bold"),
            ft.ElevatedButton("BAN_USER", bgcolor="red", color="white"),
            ft.ElevatedButton("WIPE_ALL_CHAT", on_click=lambda _: None),
            ft.ElevatedButton("BACK", on_click=lambda _: show_chat())
        ], horizontal_alignment="center"))

    def show_chat():
        page.clean()
        msg_in = ft.TextField(hint_text=">>> DATA", expand=True, border_color="#00FF00")
        
        def send(e):
            if msg_in.value:
                db.collection("messages").add({
                    "user": state["uid"], "text": msg_in.value, "type": "text",
                    "time": datetime.datetime.now().strftime("%H:%M"),
                    "ts": firestore.SERVER_TIMESTAMP
                })
                msg_in.value = ""
                page.update()

        page.add(ft.Container(content=ft.Column([
            ft.Row([
                ft.Text("GHOST_NET", color="#00FF00", size=20, weight="bold"),
                ft.IconButton(ft.icons.ADMIN_PANEL_SETTINGS, icon_color="red", visible=state["role"]=="ADMIN", on_click=lambda _: show_admin())
            ], justify="spaceBetween"),
            ft.Container(content=chat_list, expand=True, border=ft.border.all(1, "#002200")),
            ft.Row([ft.IconButton(ft.icons.ADD, on_click=lambda _: picker.pick_files()), msg_in, ft.IconButton(ft.icons.SEND, on_click=send)])
        ]), expand=True, padding=10))
        
        db.collection("messages").order_by("ts").on_snapshot(lambda docs, c, t: (
            chat_list.controls.clear(),
            [chat_list.controls.append(ft.Text(f"{d.to_dict().get('user')}: {d.to_dict().get('text', 'MEDIA')}", color="white")) for d in docs],
            page.update()
        ))

    # ВХОД (adminpan / TimaIssam2026)
    def login(e):
        if log_in.value == "adminpan" and pass_in.value == "TimaIssam2026":
            state["uid"], state["role"] = "@ADMIN_CORE", "ADMIN"
            show_chat()
        elif log_in.value:
            state["uid"] = f"@{log_in.value}"
            show_chat()

    log_in = ft.TextField(label="UID/EMAIL", border_color="#00FF00")
    pass_in = ft.TextField(label="KEY", password=True, border_color="#00FF00")
    page.add(ft.Column([ft.Icon(ft.icons.SECURITY, size=80, color="#00FF00"), log_in, pass_in, ft.ElevatedButton("INIT", on_click=login)], horizontal_alignment="center"))

ft.app(target=main)
