import flet as ft
import firebase_admin
from firebase_admin import credentials, firestore
import datetime
import time

def main(page: ft.Page):
    # Конфигурация Матрицы
    page.title = "Ghost PRO"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#000000"
    page.padding = 0
    page.window_width = 450
    page.window_height = 850
    
    state = {"db": None, "uid": None, "role": "USER", "target": "GLOBAL"}

    # Скрытая инициализация (чтобы не висло)
    def init_db():
        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate("serviceAccountKey.json")
                firebase_admin.initialize_app(cred)
            state["db"] = firestore.client()
        except: pass

    container = ft.Column(expand=True)
    page.add(container)

    # --- ЭКРАН 1: АВТОРИЗАЦИЯ 2FA ---
    def auth_view():
        u_in = ft.TextField(label="GHOST_ID", border_color="#00FF00", prefix_text="@")
        p_in = ft.TextField(label="2FA_KEY", password=True, border_color="#00FF00", can_reveal_password=True)
        
        def start_link(e):
            if u_in.value:
                state["uid"] = f"@{u_in.value}"
                if u_in.value == "adminpan" and p_in.value == "TimaIssam2026":
                    state["role"] = "ADMIN"
                init_db()
                terminal_view()

        container.controls.clear()
        container.controls.append(
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.icons.SECURITY, size=100, color="#00FF00"),
                    ft.Text("GHOST PRO V13", size=45, weight="bold", color="#00FF00"),
                    ft.Text("SYSTEM INITIALIZATION...", color="#555555"),
                    ft.Divider(height=50, color="transparent"),
                    u_in, p_in,
                    ft.ElevatedButton("CONNECT TO MATRIX", on_click=start_link, bgcolor="#002200", color="#00FF00", width=350, height=60)
                ], horizontal_alignment="center", alignment="center"),
                expand=True, padding=40
            )
        )
        page.update()

    # --- ЭКРАН 2: ПОЛНОФУНКЦИОНАЛЬНЫЙ ТЕРМИНАЛ ---
    def terminal_view():
        chat_list = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True)
        msg_in = ft.TextField(hint_text="Type encrypted message...", expand=True, border_color="#1A1A1A")

        def send_data(e):
            if msg_in.value and state["db"]:
                state["db"].collection("messages").add({
                    "u": state["uid"], "t": msg_in.value, "r": state["role"],
                    "ts": firestore.SERVER_TIMESTAMP,
                    "time": datetime.datetime.now().strftime("%H:%M")
                })
                msg_in.value = ""
                page.update()

        def stream_chat(docs, changes, read_time):
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
                        padding=12, bgcolor="#0A0A0A" if not is_adm else "#001100",
                        border=ft.border.all(1, "#1A1A1A" if not is_adm else "#00FF00"),
                        border_radius=10
                    )
                )
            page.update()

        if state["db"]:
            state["db"].collection("messages").order_by("ts", descending=False).limit_to_last(30).on_snapshot(stream_chat)

        container.controls.clear()
        container.controls.append(
            ft.Column([
                ft.Container(
                    content=ft.Row([
                        ft.Text(f"ACTIVE_SESSION: {state['uid']}", color="#00FF00", weight="bold"),
                        ft.Icon(ft.icons.VERIFIED, color="#00FF00", visible=(state["role"]=="ADMIN"))
                    ], justify="spaceBetween"),
                    padding=15, bgcolor="#111111"
                ),
                ft.Container(content=chat_list, expand=True, padding=10),
                ft.Row([
                    ft.IconButton(ft.icons.SEARCH, icon_color="#00FF00"),
                    msg_in,
                    ft.IconButton(ft.icons.SEND_ROUNDED, icon_color="#00FF00", on_click=send_data)
                ], padding=10)
            ], expand=True)
        )
        page.update()

    auth_view()

if __name__ == "__main__":
    ft.app(target=main)
