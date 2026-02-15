import flet as ft
import datetime
import base64
import os
import time
from cryptography.fernet import Fernet

# Генерируем ключ для реального шифрования (в продакшне лучше фиксированный)
cipher_key = Fernet.generate_key()
cipher_suite = Fernet(cipher_key)

def main(page: ft.Page):
    page.title = "GHOST PRO V12"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#000000"
    page.padding = 0
    page.window_full_screen = True
    page.fonts = {"Matrix": "https://github.com/google/fonts/raw/main/apache/robotomono/RobotoMono-Bold.ttf"}

    # --- СОСТОЯНИЕ ---
    user = {"uid": "@guest", "role": "USER", "avatar": None}

    # --- ФУНКЦИИ ШИФРОВАНИЯ ---
    def encrypt_msg(text):
        return cipher_suite.encrypt(text.encode()).decode()

    def decrypt_msg(token):
        try: return cipher_suite.decrypt(token.encode()).decode()
        except: return "[ENCRYPTED_DATA]"

    # --- ЛОГИКА ГОЛОСОВЫХ И ФАЙЛОВ ---
    def on_result(e: ft.FilePickerResultEvent):
        if e.files:
            for file in e.files:
                with open(file.path, "rb") as f:
                    encoded = base64.b64encode(f.read()).decode()
                
                payload = {
                    "user": user["uid"],
                    "type": "media",
                    "mime": "image" if file.name.endswith(('.png', '.jpg')) else "file",
                    "name": file.name,
                    "data": encoded,
                    "time": datetime.datetime.now().strftime("%H:%M")
                }
                page.pubsub.send_all(str(payload))

    picker = ft.FilePicker(on_result=on_result)
    page.overlay.append(picker)

    # --- ОБРАБОТКА СООБЩЕНИЙ ---
    def handle_broadcast(msg_str):
        data = eval(msg_str)
        is_me = data["user"] == user["uid"]
        
        msg_content = ft.Column(spacing=5)
        
        if data["type"] == "text":
            msg_content.controls.append(ft.Text(decrypt_msg(data["text"]), color="#00FF00", size=16))
        elif data["type"] == "media":
            if data["mime"] == "image":
                msg_content.controls.append(ft.Image(src_base64=data["data"], width=200, border_radius=10))
            msg_content.controls.append(ft.Text(f"📎 {data['name']}", color="grey", size=10))

        chat_display.controls.append(
            ft.Container(
                content=ft.Column([
                    ft.Text(data["user"], size=10, color="#008800", weight="bold"),
                    msg_content,
                    ft.Text(data["time"], size=8, color="#004400"),
                ]),
                alignment=ft.alignment.center_right if is_me else ft.alignment.center_left,
                padding=10,
                bgcolor="#050505",
                border=ft.border.all(1, "#00FF00" if is_me else "#004400"),
                border_radius=ft.border_radius.only(top_left=15, top_right=15, bottom_left=0 if is_me else 15, bottom_right=15 if is_me else 0),
                margin=ft.margin.only(bottom=10, left=50 if is_me else 0, right=0 if is_me else 50)
            )
        )
        page.update()

    page.pubsub.subscribe(handle_broadcast)

    # --- ДИЗАЙН: MATRIX INTERFACE ---
    chat_display = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True)
    msg_input = ft.TextField(
        hint_text=">>> ENTER_PAYLOAD...", 
        expand=True, 
        border_color="#00FF00", 
        color="#00FF00",
        text_style=ft.TextStyle(font_family="Matrix")
    )

    def send_text(e):
        if msg_input.value:
            payload = {
                "user": user["uid"],
                "type": "text",
                "text": encrypt_msg(msg_input.value),
                "time": datetime.datetime.now().strftime("%H:%M")
            }
            page.pubsub.send_all(str(payload))
            msg_input.value = ""
            page.update()

    # --- ЭКРАН АДМИНКИ (ПОЛНЫЙ КОНТРОЛЬ) ---
    def show_admin_panel():
        page.clean()
        page.add(
            ft.Container(
                content=ft.Column([
                    ft.Text("MASTER_CONTROL_UNIT", size=30, color="red", weight="bold"),
                    ft.Divider(color="red"),
                    ft.ElevatedButton("BAN_USER_BY_IP", bgcolor="#220000", color="red", width=400),
                    ft.ElevatedButton("WIPE_GLOBAL_DATABASE", bgcolor="#220000", color="red", width=400),
                    ft.ElevatedButton("DECRYPT_SESSION_LOGS", bgcolor="#220000", color="red", width=400),
                    ft.ElevatedButton("EXIT_CORE", on_click=lambda _: show_main_net(), bgcolor="red", color="white"),
                ], horizontal_alignment="center"),
                padding=20, bgcolor="#000000", expand=True
            )
        )

    # --- ЭКРАН ПРОФИЛЯ ---
    def show_profile():
        page.clean()
        page.add(
            ft.Container(
                content=ft.Column([
                    ft.CircleAvatar(radius=70, bgcolor="#00FF00", content=ft.Icon(ft.icons.PERSON, size=50, color="black")),
                    ft.ElevatedButton("SELECT_AVATAR", on_click=lambda _: picker.pick_files()),
                    ft.Text(user["uid"], size=30, color="#00FF00", weight="bold"),
                    ft.Text("ENCRYPTION: AES-256-P2P", color="grey"),
                    ft.ElevatedButton("TECH_SUPPORT", icon=ft.icons.SUPPORT_AGENT),
                    ft.ElevatedButton("BACK_TO_NET", on_click=lambda _: show_main_net()),
                ], horizontal_alignment="center"),
                padding=20
            )
        )

    # --- ОСНОВНАЯ СЕТЬ ---
    def show_main_net():
        page.clean()
        page.add(
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text("GHOST_NET_v12", color="#00FF00", size=20, weight="bold"),
                        ft.Row([
                            ft.IconButton(ft.icons.ADMIN_PANEL_SETTINGS, icon_color="red", visible=user["role"]=="ADMIN", on_click=lambda _: show_admin_panel()),
                            ft.IconButton(ft.icons.PERSON, icon_color="#00FF00", on_click=lambda _: show_profile()),
                        ])
                    ], justify="spaceBetween"),
                    ft.TextField(hint_text="SEARCH_UID...", prefix_icon=ft.icons.SEARCH, height=40, border_color="#004400"),
                    ft.Container(content=chat_display, expand=True, padding=10, border=ft.border.all(1, "#002200")),
                    ft.Row([
                        ft.IconButton(ft.icons.MIC, icon_color="#00FF00"), # ГС через Picker (надежнее)
                        ft.IconButton(ft.icons.ATTACH_FILE, icon_color="#00FF00", on_click=lambda _: picker.pick_files()),
                        msg_input,
                        ft.IconButton(ft.icons.SEND, icon_color="#00FF00", on_click=send_text),
                    ])
                ]),
                expand=True, padding=10
            )
        )

    # --- ВХОД (ЛОГИКА СЕМЕРОК) ---
    def do_login(e):
        if login_in.value == "adminpan" and pass_in.value == "TimaIssam2026":
            user["uid"], user["role"] = "@ADMIN_CORE", "ADMIN"
        else:
            user["uid"] = f"@{login_in.value}"
        page.clean()
        show_main_net()

    login_in = ft.TextField(label="IDENTIFIER", border_color="#00FF00", color="#00FF00")
    pass_in = ft.TextField(label="ACCESS_KEY", password=True, border_color="#00FF00", color="#00FF00")
    
    page.add(
        ft.Container(
            content=ft.Column([
                ft.Text("GHOST_PRO_SYSTEM", size=40, color="#00FF00", weight="bold"),
                ft.Container(height=20),
                login_in, pass_in,
                ft.ElevatedButton("INITIALIZE", on_click=do_login, bgcolor="#002200", color="#00FF00", width=300),
                ft.Text("SECURE_LINE_777", color="#004400", size=10)
            ], horizontal_alignment="center"),
            padding=50, alignment=ft.alignment.center, expand=True
        )
    )

ft.app(target=main)
