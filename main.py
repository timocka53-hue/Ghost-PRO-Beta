import flet as ft
import firebase_admin
from firebase_admin import credentials, firestore, storage
import datetime
import base64

def main(page: ft.Page):
    # Глобальные настройки дизайна (Тёмный киберпанк)
    page.title = "GHOST PRO V13: ELITE"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#000000"
    page.padding = 0
    page.window_width = 450
    page.window_height = 850
    page.scroll = ft.ScrollMode.HIDDEN

    class GhostSystem:
        db = None
        bucket = None
        user_id = "ANON_GHOST"
        role = "USER"
        is_banned = False

    gs = GhostSystem()

    # --- КРИПТОГРАФИЯ (Base64 Encryption) ---
    def crypt(text, mode="enc"):
        try:
            if mode == "enc":
                return base64.b64encode(text.encode()).decode()
            return base64.b64decode(text.encode()).decode()
        except: return text

    # --- CONNECT TO FIREBASE ---
    def connect_to_matrix():
        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate("serviceAccountKey.json")
                firebase_admin.initialize_app(cred, {'storageBucket': 'YOUR_PROJECT_ID.appspot.com'})
            gs.db = firestore.client()
            gs.bucket = storage.bucket()
            return True
        except: return False

    container = ft.Column(expand=True, spacing=0)
    page.add(container)

    # --- UI КОМПОНЕНТЫ ---
    message_log = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True, spacing=15)
    
    def on_snapshot(docs, changes, read_time):
        message_log.controls.clear()
        for doc in docs:
            m = doc.to_dict()
            is_adm = m.get("r") == "ADMIN"
            message_log.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text(m.get("u"), size=10, color="#00FF00" if is_adm else "#666666", weight="bold"),
                            ft.Text(m.get("time"), size=9, color="#222222")
                        ], justify="spaceBetween"),
                        ft.Text(crypt(m.get("t"), "dec"), color="#FFFFFF", size=15),
                        ft.Image(src=m.get("media"), width=250, border_radius=10, visible=bool(m.get("media")))
                    ], spacing=5),
                    padding=15, 
                    bgcolor="#0A0A0A" if not is_adm else "#001A00",
                    border=ft.border.all(1, "#1A1A1A" if not is_adm else "#00FF00"),
                    border_radius=15, margin=ft.margin.only(left=10, right=10)
                )
            )
        page.update()

    # --- ЭКРАН 1: АВТОРИЗАЦИЯ (БЕЗ КОНСОЛИ!) ---
    def show_auth_gate():
        u_field = ft.TextField(label="IDENT_ID", border_color="#00FF00", prefix_text="@", color="#00FF00")
        p_field = ft.TextField(label="2FA_KEY", password=True, border_color="#00FF00", can_reveal_password=True)
        
        def start_uplink(e):
            if not u_field.value: return
            
            # Твои требования по админке
            if u_field.value == "adminpan" and p_field.value == "TimaIssam2026":
                gs.role = "ADMIN"
            
            gs.user_id = f"@{u_field.value}"
            if connect_to_matrix():
                show_main_hub()
            else:
                page.snack_bar = ft.SnackBar(ft.Text("CRITICAL ERROR: DB OFFLINE"), bgcolor="red")
                page.snack_bar.open = True
                page.update()

        container.controls.clear()
        container.controls.append(
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.icons.VAPES, size=100, color="#00FF00"),
                    ft.Text("GHOST PRO V13", size=35, weight="bold", color="#00FF00"),
                    ft.Text("ENCRYPTED NETWORK ACCESS", size=10, color="#00FF00"),
                    ft.Divider(height=50, color="transparent"),
                    u_field, p_field,
                    ft.ElevatedButton("EXECUTE UPLINK", on_click=start_uplink, bgcolor="#003300", color="#00FF00", width=350, height=60)
                ], horizontal_alignment="center", alignment="center"),
                expand=True, padding=40
            )
        )
        page.update()

    # --- ЭКРАН 2: MAIN HUB (Чат, Медиа, Админка) ---
    def show_main_hub():
        input_msg = ft.TextField(hint_text="Type encrypted packet...", expand=True, border_color="#1A1A1A")
        
        def send_data(e):
            if input_msg.value and gs.db:
                gs.db.collection("messages").add({
                    "u": gs.user_id, "t": crypt(input_msg.value, "enc"), 
                    "r": gs.role, "ts": firestore.SERVER_TIMESTAMP,
                    "time": datetime.datetime.now().strftime("%H:%M")
                })
                input_msg.value = ""
                page.update()

        if gs.db:
            gs.db.collection("messages").order_by("ts", descending=False).limit_to_last(50).on_snapshot(on_snapshot)

        container.controls.clear()
        container.controls.append(
            ft.Column([
                # Панель управления
                ft.Container(
                    content=ft.Row([
                        ft.Column([
                            ft.Text("SIGNAL: SECURE", color="#00FF00", size=10),
                            ft.Text(gs.user_id, size=20, weight="bold", color="white")
                        ]),
                        ft.Row([
                            ft.IconButton(ft.icons.SUPPORT_AGENT, icon_color="#00FF00", on_click=lambda _: show_support()),
                            ft.IconButton(ft.icons.ADMIN_PANEL_SETTINGS, icon_color="red", visible=(gs.role=="ADMIN"), on_click=lambda _: show_admin_panel())
                        ])
                    ], justify="spaceBetween"),
                    padding=20, bgcolor="#0A0A0A"
                ),
                # Область чата
                ft.Container(content=message_log, expand=True, padding=10),
                # Поле ввода
                ft.Container(
                    content=ft.Row([
                        ft.IconButton(ft.icons.ADD_A_PHOTO, icon_color="#333333"),
                        input_msg,
                        ft.IconButton(ft.icons.SEND_ROUNDED, icon_color="#00FF00", on_click=send_data)
                    ]),
                    padding=20, bgcolor="#000000"
                )
            ], expand=True)
        )
        page.update()

    # --- ЭКРАН 3: АДМИНКА (БАНЫ, ЧИСТКА) ---
    def show_admin_panel():
        container.controls.clear()
        container.controls.append(
            ft.Column([
                ft.AppBar(title=ft.Text("SYSTEM OVERRIDE"), bgcolor="#660000"),
                ft.ListTile(title=ft.Text("BAN USER @target"), leading=ft.Icon(ft.icons.PERSON_OFF), on_click=lambda _: None),
                ft.ListTile(title=ft.Text("WIPE ALL DATA"), leading=ft.Icon(ft.icons.DELETE_FOREVER), icon_color="red", on_click=lambda _: None),
                ft.ElevatedButton("BACK TO HUB", on_click=lambda _: show_main_hub())
            ])
        )
        page.update()

    # --- ЭКРАН 4: ТЕХПОДДЕРЖКА ---
    def show_support():
        container.controls.clear()
        container.controls.append(
            ft.Column([
                ft.AppBar(title=ft.Text("SUPPORT TERMINAL"), bgcolor="#004400"),
                ft.Padding(padding=20, content=ft.Column([
                    ft.TextField(label="Subject", border_color="#00FF00"),
                    ft.TextField(label="Problem Description", multiline=True, min_lines=5, border_color="#00FF00"),
                    ft.ElevatedButton("SEND TICKET", width=400, bgcolor="#002200", color="#00FF00")
                ])),
                ft.TextButton("BACK", on_click=lambda _: show_main_hub())
            ])
        )
        page.update()

    show_auth_gate()

if __name__ == "__main__":
    ft.app(target=main)

