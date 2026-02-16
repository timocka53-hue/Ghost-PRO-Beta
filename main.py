import flet as ft
import firebase_admin
from firebase_admin import credentials, firestore
import datetime
import time

def main(page: ft.Page):
    # --- НАСТРОЙКИ СИСТЕМЫ GHOST ---
    page.title = "GHOST PRO V13: MAXIMUM"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#000000"
    page.padding = 0
    page.window_width = 450
    page.window_height = 850
    page.scroll = ft.ScrollMode.HIDDEN

    class GhostState:
        db = None
        uid = "UNREGISTERED"
        role = "USER"
        is_connected = False

    st = GhostState()
    view_canvas = ft.Column(expand=True, spacing=0)
    page.add(view_canvas)

    # --- FIREBASE UPLINK ---
    def connect_to_matrix():
        try:
            if not firebase_admin._apps:
                # ВАЖНО: serviceAccountKey.json должен быть в корне!
                cred = credentials.Certificate("serviceAccountKey.json")
                firebase_admin.initialize_app(cred)
            st.db = firestore.client()
            st.is_connected = True
            return True
        except: return False

    # --- КОМПОНЕНТЫ ИНТЕРФЕЙСА ---
    message_log = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True, spacing=15)

    def sync_matrix_data(docs, changes, read_time):
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
                    padding=15, bgcolor="#0A0A0A" if not is_adm else "#001A00",
                    border=ft.border.all(1, "#1A1A1A" if not is_adm else "#00FF00"),
                    border_radius=15, margin=ft.margin.only(left=10, right=10)
                )
            )
        page.update()

    # --- ЭКРАН 1: MATRIX AUTH (БЕЗ КОНСОЛИ!) ---
    def show_auth_panel():
        id_input = ft.TextField(label="IDENT_ID", border_color="#00FF00", prefix_text="@", color="#00FF00")
        key_input = ft.TextField(label="2FA_KEY", password=True, border_color="#00FF00", can_reveal_password=True)
        
        def run_initialization(e):
            if not id_input.value: return
            st.uid = f"@{id_input.value}"
            # Проверка админки
            if id_input.value == "adminpan" and key_input.value == "TimaIssam2026":
                st.role = "ADMIN"
            
            if connect_to_matrix(): show_main_terminal()
            else:
                page.snack_bar = ft.SnackBar(ft.Text("ERROR: NO DATABASE LINK"))
                page.snack_bar.open = True
                page.update()

        view_canvas.controls.clear()
        view_canvas.controls.append(
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.icons.SECURITY, size=100, color="#00FF00"),
                    ft.Text("GHOST PRO V13", size=45, weight="bold", color="#00FF00"),
                    ft.Text("ENCRYPTED ACCESS ONLY", size=12, color="#00FF00"),
                    ft.Divider(height=50, color="transparent"),
                    id_input, key_input,
                    ft.ElevatedButton("INITIALIZE UPLINK", on_click=run_initialization, bgcolor="#002200", color="#00FF00", width=350, height=60)
                ], horizontal_alignment="center", alignment="center"),
                expand=True, padding=40
            )
        )
        page.update()

    # --- ЭКРАН 2: ТЕРМИНАЛ ХАБ (ПОЛНЫЙ ФУНКЦИОНАЛ) ---
    def show_main_terminal():
        msg_in = ft.TextField(hint_text="Type data packet...", expand=True, border_color="#1A1A1A")
        
        def send_packet(e):
            if msg_in.value and st.db:
                st.db.collection("messages").add({
                    "u": st.uid, "t": msg_in.value, "r": st.role,
                    "ts": firestore.SERVER_TIMESTAMP,
                    "time": datetime.datetime.now().strftime("%H:%M")
                })
                msg_in.value = ""
                page.update()

        if st.db:
            st.db.collection("messages").order_by("ts", descending=False).limit_to_last(50).on_snapshot(sync_matrix_data)

        view_canvas.controls.clear()
        view_canvas.controls.append(
            ft.Column([
                # Header
                ft.Container(
                    content=ft.Row([
                        ft.Column([
                            ft.Text("STATUS: CONNECTED", color="#00FF00", size=10),
                            ft.Row([
                                ft.Text(st.uid, color="#FFFFFF", size=16, weight="bold"),
                                ft.Icon(ft.icons.VERIFIED, color="#00FF00", size=18, visible=(st.role=="ADMIN"))
                            ])
                        ]),
                        ft.IconButton(ft.icons.SEARCH, icon_color="#00FF00")
                    ], justify="spaceBetween"),
                    padding=20, bgcolor="#0D0D0D", border=ft.border.only(bottom=ft.border.BorderSide(1, "#1A1A1A"))
                ),
                # Navigation
                ft.Container(
                    content=ft.Row([
                        ft.TextButton("MATRIX_HUB", icon=ft.icons.HUB, icon_color="#00FF00"),
                        ft.TextButton("ADMIN_LOGS", icon=ft.icons.LOCK, icon_color="red", visible=(st.role=="ADMIN")),
                    ]),
                    padding=5
                ),
                # Чат
                ft.Container(content=message_log, expand=True, padding=10),
                # Ввод
                ft.Container(
                    content=ft.Row([
                        ft.IconButton(ft.icons.ADD_BOX, icon_color="#333333"),
                        msg_in,
                        ft.IconButton(ft.icons.SEND_ROUNDED, icon_color="#00FF00", on_click=send_packet)
                    ]),
                    padding=20, bgcolor="#050505"
                )
            ], expand=True, spacing=0)
        )
        page.update()

    show_auth_panel()

if __name__ == "__main__":
    ft.app(target=main)

