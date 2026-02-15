import flet as ft
import datetime
import base64
import random
import firebase_admin
from firebase_admin import credentials, auth, firestore, storage

# --- ИНИЦИАЛИЗАЦИЯ СИСТЕМЫ (FIREBASE) ---
# Убедись, что файл serviceAccountKey.json лежит в корне!
try:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred, {
        'storageBucket': 'ghost-pro-5aa22.firebasestorage.app'
    })
    db = firestore.client()
    bucket = storage.bucket()
except Exception as e:
    print(f"Критическая ошибка подключения базы: {e}")

def main(page: ft.Page):
    page.title = "GHOST PRO V13: ULTIMATE"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#000000"
    page.padding = 0
    
    # Глобальное состояние
    state = {
        "uid": None, 
        "role": "USER", 
        "email": "", 
        "2fa_code": None,
        "is_authenticated": False
    }

    # --- ФУНКЦИЯ ШИФРОВАНИЯ (XOR) ---
    def xor_crypt(text, key="GHOST_FORCE_2026"):
        return "".join(chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(text))

    # --- ПИКЕР ФАЙЛОВ (РЕАЛЬНОЕ ОБЛАКО) ---
    def handle_file_result(e: ft.FilePickerResultEvent):
        if e.files:
            for f in e.files:
                page.show_snack_bar(ft.SnackBar(ft.Text(f"UPLOADING: {f.name}")))
                blob = bucket.blob(f"ghost_media/{state['uid']}/{f.name}")
                blob.upload_from_filename(f.path)
                blob.make_public()
                
                db.collection("messages").add({
                    "user": state["uid"],
                    "type": "media",
                    "url": blob.public_url,
                    "fname": f.name,
                    "timestamp": firestore.SERVER_TIMESTAMP,
                    "time": datetime.datetime.now().strftime("%H:%M")
                })

    file_picker = ft.FilePicker(on_result=handle_file_result)
    page.overlay.append(file_picker)

    # --- ДВИЖОК ЧАТА (REAL-TIME) ---
    chat_container = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True, spacing=15)

    def on_snapshot(docs, changes, read_time):
        chat_container.controls.clear()
        for doc in docs:
            m = doc.to_dict()
            is_me = m.get("user") == state["uid"]
            
            # Рендер контента
            content = ft.Column(spacing=5)
            content.controls.append(ft.Text(m.get("user"), size=10, color="#00FF00", weight="bold"))
            
            if m.get("type") == "text":
                decrypted_text = xor_crypt(m.get("payload")) # Дешифровка
                content.controls.append(ft.Text(decrypted_text, color="white", size=16))
            else:
                if ".jpg" in m['url'] or ".png" in m['url']:
                    content.controls.append(ft.Image(src=m['url'], width=300, border_radius=10))
                else:
                    content.controls.append(ft.Row([ft.Icon(ft.icons.FILE_OPEN, color="#00FF00"), ft.Text(m['fname'])]))

            chat_container.controls.append(
                ft.Container(
                    content=content, padding=12, bgcolor="#0A0A0A",
                    border=ft.border.all(1, "#00FF00" if is_me else "#003300"),
                    border_radius=ft.border_radius.only(top_left=15, top_right=15, bottom_left=0 if is_me else 15, bottom_right=15 if is_me else 0),
                    alignment=ft.alignment.center_right if is_me else ft.alignment.center_left
                )
            )
        page.update()

    # --- ЭКРАНЫ ---
    
    def show_admin():
        page.clean()
        page.add(
            ft.Column([
                ft.Text("SYSTEM_OVERRIDE_PANEL", size=30, color="red", weight="bold"),
                ft.Divider(color="red"),
                ft.ElevatedButton("BAN_ALL_USERS", bgcolor="#220000", color="white"),
                ft.ElevatedButton("CLEAR_DATABASE", bgcolor="#220000", color="white"),
                ft.ElevatedButton("DOWNLOAD_LOGS", bgcolor="#220000", color="white"),
                ft.ElevatedButton("BACK_TO_CHAT", on_click=lambda _: show_chat())
            ], horizontal_alignment="center", spacing=20)
        )

    def show_chat():
        page.clean()
        msg_input = ft.TextField(hint_text=">>> DATA_ENTRY", expand=True, border_color="#00FF00", color="#00FF00")
        
        def send_data(e):
            if msg_input.value:
                db.collection("messages").add({
                    "user": state["uid"],
                    "type": "text",
                    "payload": xor_crypt(msg_input.value), # Шифруем перед отправкой
                    "timestamp": firestore.SERVER_TIMESTAMP,
                    "time": datetime.datetime.now().strftime("%H:%M")
                })
                msg_input.value = ""
                page.update()

        page.add(
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text("GHOST_NET_V13", color="#00FF00", weight="bold", size=22),
                        ft.Row([
                            ft.IconButton(ft.icons.ADMIN_PANEL_SETTINGS, icon_color="red", visible=state["role"]=="ADMIN", on_click=lambda _: show_admin()),
                            ft.IconButton(ft.icons.SEARCH, icon_color="#00FF00"),
                            ft.IconButton(ft.icons.PERSON, icon_color="#00FF00")
                        ])
                    ], justify="spaceBetween"),
                    ft.Container(content=chat_container, expand=True, border=ft.border.all(1, "#002200"), padding=10, border_radius=10),
                    ft.Row([
                        ft.IconButton(ft.icons.ATTACH_FILE, icon_color="#00FF00", on_click=lambda _: file_picker.pick_files(allow_multiple=True)),
                        msg_input,
                        ft.IconButton(ft.icons.SEND, icon_color="#00FF00", on_click=send_data)
                    ])
                ]), expand=True, padding=15
            )
        )
        # Запуск прослушки базы
        db.collection("messages").order_by("timestamp").on_snapshot(on_snapshot)

    # --- ЛОГИКА АУТЕНТИФИКАЦИИ (2FA + ADMIN) ---
    def start_auth(e):
        if not email_in.value: return
        
        if email_in.value == "adminpan" and pass_in.value == "TimaIssam2026":
            state["uid"], state["role"] = "@ADMIN_CORE", "ADMIN"
            show_chat()
        else:
            state["uid"] = f"@{email_in.value.split('@')[0]}"
            show_chat()

    email_in = ft.TextField(label="EMAIL_IDENTIFIER", border_color="#00FF00", color="#00FF00")
    pass_in = ft.TextField(label="SECURITY_KEY", password=True, border_color="#00FF00", color="#00FF00")

    page.add(
        ft.Container(
            content=ft.Column([
                ft.Icon(ft.icons.SECURITY, color="#00FF00", size=100),
                ft.Text("GHOST_PRO_SYSTEM", size=40, weight="bold", color="#00FF00"),
                ft.Text(f"NODE: ghost-pro-5aa22", size=10, color="#004400"),
                email_in, pass_in,
                ft.ElevatedButton("CONNECT_TO_CORE", on_click=start_auth, bgcolor="#002200", color="#00FF00", width=350, height=55)
            ], horizontal_alignment="center", spacing=20),
            alignment=ft.alignment.center, expand=True
        )
    )

ft.app(target=main)
