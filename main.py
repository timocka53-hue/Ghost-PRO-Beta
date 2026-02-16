import flet as ft
import firebase_admin
from firebase_admin import credentials, firestore
import datetime
import time

def main(page: ft.Page):
    # Глобальные настройки системы
    page.title = "GHOST PRO V13: ULTIMATE"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#000000"
    page.padding = 0
    page.window_width = 450
    page.window_height = 850
    page.scroll = ft.ScrollMode.HIDDEN

    class GhostState:
        db = None
        uid = "GHOST_ANONYMOUS"
        role = "USER"
        is_connected = False

    st = GhostState()
    container = ft.Column(expand=True, spacing=0)
    page.add(container)

    # Функция подключения к Firebase (Matrix Uplink)
    def connect_matrix():
        try:
            if not firebase_admin._apps:
                # serviceAccountKey.json должен быть в корне репозитория!
                cred = credentials.Certificate("serviceAccountKey.json")
                firebase_admin.initialize_app(cred)
            st.db = firestore.client()
            st.is_connected = True
            return True
        except Exception:
            return False

    # Область отображения данных (Чат)
    message_log = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True, spacing=15)

    def on_snapshot_receive(docs, changes, read_time):
        message_log.controls.clear()
        for doc in docs:
            m = doc.to_dict()
            is_adm = m.get("r") == "ADMIN"
            message_log.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text(m.get("u"), size=10, color="#00FF00" if is_adm else "#666666", weight="bold"),
                            ft.Text(m.get("time"), size=9, color="#333333")
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

    # ЭКРАН 1: АВТОРИЗАЦИЯ И 2FA (ВМЕСТО КОНСОЛИ)
    def show_auth_screen():
        container.controls.clear()
        
        user_id = ft.TextField(label="IDENT_ID", border_color="#00FF00", prefix_text="@", color="#00FF00")
        auth_key = ft.TextField(label="2FA_ENCRYPT_KEY", password=True, border_color="#00FF00", can_reveal_password=True)
        
        def start_system(e):
            if not user_id.value:
                return
            
            st.uid = f"@{user_id.value}"
            # Проверка прав администратора
            if user_id.value == "adminpan" and auth_key.value == "TimaIssam2026":
                st.role = "ADMIN"
            
            if connect_matrix():
                show_terminal_hub()
            else:
                page.snack_bar = ft.SnackBar(ft.Text("CRITICAL ERROR: NO DB LINK"), bgcolor="red")
                page.snack_bar.open = True
                page.update()

        container.controls.append(
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.icons.SECURITY, size=100, color="#00FF00"),
                    ft.Text("GHOST PRO V13", size=40, weight="bold", color="#00FF00"),
                    ft.Text("SYSTEM INITIALIZATION...", size=12, color="#00FF00"),
                    ft.Divider(height=50, color="transparent"),
                    user_id,
                    auth_key,
                    ft.Divider(height=20, color="transparent"),
                    ft.ElevatedButton(
                        "EXECUTE UPLINK", 
                        on_click=start_system, 
                        bgcolor="#003300", 
                        color="#00FF00", 
                        width=350, 
                        height=60
                    )
                ], horizontal_alignment="center", alignment="center"),
                expand=True, padding=40
            )
        )
        page.update()

    # ЭКРАН 2: ТЕРМИНАЛ (ЧАТ + ПОИСК + АДМИНКА)
    def show_terminal_hub():
        container.controls.clear()
        
        input_field = ft.TextField(hint_text="Type encrypted packet...", expand=True, border_color="#1A1A1A")
        
        def send_data(e):
            if input_field.value and st.db:
                st.db.collection("messages").add({
                    "u": st.uid, 
                    "t": input_field.value, 
                    "r": st.role,
                    "ts": firestore.SERVER_TIMESTAMP,
                    "time": datetime.datetime.now().strftime("%H:%M")
                })
                input_field.value = ""
                page.update()

        # Поиск (заглушка с визуалом)
        def trigger_search(e):
            page.snack_bar = ft.SnackBar(ft.Text("SCANNING GLOBAL NETWORK..."))
            page.snack_bar.open = True
            page.update()

        # Слушатель базы данных
        if st.db:
            st.db.collection("messages").order_by("ts", descending=False).limit_to_last(50).on_snapshot(on_snapshot_receive)

        container.controls.append(
            ft.Column([
                # Верхняя панель статуса
                ft.Container(
                    content=ft.Row([
                        ft.Column([
                            ft.Text("UPLINK: ACTIVE", color="#00FF00", size=10, weight="bold"),
                            ft.Row([
                                ft.Text(st.uid, color="#FFFFFF", size=18, weight="bold"),
                                ft.Icon(ft.icons.VERIFIED, color="#00FF00", size=20, visible=(st.role=="ADMIN"))
                            ])
                        ]),
                        ft.IconButton(ft.icons.SETTINGS_INPUT_ANTENNA, icon_color="#555555", on_click=lambda _: show_auth_screen())
                    ], justify="spaceBetween"),
                    padding=20, bgcolor="#0A0A0A", border=ft.border.only(bottom=ft.border.BorderSide(1, "#1A1A1A"))
                ),
                # Навигация
                ft.Container(
                    content=ft.Row([
                        ft.TextButton("GLOBAL_NET", icon=ft.icons.LANGUAGE, icon_color="#00FF00"),
                        ft.TextButton("SEARCH", icon=ft.icons.SEARCH, icon_color="#00FF00", on_click=trigger_search),
                        ft.TextButton("ADMIN_PANEL", icon=ft.icons.LOCK, icon_color="red", visible=(st.role=="ADMIN")),
                    ], scroll=ft.ScrollMode.AUTO),
                    padding=5
                ),
                # Тело чата
                ft.Container(content=message_log, expand=True, padding=10),
                # Поле ввода
                ft.Container(
                    content=ft.Row([
                        ft.IconButton(ft.icons.ADD_CIRCLE_OUTLINE, icon_color="#333333"),
                        input_field,
                        ft.IconButton(ft.icons.SEND_ROUNDED, icon_color="#00FF00", on_click=send_data)
                    ]),
                    padding=20, bgcolor="#000000"
                )
            ], expand=True, spacing=0)
        )
        page.update()

    show_auth_screen()

if __name__ == "__main__":
    ft.app(target=main)


