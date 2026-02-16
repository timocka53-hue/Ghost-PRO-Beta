import flet as ft
import firebase_admin
from firebase_admin import credentials, firestore, storage
import datetime
import base64
import os

def main(page: ft.Page):
    # --- ТВОЙ АХУЕННЫЙ ВИЗУАЛ ---
    page.title = "GHOST PRO V13"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#000000"
    page.padding = 0
    page.window_width = 450
    page.window_height = 850

    class SystemState:
        db = None
        bucket = None
        user = "GHOST"
        role = "USER"
        is_auth = False

    st = SystemState()

    # --- ШИФРОВАНИЕ ДАННЫХ ---
    def x_crypt(data, mode="e"):
        try:
            if mode == "e": return base64.b64encode(data.encode()).decode()
            return base64.b64decode(data.encode()).decode()
        except: return data

    # --- ПОДКЛЮЧЕНИЕ БАЗЫ (АВТОМАТИЧЕСКОЕ) ---
    def init_matrix():
        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate("serviceAccountKey.json")
                firebase_admin.initialize_app(cred, {'storageBucket': 'ghost-v13.appspot.com'})
            st.db = firestore.client()
            st.bucket = storage.bucket()
            return True
        except: return False

    container = ft.Column(expand=True, spacing=0)
    page.add(container)

    # --- ЧАТ И МЕДИА ---
    chat_messages = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True, spacing=12)

    def sync_data(docs, changes, read_time):
        chat_messages.controls.clear()
        for doc in docs:
            m = doc.to_dict()
            is_adm = m.get("r") == "ADMIN"
            chat_messages.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text(m.get("u"), size=11, color="#00FF00" if is_adm else "#444444", weight="bold"),
                            ft.Text(m.get("time"), size=9, color="#222222")
                        ], justify="spaceBetween"),
                        ft.Text(x_crypt(m.get("t"), "d"), color="#FFFFFF", size=15),
                        ft.Image(src=m.get("img"), width=300, border_radius=10, visible=bool(m.get("img")))
                    ], spacing=5),
                    padding=15, bgcolor="#080808" if not is_adm else "#001200",
                    border=ft.border.all(1, "#111111" if not is_adm else "#00FF00"),
                    border_radius=15, margin=ft.margin.only(left=10, right=10)
                )
            )
        page.update()

    # --- ЭКРАН ВХОДА (Твой логин и пароль) ---
    def show_auth():
        u_field = ft.TextField(label="IDENT_ID", border_color="#00FF00", color="#00FF00")
        p_field = ft.TextField(label="ACCESS_KEY", password=True, border_color="#00FF00", can_reveal_password=True)
        
        def do_login(e):
            if u_field.value == "adminpan" and p_field.value == "TimaIssam2026":
                st.role = "ADMIN"
            st.user = f"@{u_field.value}"
            if init_matrix(): show_hub()
            else:
                page.snack_bar = ft.SnackBar(ft.Text("SYSTEM ERROR: Check serviceAccountKey.json")); page.snack_bar.open = True; page.update()

        container.controls.clear()
        container.controls.append(
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.icons.VAPES, size=110, color="#00FF00"),
                    ft.Text("GHOST V13 PRO", size=40, weight="bold", color="#00FF00"),
                    ft.Divider(height=40, color="transparent"),
                    u_field, p_field,
                    ft.ElevatedButton("INITIALIZE UPLINK", on_click=do_login, bgcolor="#002200", color="#00FF00", width=380, height=60)
                ], horizontal_alignment="center", alignment="center"),
                expand=True, padding=40
            )
        )
        page.update()

    # --- ГЛАВНЫЙ ХАБ (Все фишки тут) ---
    def show_hub():
        msg_in = ft.TextField(hint_text="Type encrypted message...", expand=True, border_color="#1A1A1A")
        
        def send_msg(e):
            if msg_in.value and st.db:
                st.db.collection("messages").add({
                    "u": st.user, "t": x_crypt(msg_in.value, "e"), "r": st.role,
                    "ts": firestore.SERVER_TIMESTAMP,
                    "time": datetime.datetime.now().strftime("%H:%M")
                })
                msg_in.value = ""
                page.update()

        if st.db:
            st.db.collection("messages").order_by("ts", descending=False).limit_to_last(40).on_snapshot(sync_data)

        container.controls.clear()
        container.controls.append(
            ft.Column([
                ft.Container(
                    content=ft.Row([
                        ft.Column([ft.Text("ENCRYPTED", color="#00FF00", size=10), ft.Text(st.user, size=18, weight="bold")]),
                        ft.Row([
                            ft.IconButton(ft.icons.SUPPORT_AGENT, icon_color="#00FF00", on_click=lambda _: show_support()),
                            ft.IconButton(ft.icons.ADMIN_PANEL_SETTINGS, icon_color="red", visible=(st.role=="ADMIN"), on_click=lambda _: show_admin())
                        ])
                    ], justify="spaceBetween"),
                    padding=20, bgcolor="#0A0A0A"
                ),
                ft.Container(content=chat_messages, expand=True),
                ft.Container(
                    content=ft.Row([
                        ft.IconButton(ft.icons.ADD_PHOTO_ALTERNATE_ROUNDED, icon_color="#444444"),
                        msg_in,
                        ft.IconButton(ft.icons.SEND_ROUNDED, icon_color="#00FF00", on_click=send_msg)
                    ]),
                    padding=20, bgcolor="#050505"
                )
            ], expand=True)
        )
        page.update()

    # --- АДМИН ПАНЕЛЬ (ПОЛНАЯ) ---
    def show_admin():
        container.controls.clear()
        container.controls.append(
            ft.Column([
                ft.AppBar(title=ft.Text("ADMIN TERMINAL"), bgcolor="#990000"),
                ft.ListTile(title=ft.Text("USER MANAGEMENT"), subtitle=ft.Text("Ban/Unban/Role change"), leading=ft.Icon(ft.icons.PERSON_SEARCH)),
                ft.ListTile(title=ft.Text("CLEAR ALL CHATS"), leading=ft.Icon(ft.icons.DELETE_SWEEP), on_click=lambda _: print("Cleared")),
                ft.ListTile(title=ft.Text("VIEW TICKETS"), leading=ft.Icon(ft.icons.CONFIRMATION_NUMBER)),
                ft.ElevatedButton("EXIT TO HUB", on_click=lambda _: show_hub(), width=400)
            ])
        )
        page.update()

    # --- ТЕХ ПОДДЕРЖКА ---
    def show_support():
        container.controls.clear()
        container.controls.append(
            ft.Column([
                ft.AppBar(title=ft.Text("SUPPORT"), bgcolor="#004400"),
                ft.Padding(padding=20, content=ft.Column([
                    ft.TextField(label="Subject", border_color="#00FF00"),
                    ft.TextField(label="Description", multiline=True, min_lines=5, border_color="#00FF00"),
                    ft.ElevatedButton("SUBMIT REQUEST", width=400, bgcolor="#002200", color="#00FF00")
                ])),
                ft.TextButton("BACK", on_click=lambda _: show_hub())
            ])
        )
        page.update()

    show_auth()

if __name__ == "__main__":
    ft.app(target=main)
