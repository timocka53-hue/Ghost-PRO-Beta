import flet as ft
import datetime
import firebase_admin
from firebase_admin import credentials, firestore, storage

# КОНФИГ ТВОЕГО ПРОЕКТА
try:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred, {
        'storageBucket': 'ghost-pro-5aa22.firebasestorage.app'
    })
    db = firestore.client()
    bucket = storage.bucket()
except:
    print("ВНИМАНИЕ: Работаем без прямого доступа к Firebase (проверь ключи)!")

def main(page: ft.Page):
    page.title = "GHOST PRO V13"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#000000"
    page.padding = 0

    state = {"uid": None, "role": "USER", "active_chat": None}
    chat_area = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True)
    side_bar = ft.Column(spacing=10, width=70)

    # ФИКС ОШИБКИ СО СКРИНА (FilePickerResultEvent -> flet.ControlEvent)
    def on_file_res(e: ft.ControlEvent):
        if e.files and state["active_chat"]:
            page.show_snack_bar(ft.SnackBar(ft.Text("Загрузка медиа...")))
            # Логика загрузки в storage тут...

    picker = ft.FilePicker(on_result=on_file_res)
    page.overlay.append(picker)

    def load_chat(chat_id, partner_uid):
        state["active_chat"] = chat_id
        chat_area.controls.clear()
        page.update()
        # Тут подключаем прослушку конкретной лички из Firestore

    def start_chat(target_uid):
        if not target_uid.startswith("@"): target_uid = f"@{target_uid}"
        chat_id = "_".join(sorted([state["uid"], target_uid]))
        side_bar.controls.append(
            ft.IconButton(ft.icons.PERSON_PIN, icon_color="#00FF00", tooltip=target_uid, 
                          on_click=lambda _: load_chat(chat_id, target_uid))
        )
        load_chat(chat_id, target_uid)
        page.update()

    def messenger_ui():
        page.clean()
        msg_in = ft.TextField(hint_text="CRYPT_MSG...", expand=True, border_color="#00FF00")
        search_in = ft.TextField(label="FIND @USER", border_color="#00FF00", width=150)
        
        page.add(
            ft.Row([
                ft.Container(content=side_bar, width=80, bgcolor="#050505", padding=10),
                ft.Column([
                    ft.Row([
                        search_in,
                        ft.IconButton(ft.icons.SEARCH, on_click=lambda _: start_chat(search_in.value)),
                        ft.IconButton(ft.icons.ADMIN_PANEL_SETTINGS, icon_color="red", visible=state["role"]=="ADMIN")
                    ]),
                    ft.Container(content=chat_area, expand=True),
                    ft.Row([
                        ft.IconButton(ft.icons.ATTACH_FILE, on_click=lambda _: picker.pick_files()),
                        msg_in,
                        ft.IconButton(ft.icons.SEND, icon_color="#00FF00")
                    ])
                ], expand=True, padding=15)
            ], expand=True)
        )

    def login_click(e):
        if user_in.value:
            state["uid"] = f"@{user_in.value}"
            if user_in.value == "adminpan" and pass_in.value == "TimaIssam2026":
                state["role"] = "ADMIN"
            messenger_ui()

    user_in = ft.TextField(label="USER_ID", border_color="#00FF00")
    pass_in = ft.TextField(label="SECURITY_KEY", password=True, border_color="#00FF00")
    page.add(
        ft.Container(
            content=ft.Column([
                ft.Text("GHOST_PRO_V13", size=40, weight="bold", color="#00FF00"),
                user_in, pass_in,
                ft.ElevatedButton("INIT_SESSION", on_click=login_click, width=300, bgcolor="#002200", color="#00FF00")
            ], horizontal_alignment="center", spacing=20),
            alignment=ft.alignment.center, expand=True
        )
    )

ft.app(target=main)
