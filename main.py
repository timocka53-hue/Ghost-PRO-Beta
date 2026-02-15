import flet as ft
import datetime
import base64

def main(page: ft.Page):
    page.title = "GHOST PRO V13 ULTIMATE"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#000000"
    page.padding = 0
    page.window_full_screen = True
    
    # Состояние системы
    state = {
        "uid": "@guest",
        "role": "USER",
        "avatar_b64": None,
        "users_db": ["@ADMIN_CORE", "@root", "@ghost_user"]
    }

    # --- РАБОТА С РЕАЛЬНЫМИ ФАЙЛАМИ ---
    def on_file_result(e: ft.FilePickerResultEvent):
        if e.files:
            for f in e.files:
                with open(f.path, "rb") as file_raw:
                    b64_data = base64.b64encode(file_raw.read()).decode()
                
                ext = f.name.split(".")[-1].lower()
                m_type = "image" if ext in ["jpg", "png", "jpeg"] else "video" if ext in ["mp4"] else "audio" if ext in ["mp3", "wav"] else "file"

                page.pubsub.send_all(str({
                    "user": state["uid"],
                    "type": m_type,
                    "name": f.name,
                    "data": b64_data,
                    "time": datetime.datetime.now().strftime("%H:%M")
                }))

    file_picker = ft.FilePicker(on_result=on_file_result)
    page.overlay.append(file_picker)

    # --- ПРИЕМ СООБЩЕНИЙ В РЕАЛЬНОМ ВРЕМЕНИ ---
    def on_broadcast(msg_str):
        data = eval(msg_str)
        is_me = data["user"] == state["uid"]
        
        content = ft.Column(spacing=5)
        content.controls.append(ft.Text(data["user"], size=10, color="#00FF00", weight="bold"))
        
        if data["type"] == "text":
            content.controls.append(ft.Text(data["text"], color="white", size=16))
        elif data["type"] == "image":
            content.controls.append(ft.Image(src_base64=data["data"], width=300, border_radius=10))
        elif data.get("type") in ["video", "audio", "file"]:
            content.controls.append(ft.Row([ft.Icon(ft.icons.ATTACH_FILE, color="#00FF00"), ft.Text(data["name"], color="white")]))

        chat_list.controls.append(
            ft.Container(
                content=content, padding=12, bgcolor="#0A0A0A",
                border=ft.border.all(1, "#00FF00" if is_me else "#004400"),
                border_radius=10, margin=ft.margin.only(bottom=10)
            )
        )
        page.update()

    page.pubsub.subscribe(on_broadcast)

    # --- ИНТЕРФЕЙСЫ ---
    chat_list = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True)
    msg_input = ft.TextField(hint_text=">>> DATA_INPUT", expand=True, border_color="#00FF00", color="#00FF00")

    def send_msg(e):
        if msg_input.value:
            page.pubsub.send_all(str({"user": state["uid"], "type": "text", "text": msg_input.value, "time": datetime.datetime.now().strftime("%H:%M")}))
            msg_input.value = ""
            page.update()

    def show_main():
        page.clean()
        page.add(
            ft.Container(content=ft.Column([
                ft.Row([
                    ft.Text("GHOST_NET", color="#00FF00", weight="bold", size=22),
                    ft.Row([
                        ft.IconButton(ft.icons.ADMIN_PANEL_SETTINGS, icon_color="red", visible=state["role"]=="ADMIN", on_click=lambda _: show_admin()),
                        ft.IconButton(ft.icons.PERSON, icon_color="#00FF00", on_click=lambda _: show_profile())
                    ])
                ], justify="spaceBetween"),
                ft.TextField(hint_text="SEARCH_DATABASE...", prefix_icon=ft.icons.SEARCH, height=40, border_color="#003300"),
                ft.Container(content=chat_list, expand=True, border=ft.border.all(1, "#002200"), padding=10),
                ft.Row([
                    ft.IconButton(ft.icons.ATTACH_FILE, icon_color="#00FF00", on_click=lambda _: file_picker.pick_files()),
                    msg_input,
                    ft.IconButton(ft.icons.SEND, icon_color="#00FF00", on_click=send_msg)
                ])
            ]), expand=True, padding=10)
        )

    def show_admin():
        page.clean()
        page.add(ft.Column([ft.Text("ROOT_PANEL", color="red", size=30), ft.ElevatedButton("BAN_USER"), ft.ElevatedButton("BACK", on_click=lambda _: show_main())], horizontal_alignment="center"))

    def show_profile():
        page.clean()
        page.add(ft.Column([ft.CircleAvatar(radius=60, bgcolor="#001100"), ft.Text(state["uid"], size=30, color="#00FF00"), ft.ElevatedButton("BACK", on_click=lambda _: show_main())], horizontal_alignment="center"))

    # ВХОД
    def login(e):
        if login_in.value == "adminpan" and pass_in.value == "TimaIssam2026":
            state["role"], state["uid"] = "ADMIN", "@ADMIN_CORE"
        else: state["uid"] = f"@{login_in.value}"
        show_main()

    login_in = ft.TextField(label="UID")
    pass_in = ft.TextField(label="KEY", password=True)
    page.add(ft.Column([ft.Text("GHOST_SYSTEM", size=40, color="#00FF00"), login_in, pass_in, ft.ElevatedButton("INIT", on_click=login)], horizontal_alignment="center"))

ft.app(target=main)
 
