import flet as ft
import firebase_admin
from firebase_admin import credentials, firestore
import datetime
import time

def main(page: ft.Page):
    # --- НАСТРОЙКИ СТРАНИЦЫ ---
    page.title = "GHOST PRO V13"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#000000"
    page.padding = 0
    page.window_width = 450
    page.window_height = 850

    class AppState:
        db = None
        uid = "ANONYMOUS"
        role = "USER"
        authenticated = False

    st = AppState()

    # Основной контейнер
    content_view = ft.Column(expand=True, spacing=0)
    page.add(content_view)

    # --- ИНИЦИАЛИЗАЦИЯ БАЗЫ ---
    def connect_db():
        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate("serviceAccountKey.json")
                firebase_admin.initialize_app(cred)
            st.db = firestore.client()
            return True
        except:
            return False

    # --- ВИЗУАЛ СООБЩЕНИЙ ---
    messages_column = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True, spacing=15)

    def on_snapshot_update(docs, changes, read_time):
        messages_column.controls.clear()
        for doc in docs:
            m = doc.to_dict()
            is_adm = m.get("r") == "ADMIN"
            messages_column.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text(m.get("u"), size=10, color="#00FF00" if is_adm else "#777777", weight="bold"),
                            ft.Text(m.get("time"), size=9, color="#444444")
                        ], justify="spaceBetween"),
                        ft.Text(m.get("t"), color="#FFFFFF", size=15),
                    ], spacing=5),
                    padding=15,
                    bgcolor="#0A0A0A" if not is_adm else "#001A00",
                    border=ft.border.all(1, "#1A1A1A" if not is_adm else "#00FF00"),
                    border_radius=15,
                    margin=ft.margin.only(left=10, right=10)
                )
            )
        page.update()

    # --- ЭКРАН ВХОДА И 2FA ---
    def show_auth():
        view_view = ft.Column(horizontal_alignment="center", alignment="center", expand=True)
        
        id_input = ft.TextField(label="IDENT_ID", border_color="#00FF00", prefix_text="@", color="#00FF00")
        key_input = ft.TextField(label="2FA_KEY", password=True, border_color="#00FF00", can_reveal_password=True)
        
        def attempt_login(e):
            if id_input.value:
                st.uid = f"@{id_input.value}"
                # Админ-панель
                if id_input.value == "adminpan" and key_input.value == "TimaIssam2026":
                    st.role = "ADMIN"
                
                if connect_db():
                    show_hub()
                else:
                    page.snack_bar = ft.SnackBar(ft.Text("DATABASE ERROR: serviceAccountKey.json MISSING"))
                    page.snack_bar.open = True
                    page.update()

        view_view.controls = [
            ft.Icon(ft.icons.SECURITY, size=100, color="#00FF00"),
            ft.Text("GHOST PRO", size=50, weight="bold", color="#00FF00"),
            ft.Text("SYSTEM INITIALIZATION", size=12, color="#00FF00"),
            ft.Divider(height=40, color="transparent"),
            id_input, key_input,
            ft.ElevatedButton("CONNECT TO MATRIX", on_click=attempt_login, bgcolor="#002200", color="#00FF00", width=350, height=60)
        ]
        content_view.controls.clear()
        content_view.controls.append(ft.Container(content=view_view, padding=40, expand=True))
        page.update()

    # --- ЭКРАН ТЕРМИНАЛА (ЧАТ, ПОИСК, АДМИНКА) ---
    def show_hub():
        msg_field = ft.TextField(hint_text="Packet data...", expand=True, border_color="#1A1A1A")
        
        def send_data(e):
            if msg_field.value and st.db:
                st.db.collection("messages").add({
                    "u": st.uid, "t": msg_field.value, "r": st.role,
                    "ts": firestore.SERVER_TIMESTAMP,
                    "time": datetime.datetime.now().strftime("%H:%M")
                })
                msg_field.value = ""
                page.update()

        if st.db:
            st.db.collection("messages").order_by("ts", descending=False).limit_to_last(40).on_snapshot(on_snapshot_update)

        content_view.controls.clear()
        content_view.controls.append(
            ft.Column([
                ft.Container(
                    content=ft.Row([
                        ft.Column([
                            ft.Text("STATUS: UPLINK_ACTIVE", color="#00FF00", size=10, weight="bold"),
                            ft.Row([
                                ft.Text(st.uid, color="#FFFFFF", size=16, weight="bold"),
                                ft.Icon(ft.icons.VERIFIED, color="#00FF00", size=20, visible=(st.role=="ADMIN"))
                            ])
                        ]),
                        ft.IconButton(ft.icons.LOGOUT, on_click=lambda _: show_auth())
                    ], justify="spaceBetween"),
                    padding=20, bgcolor="#0A0A0A", border=ft.border.only(bottom=ft.border.BorderSide(1, "#1A1A1A"))
                ),
                ft.Container(content=messages_column, expand=True, padding=10),
                ft.Container(
                    content=ft.Row([
                        ft.IconButton(ft.icons.SEARCH, icon_color="#00FF00"),
                        msg_field,
                        ft.IconButton(ft.icons.SEND_ROUNDED, icon_color="#00FF00", on_click=send_data)
                    ]),
                    padding=20, bgcolor="#000000"
                )
            ], expand=True, spacing=0)
        )
        page.update()

    show_auth()

if __name__ == "__main__":
    ft.app(target=main)

