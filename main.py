import flet as ft
import datetime
import requests # Для прямой работы с REST API Firebase без ключей-файлов

def main(page: ft.Page):
    page.title = "GHOST PRO V13"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#000000"
    page.window_full_screen = True
    
    # Твои данные из google-services.json для связи
    FB_URL = "https://ghost-pro-5aa22-default-rtdb.firebaseio.com/messages.json"
    
    state = {"uid": None, "role": "USER"}

    chat_list = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True, spacing=10)

    # --- ФУНКЦИЯ ОБЩЕНИЯ (РЕАЛЬНОЕ ВРЕМЯ) ---
    def sync_chat():
        try:
            res = requests.get(FB_URL).json()
            if res:
                chat_list.controls.clear()
                for msg_id in res:
                    m = res[msg_id]
                    is_me = m.get("user") == state["uid"]
                    chat_list.controls.append(
                        ft.Container(
                            content=ft.Text(f"{m.get('user')}: {m.get('text')}", color="white"),
                            padding=10,
                            bgcolor="#0A0A0A",
                            border=ft.border.all(1, "#00FF00" if is_me else "#002200"),
                            border_radius=10,
                            alignment=ft.alignment.center_right if is_me else ft.alignment.center_left
                        )
                    )
                page.update()
        except:
            pass

    def send_msg(e):
        if msg_input.value:
            payload = {
                "user": state["uid"],
                "text": msg_input.value,
                "ts": datetime.datetime.now().isoformat()
            }
            requests.post(FB_URL, json=payload)
            msg_input.value = ""
            sync_chat()

    # --- ЭКРАН ЧАТА ---
    def show_chat():
        page.clean()
        page.add(
            ft.Column([
                ft.Row([
                    ft.Text("GHOST_PRO_NETWORK", color="#00FF00", weight="bold", size=20),
                    ft.IconButton(ft.icons.REFRESH, on_click=lambda _: sync_chat())
                ], justify="spaceBetween"),
                ft.Container(content=chat_list, expand=True, border=ft.border.all(1, "#002200"), padding=10),
                ft.Row([
                    msg_input,
                    ft.IconButton(ft.icons.SEND, icon_color="#00FF00", on_click=send_msg)
                ])
            ], expand=True, padding=15)
        )
        sync_chat()

    # --- ЭКРАН ВХОДА (ПЕРВОЕ, ЧТО УВИДИТ ЮЗЕР) ---
    user_in = ft.TextField(label="ENTER_YOUR_UID", border_color="#00FF00", color="#00FF00")
    pass_in = ft.TextField(label="ACCESS_KEY", password=True, border_color="#00FF00")
    msg_input = ft.TextField(hint_text="Type message...", expand=True, border_color="#00FF00")

    def login(e):
        if user_in.value:
            state["uid"] = f"@{user_in.value}"
            if user_in.value == "adminpan" and pass_in.value == "TimaIssam2026":
                state["role"] = "ADMIN"
            show_chat()

    page.add(
        ft.Container(
            content=ft.Column([
                ft.Icon(ft.icons.SECURITY, size=80, color="#00FF00"),
                ft.Text("MATRIX_ENCRYPTED_V13", size=25, weight="bold", color="#00FF00"),
                user_in, pass_in,
                ft.ElevatedButton("INITIALIZE_SESSION", on_click=login, bgcolor="#002200", color="#00FF00", width=300)
            ], horizontal_alignment="center", spacing=20),
            alignment=ft.alignment.center, expand=True
        )
    )

ft.app(target=main)
