import flet as ft
import firebase_admin
from firebase_admin import credentials, firestore
import datetime

def main(page: ft.Page):
    # --- БАЗОВЫЕ НАСТРОЙКИ ---
    page.title = "GHOST PRO V13"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#000000"
    page.padding = 0
    page.window_width = 450
    page.window_height = 850

    class AppState:
        db = None
        uid = "GHOST_USER"
        role = "USER"
        is_auth = False

    st = AppState()
    container = ft.Column(expand=True, spacing=0)
    page.add(container)

    # --- ПОДКЛЮЧЕНИЕ FIREBASE ---
    def init_db():
        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate("serviceAccountKey.json")
                firebase_admin.initialize_app(cred)
            st.db = firestore.client()
            return True
        except:
            return False

    # --- ЭЛЕМЕНТЫ ИНТЕРФЕЙСА ---
    msg_list = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True, spacing=15)

    def update_chat(docs, changes, read_time):
        msg_list.controls.clear()
        for doc in docs:
            data = doc.to_dict()
            is_adm = data.get("r") == "ADMIN"
            msg_list.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text(data.get("u"), size=10, color="#00FF00" if is_adm else "#777777", weight="bold"),
                            ft.Text(data.get("time"), size=9, color="#444444")
                        ], justify="spaceBetween"),
                        ft.Text(data.get("t"), color="#FFFFFF", size=15),
                    ], spacing=5),
                    padding=15, bgcolor="#0A0A0A" if not is_adm else "#001A00",
                    border=ft.border.all(1, "#1A1A1A" if not is_adm else "#00FF00"),
                    border_radius=15, margin=ft.margin.only(left=10, right=10)
                )
            )
        page.update()

    # --- ЭКРАН ВХОДА ---
    def show_auth():
        u_in = ft.TextField(label="IDENT_ID", border_color="#00FF00", prefix_text="@")
        p_in = ft.TextField(label="2FA_KEY", password=True, border_color="#00FF00", can_reveal_password=True)
        
        def run_login(e):
            if u_in.value:
                st.uid = f"@{u_in.value}"
                # Проверка админки
                if u_in.value == "adminpan" and p_in.value == "TimaIssam2026":
                    st.role = "ADMIN"
                
                if init_db():
                    show_hub()
                else:
                    page.snack_bar = ft.SnackBar(ft.Text("FIREBASE ERROR: CHECK serviceAccountKey.json"))
                    page.snack_bar.open = True
                    page.update()

        container.controls.clear()
        container.controls.append(
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.icons.FINGERPRINT, size=80, color="#00FF00"),
                    ft.Text("GHOST PRO", size=40, weight="bold", color="#00FF00"),
                    ft.Divider(height=30, color="transparent"),
                    u_in, p_in,
                    ft.ElevatedButton("INITIALIZE LINK", on_click=run_login, bgcolor="#002200", color="#00FF00", width=350, height=60)
                ], horizontal_alignment="center", alignment="center"),
                expand=True, padding=40
            )
        )
        page.update()

    # --- ЭКРАН ХАБА ---
    def show_hub():
        msg_in = ft.TextField(hint_text="Type encrypted message...", expand=True, border_color="#1A1A1A")
        
        def send_msg(e):
            if msg_in.value and st.db:
                st.db.collection("messages").add({
                    "u": st.uid, "t": msg_in.value, "r": st.role,
                    "ts": firestore.SERVER_TIMESTAMP,
                    "time": datetime.datetime.now().strftime("%H:%M")
                })
                msg_in.value = ""
                page.update()

        if st.db:
            st.db.collection("messages").order_by("ts", descending=False).limit_to_last(40).on_snapshot(update_chat)

        container.controls.clear()
        container.controls.append(
            ft.Column([
                ft.Container(
                    content=ft.Row([
                        ft.Column([
                            ft.Text("SYSTEM: ONLINE", color="#00FF00", size=10),
                            ft.Row([
                                ft.Text(st.uid, color="#FFFFFF", size=16, weight="bold"),
                                ft.Icon(ft.icons.VERIFIED, color="#00FF00", size=20, visible=(st.role=="ADMIN"))
                            ])
                        ]),
                        ft.IconButton(ft.icons.SEARCH, icon_color="#00FF00")
                    ], justify="spaceBetween"),
                    padding=20, bgcolor="#0A0A0A"
                ),
                ft.Container(content=msg_list, expand=True),
                ft.Container(
                    content=ft.Row([msg_in, ft.IconButton(ft.icons.SEND_ROUNDED, icon_color="#00FF00", on_click=send_msg)]),
                    padding=20, bgcolor="#050505"
                )
            ], expand=True)
        )
        page.update()

    show_auth()

if __name__ == "__main__":
    ft.app(target=main)


