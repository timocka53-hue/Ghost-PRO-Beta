import flet as ft
import firebase_admin
from firebase_admin import credentials, firestore
import datetime
import time

def main(page: ft.Page):
    # --- КОНФИГУРАЦИЯ СИСТЕМЫ ---
    page.title = "Ghost PRO"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#000000"
    page.padding = 0
    page.window_width = 450
    page.window_height = 850
    
    # Состояние приложения
    class AppState:
        db = None
        uid = None
        role = "USER"
        is_connected = False

    st = AppState()

    # Сразу создаем контейнер для контента
    content_area = ft.Column(expand=True)
    page.add(content_area)

    def init_firebase():
        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate("serviceAccountKey.json")
                firebase_admin.initialize_app(cred)
            st.db = firestore.client()
            st.is_connected = True
            return True
        except: return False

    # --- ВИЗУАЛ СООБЩЕНИЙ ---
    chat_list = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True, spacing=10)

    def update_chat(docs, changes, read_time):
        chat_list.controls.clear()
        for doc in docs:
            m = doc.to_dict()
            is_adm = m.get("r") == "ADMIN"
            chat_list.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text(m.get("u"), size=11, color="#00FF00" if is_adm else "#777777", weight="bold"),
                            ft.Text(m.get("time"), size=9, color="#444444")
                        ], justify="spaceBetween"),
                        ft.Text(m.get("t"), color="#FFFFFF", size=15),
                    ], spacing=2),
                    padding=12,
                    bgcolor="#0A0A0A" if not is_adm else "#001100",
                    border=ft.border.all(1, "#1A1A1A" if not is_adm else "#00FF00"),
                    border_radius=10
                )
            )
        page.update()

    # --- ЭКРАН 1: ВХОД (БЕЗ INPUT) ---
    def show_auth():
        u_field = ft.TextField(label="GHOST_ID", border_color="#00FF00", prefix_text="@")
        p_field = ft.TextField(label="2FA_KEY", password=True, border_color="#00FF00", can_reveal_password=True)
        
        def on_login_click(e):
            if u_field.value:
                st.uid = f"@{u_field.value}"
                if u_field.value == "adminpan" and p_field.value == "TimaIssam2026":
                    st.role = "ADMIN"
                
                if init_firebase():
                    show_terminal()
                else:
                    page.snack_bar = ft.SnackBar(ft.Text("FIREBASE ERROR"))
                    page.snack_bar.open = True
                    page.update()

        content_area.controls.clear()
        content_area.controls.append(
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.icons.SECURITY, size=100, color="#00FF00"),
                    ft.Text("GHOST PRO V13", size=45, weight="bold", color="#00FF00"),
                    ft.Divider(height=40, color="transparent"),
                    u_field, p_field,
                    ft.ElevatedButton("INITIALIZE LINK", on_click=on_login_click, bgcolor="#002200", color="#00FF00", width=350, height=60)
                ], horizontal_alignment="center", alignment="center"),
                expand=True, padding=40
            )
        )
        page.update()

    # --- ЭКРАН 2: ТЕРМИНАЛ (ЧАТ) ---
    def show_terminal():
        msg_in = ft.TextField(hint_text="Message...", expand=True, border_color="#1A1A1A")
        
        def send(e):
            if msg_in.value and st.db:
                st.db.collection("messages").add({
                    "u": st.uid, "t": msg_in.value, "r": st.role,
                    "ts": firestore.SERVER_TIMESTAMP,
                    "time": datetime.datetime.now().strftime("%H:%M")
                })
                msg_in.value = ""
                page.update()

        # Слушатель базы
        if st.db:
            st.db.collection("messages").order_by("ts", descending=False).limit_to_last(30).on_snapshot(update_chat)

        content_area.controls.clear()
        content_area.controls.append(
            ft.Column([
                ft.Container(
                    content=ft.Row([
                        ft.Text(f"LOGGED: {st.uid}", color="#00FF00", weight="bold"),
                        ft.Icon(ft.icons.VERIFIED, color="#00FF00", visible=(st.role=="ADMIN"))
                    ], justify="spaceBetween"),
                    padding=15, bgcolor="#111111"
                ),
                ft.Container(content=chat_list, expand=True, padding=10),
                ft.Row([
                    ft.IconButton(ft.icons.SEARCH, icon_color="#00FF00"),
                    msg_in,
                    ft.IconButton(ft.icons.SEND, on_click=send, icon_color="#00FF00")
                ], padding=10)
            ], expand=True)
        )
        page.update()

    show_auth()

if __name__ == "__main__":
    ft.app(target=main)
