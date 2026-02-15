import flet as ft
import datetime
import base64
import firebase_admin
from firebase_admin import credentials, firestore, storage

# ПОДКЛЮЧЕНИЕ ТВОЕГО FIREBASE
try:
    # serviceAccountKey.json должен быть в корне репозитория!
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred, {
        'storageBucket': 'ghost-pro-5aa22.firebasestorage.app'
    })
    db = firestore.client()
    bucket = storage.bucket()
except:
    print("Ошибка: Добавь serviceAccountKey.json!")

def main(page: ft.Page):
    page.title = "GHOST PRO V13"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#000000"
    
    state = {"uid": None, "role": "USER"}

    # ПИКЕР ДЛЯ РЕАЛЬНЫХ ФОТО/ГС
    def upload_file(e: ft.FilePickerResultEvent):
        if e.files:
            for f in e.files:
                blob = bucket.blob(f"ghost_files/{f.name}")
                blob.upload_from_filename(f.path)
                blob.make_public()
                db.collection("ghost_chat").add({
                    "user": state["uid"], "url": blob.public_url,
                    "type": "media", "ts": firestore.SERVER_TIMESTAMP
                })

    picker = ft.FilePicker(on_result=upload_file)
    page.overlay.append(picker)

    chat_list = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True)

    def show_chat():
        page.clean()
        msg_in = ft.TextField(hint_text=">>> CRYPT_DATA", expand=True, border_color="#00FF00")
        
        def send(e):
            if msg_in.value:
                db.collection("ghost_chat").add({
                    "user": state["uid"], "text": msg_in.value,
                    "type": "text", "ts": firestore.SERVER_TIMESTAMP
                })
                msg_in.value = ""
                page.update()

        page.add(ft.Column([
            ft.Row([
                ft.Text("GHOST_NET_V13", color="#00FF00", size=22, weight="bold"),
                ft.IconButton(ft.icons.ADMIN_PANEL_SETTINGS, icon_color="red", visible=state["role"]=="ADMIN")
            ], justify="spaceBetween"),
            ft.Container(content=chat_list, expand=True, border=ft.border.all(1, "#002200")),
            ft.Row([
                ft.IconButton(ft.icons.ADD_A_PHOTO, on_click=lambda _: picker.pick_files()),
                msg_in,
                ft.IconButton(ft.icons.SEND, on_click=send)
            ])
        ], expand=True, padding=10))

        db.collection("ghost_chat").order_by("ts").on_snapshot(lambda docs, c, t: (
            chat_list.controls.clear(),
            [chat_list.controls.append(ft.Text(f"{d.to_dict().get('user')}: {d.to_dict().get('text', 'FILE')}", color="white")) for d in docs],
            page.update()
        ))

    def login(e):
        if uid_in.value == "adminpan" and key_in.value == "TimaIssam2026":
            state["uid"], state["role"] = "@ADMIN_CORE", "ADMIN"
        else: state["uid"] = f"@{uid_in.value}"
        show_chat()

    uid_in = ft.TextField(label="UID/EMAIL", border_color="#00FF00")
    key_in = ft.TextField(label="KEY", password=True, border_color="#00FF00")
    page.add(ft.Column([
        ft.Icon(ft.icons.SECURITY, size=100, color="#00FF00"),
        ft.Text("GHOST_SYSTEM", size=30, weight="bold"),
        uid_in, key_in,
        ft.ElevatedButton("INIT_SESSION", on_click=login, width=300)
    ], horizontal_alignment="center"))

ft.app(target=main)
