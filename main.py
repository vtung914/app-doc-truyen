import flet as ft
from pypdf import PdfReader
import os
import asyncio

async def main(page: ft.Page):
    page.title = "App Đọc Truyện Audio PDF"
    page.theme_mode = ft.ThemeMode.DARK
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    file_path_ref = ft.Ref[ft.Text]()
    txt_bat_dau = ft.TextField(label="Trang Bắt Đầu", value="1", keyboard_type=ft.KeyboardType.NUMBER, width=150)
    txt_ket_thuc = ft.TextField(label="Trang Kết Thúc", value="5", keyboard_type=ft.KeyboardType.NUMBER, width=150)
    lbl_status = ft.Text(value="Chưa chọn file truyện", color="blue200")

    async def pick_files_result(e: ft.FilePickerResultEvent):
        if e.files:
            file_path_ref.current.value = e.files[0].path
            lbl_status.value = f"📁 Đã chọn: {e.files[0].name}"
        else:
            lbl_status.value = "❌ Bạn chưa chọn file nào!"
        page.update()

    file_picker = ft.FilePicker()
    file_picker.on_result = pick_files_result
    page.overlay.append(file_picker)

    async def bat_dau_doc_truyen(e):
        path = file_path_ref.current.value
        if not path:
            lbl_status.value = "❌ Vui lòng chọn file PDF trước!"
            page.update()
            return
        try:
            reader = PdfReader(path)
            tong_trang = len(reader.pages)
            bd = int(txt_bat_dau.value)
            kt = int(txt_ket_thuc.value)
            if bd < 1 or kt > tong_trang or bd > kt:
                lbl_status.value = f"❌ Số trang không hợp lệ (Tổng: {tong_trang} trang)"
                page.update()
                return
            lbl_status.value = f"📖 Đang xử lý dữ liệu từ trang {bd} đến {kt}..."
            page.update()
            van_ban = ""
            for i in range(bd - 1, kt):
                text = reader.pages[i].extract_text()
                if text:
                    van_ban += text + "\n"
            if len(van_ban.strip()) < 5:
                lbl_status.value = "❌ Không tìm thấy chữ trong các trang đã chọn."
                page.update()
                return
            lbl_status.value = "🔊 🎧 Đang phát Audio truyện..."
            page.update()
            try:
                await page.tts.stop()
            except:
                pass
            page.tts.text = van_ban
            await page.tts.speak()
        except Exception as ex:
            lbl_status.value = f"❌ Lỗi hệ thống: {str(ex)}"
            page.update()

    async def mo_chon_file(e):
        await file_picker.pick_files(allowed_extensions=["pdf"])

    page.add(
        ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text("AUDIO BOOK PDF", size=24, weight=ft.FontWeight.BOLD, color="amber"),
                        lbl_status,
                        ft.Text(ref=file_path_ref, visible=False), 
                        ft.Button("📁 CHỌN FILE PDF TRUYỆN", icon="folder_open", on_click=mo_chon_file),
                        ft.Row([txt_bat_dau, txt_ket_thuc], alignment=ft.MainAxisAlignment.CENTER),
                        ft.Divider(),
                        ft.IconButton(icon="play_circle_filled", icon_color="greenaccent", icon_size=60, on_click=bat_dau_doc_truyen),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20
                ), padding=30
            )
        )
    )

ft.run(main)
