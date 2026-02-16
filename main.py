import flet as ft
import firebase_admin
from firebase_admin import credentials, firestore
import datetime
import time

def main(page: ft.Page):
    # --- ГЛОБАЛЬНАЯ КОНФИГУРАЦИЯ ---
    page.title = "Ghost PRO V13"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#000000"
    page.padding = 0
    page.window_width = 450
    page.window_height = 850
    
    # Состояние приложения
    class GhostSystem:
        db = None
        uid = "GHOST_UNREGISTERED"
        role = "USER"
        is_auth = False

    st = GhostSystem()

    # Основной контейнер
    view_canvas = ft.Column(expand=True, spacing=0)
    page.add(view_canvas)

    # --- ИНИЦИАЛИЗАЦИЯ БАЗЫ ---
    def connect_matrix():
        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate("serviceAccountKey.json")
                firebase_admin.initialize_app(cred)
            st.db = firestore.client()
            return True
        except Exception:
            return False

    # --- ВИЗУАЛ СООБЩЕНИЙ (РЕАЛЬНОЕ ОБЩЕНИЕ) ---
    chat_messages = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True, spacing=15)

    def sync_matrix_chat(docs, changes, read_time):
        chat_messages.controls.clear()
        for doc in docs:
            m = doc.to_dict()
            is_adm = m.get("r") == "ADMIN"
            chat_messages.controls.append(
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

    # --- ЭКРАН 1: MATRIX AUTH (2FA + IDENTIFICATION) ---
    def show_auth_matrix():
        u_field = ft.TextField(label="IDENT_ID", border_color="#00FF00", prefix_text="@", color="#00FF00")
        p_field = ft.TextField(label="2FA_KEY", password=True, border_color="#00FF00", can_reveal_password=True)
        
        def start_uplink(e):
            if u_field.value:
                st.uid = f"@{u_field.value}"
                # Админ-панель: проверка данных
                if u_field.value == "adminpan" and p_field.value == "TimaIssam2026":
                    st.role = "ADMIN"
                
                if connect_matrix():
                    show_main_hub()
                else:
                    page.snack_bar = ft.SnackBar(ft.Text("ERROR: NO serviceAccountKey.json FOUND"))
                    page.snack_bar.open = True
                    page.update()

        view_canvas.controls.clear()
        view_canvas.controls.append(
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.icons.SECURITY, size=100, color="#00FF00"),
                    ft.Text("GHOST PRO V13", size=45, weight="bold", color="#00FF00"),
                    ft.Text("SYSTEM INITIALIZATION...", size=12, color="#00FF00"),
                    ft.Divider(height=50, color="transparent"),
                    u_field, p_field,
                    ft.Divider(height=20, color="transparent"),
                    ft.ElevatedButton("CONNECT TO MATRIX", on_click=start_uplink, bgcolor="#002200", color="#00FF00", width=350, height=60)
                ], horizontal_alignment="center", alignment="center"),
                expand=True, padding=40
            )
        )
        page.update()

    # --- ЭКРАН 2: TERMINAL HUB (ЧАТ, ПОИСК, АДМИНКА) ---
    def show_main_hub():
        view_canvas.controls.clear()
        msg_in = ft.TextField(hint_text="Type encrypted packet...", expand=True, border_color="#1A1A1A")
        
        def send_data(e):
            if msg_in.value and st.db:
                st.db.collection("messages").add({
                    "u": st.uid, "t": msg_in.value, "r": st.role,
                    "ts": firestore.SERVER_TIMESTAMP,
                    "time": datetime.datetime.now().strftime("%H:%M")
                })
                msg_in.value = ""
                page.update()

        # Поиск (Реальный визуал)
        def trigger_search(e):
            page.snack_bar = ft.SnackBar(ft.Text("SCANNING ENCRYPTED CHANNELS..."))
            page.snack_bar.open = True
            page.update()

        # Слушатель реального времени
        if st.db:
            st.db.collection("messages").order_by("ts", descending=False).limit_to_last(40).on_snapshot(sync_matrix_chat)

        view_canvas.controls.append(
            ft.Column([
                # Статус-бар
                ft.Container(
                    content=ft.Row([
                        ft.Column([
                            ft.Text("UPLINK: ACTIVE", color="#00FF00", size=10, weight="bold"),
                            ft.Row([
                                ft.Text(st.uid, color="#FFFFFF", size=16, weight="bold"),
                                ft.Icon(ft.icons.VERIFIED, color="#00FF00", size=20, visible=(st.role=="ADMIN"))
                            ])
                        ]),
                        ft.IconButton(ft.icons.LOGOUT, icon_color="#555555", on_click=lambda _: show_auth_matrix())
                    ], justify="spaceBetween"),
                    padding=20, bgcolor="#0A0A0A", border=ft.border.only(bottom=ft.border.BorderSide(1, "#1A1A1A"))
                ),
                # Навигация
                ft.Container(
                    content=ft.Row([
                        ft.TextButton("GLOBAL", icon=ft.icons.LANGUAGE, icon_color="#00FF00"),
                        ft.TextButton("SEARCH", icon=ft.icons.SEARCH, icon_color="#00FF00", on_click=trigger_search),
                        ft.TextButton("ADMIN", icon=ft.icons.LOCK, icon_color="red", visible=(st.role=="ADMIN")),
                    ], scroll=ft.ScrollMode.AUTO),
                    padding=5
                ),
                # Область сообщений
                ft.Container(content=chat_messages, expand=True, padding=10),
                # Ввод
                ft.Container(
                    content=ft.Row([
                        ft.IconButton(ft.icons.ADD_MODES, icon_color="#333333"),
                        msg_in,
                        ft.IconButton(ft.icons.SEND_ROUNDED, icon_color="#00FF00", on_click=send_data)
                    ]),
                    padding=20, bgcolor="#000000"
                )
            ], expand=True, spacing=0)
        )
        page.update()

    show_auth_matrix()

if __name__ == "__main__":
    ft.app(target=main)
