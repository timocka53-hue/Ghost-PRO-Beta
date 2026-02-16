import flet as ft
import firebase_admin
from firebase_admin import credentials, firestore
import datetime
import time
import threading

def main(page: ft.Page):
    # --- КОНФИГУРАЦИЯ СИСТЕМЫ ---
    page.title = "Ghost PRO"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#000000"
    page.padding = 0
    page.window_width = 450
    page.window_height = 850
    page.fonts = {
        "RobotoMono": "https://github.com/google/fonts/raw/main/apache/robotomono/RobotoMono%5Bwght%5D.ttf"
    }
    page.theme = ft.Theme(font_family="RobotoMono")

    # --- СОСТОЯНИЕ ПРИЛОЖЕНИЯ ---
    class State:
        db = None
        user_id = None
        role = "USER"
        active_chat = "GLOBAL"
        is_connected = False

    st = State()

    # --- ИНИЦИАЛИЗАЦИЯ FIREBASE ---
    def init_db():
        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate("serviceAccountKey.json")
                firebase_admin.initialize_app(cred)
            st.db = firestore.client()
            st.is_connected = True
        except Exception as e:
            print(f"Connection Error: {e}")

    # --- ВИЗУАЛЬНЫЕ КОМПОНЕНТЫ ---
    loading_screen = ft.Container(
        content=ft.Column([
            ft.ProgressRing(color="#00FF00"),
            ft.Text("INITIALIZING GHOST PROTOCOL...", color="#00FF00", size=12)
        ], horizontal_alignment="center", alignment="center"),
        expand=True, bgcolor="#000000"
    )

    # --- ЛОГИКА ЧАТА ---
    messages_list = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True, spacing=10)

    def on_message_update(docs, changes, read_time):
        messages_list.controls.clear()
        for doc in docs:
            data = doc.to_dict()
            is_me = data.get("u") == st.user_id
            is_admin = data.get("r") == "ADMIN"
            
            messages_list.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text(data.get("u"), size=10, color="#00FF00" if is_admin else "#777777", weight="bold"),
                            ft.Text(data.get("time"), size=9, color="#444444")
                        ], justify="spaceBetween"),
                        ft.Text(data.get("t"), color="#FFFFFF", size=15),
                    ], spacing=2),
                    alignment=ft.alignment.center_left,
                    padding=12,
                    bgcolor="#0A0A0A" if not is_admin else "#001100",
                    border=ft.border.all(1, "#1A1A1A" if not is_admin else "#00FF00"),
                    border_radius=12,
                    animate=ft.Animation(400, "decelerate")
                )
            )
        page.update()

    # --- ЭКРАНЫ ПРИЛОЖЕНИЯ ---
    def router(e=None):
        if not st.user_id:
            show_auth()
        else:
            show_terminal()

    def show_auth():
        page.clean()
        u_field = ft.TextField(label="GHOST_ID", border_color="#00FF00", cursor_color="#00FF00", text_style=ft.TextStyle(color="#00FF00"))
        p_field = ft.TextField(label="2FA_KEY", password=True, border_color="#00FF00", can_reveal_password=True)
        
        def attempt_login(e):
            if u_field.value:
                page.add(loading_screen)
                st.user_id = f"@{u_field.value}"
                if u_field.value == "adminpan" and p_field.value == "TimaIssam2026":
                    st.role = "ADMIN"
                init_db()
                time.sleep(1.5)
                show_terminal()

        page.add(
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.icons.SECURITY, size=80, color="#00FF00"),
                    ft.Text("GHOST PRO", size=40, weight="bold", color="#00FF00"),
                    ft.Text("V13.0 ENCRYPTION STANDARD", size=10, color="#00FF00", italic=True),
                    ft.Divider(height=40, color="transparent"),
                    u_field, p_field,
                    ft.ElevatedButton(
                        content=ft.Text("ESTABLISH CONNECTION", weight="bold"),
                        on_click=attempt_login,
                        style=ft.ButtonStyle(
                            color="#00FF00", bgcolor="#002200",
                            shape=ft.RoundedRectangleBorder(radius=8)
                        ),
                        width=300, height=50
                    )
                ], horizontal_alignment="center", alignment="center"),
                expand=True, padding=40
            )
        )

    def show_terminal():
        page.clean()
        msg_input = ft.TextField(
            hint_text="Type encrypted message...",
            expand=True,
            border_color="#1A1A1A",
            bgcolor="#0A0A0A",
            on_submit=send_msg
        )

        def send_msg(e):
            if msg_input.value and st.db:
                st.db.collection("messages").add({
                    "u": st.user_id,
                    "t": msg_input.value,
                    "r": st.role,
                    "time": datetime.datetime.now().strftime("%H:%M"),
                    "ts": firestore.SERVER_TIMESTAMP
                })
                msg_input.value = ""
                page.update()

        # Запуск слушателя
        if st.db:
            st.db.collection("messages").order_by("ts", descending=False).limit_to_last(30).on_snapshot(on_message_update)

        page.add(
            ft.Column([
                ft.Container(
                    content=ft.Row([
                        ft.Text("SYSTEM_ACTIVE", color="#00FF00", size=12, weight="bold"),
                        ft.Row([
                            ft.Text(st.user_id, color="#FFFFFF", size=12),
                            ft.Icon(ft.icons.VERIFIED, color="#00FF00", size=15 if st.role=="ADMIN" else 0)
                        ])
                    ], justify="spaceBetween"),
                    padding=15, bgcolor="#0A0A0A", border=ft.border.only(bottom=ft.border.BorderSide(1, "#1A1A1A"))
                ),
                ft.Container(content=messages_list, expand=True, padding=15),
                ft.Container(
                    content=ft.Row([
                        ft.IconButton(ft.icons.ADD_CIRCLE_OUTLINE, icon_color="#555555"),
                        msg_input,
                        ft.IconButton(ft.icons.SEND_ROUNDED, icon_color="#00FF00", on_click=send_msg)
                    ]),
                    padding=10, bgcolor="#000000"
                )
            ], expand=True)
        )

    show_auth()

ft.app(target=main)
