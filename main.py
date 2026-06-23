import flet as ft
from pypdf import PdfReader
import os
import asyncio

async def main(page: ft.Page):
    page.title = "App Đọc Truyện Audio PDF"
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = ft.ScrollMode.AUTO

    # Biến lưu trữ dữ liệu
    file_path_ref = ft.Ref[ft.Text]()
    txt_bat_dau = ft.TextField(label="Trang Bắt Đầu", value="1", keyboard_type=ft.KeyboardType.NUMBER, width=100)
    txt_ket_thuc = ft.TextField(label="Trang Kết Thúc", value="5", keyboard_type=ft.KeyboardType.NUMBER, width=100)
    lbl_status = ft.Text(value="Chưa chọn file truyện", color="blue200")
    
    # Khu vực hiển thị nội dung truyện
    txt_noi_dung_truyen = ft.Text(value="", size=16, color="white", selectable=True)

    # Thanh chỉnh tốc độ đọc (Mặc định là 1.0)
    slider_toc_do = ft.Slider(min=0.5, max=2.0, divisions=6, label="{value}x", value=1.0)

    # Hàm xử lý khi chọn file PDF xong
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

    # Hàm xử lý trích xuất chữ và phát âm thanh
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

            lbl_status.value = "📖 Đang trích xuất chữ từ PDF..."
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

            # Hiển thị chữ lên màn hình cho người dùng xem
            txt_noi_dung_truyen.value = van_ban
            lbl_status.value = f"🔊 Đang phát Audio (Tốc độ: {slider_toc_do.value}x)..."
            page.update()
            
            # Cấu hình giọng đọc và tốc độ
            try:
                await page.tts.stop()
            except:
                pass
                
            page.tts.text = van_ban
            page.tts.rate = float(slider_toc_do.value)
            await page.tts.speak()

        except Exception as ex:
            lbl_status.value = f"❌ Lỗi hệ thống: {str(ex)}"
            page.update()

    async def dung_doc_truyen(e):
        try:
            await page.tts.stop()
            lbl_status.value = "⏹️ Đã dừng phát."
            page.update()
        except:
            pass

    async def mo_chon_file(e):
        await file_picker.pick_files(allowed_extensions=["pdf"])

    # Giao diện hiển thị
    page.add(
        ft.Container(
            content=ft.Column(
                [
                    ft.Text("AUDIO BOOK PDF PRO", size=24, weight=ft.FontWeight.BOLD, color="amber"),
                    lbl_status,
                    ft.Text(ref=file_path_ref, visible=False), 
                    
                    ft.ElevatedButton("📁 CHỌN FILE PDF TRUYỆN", icon="folder_open", on_click=mo_chon_file),
                    
                    ft.Row([txt_bat_dau, txt_ket_thuc], alignment=ft.MainAxisAlignment.CENTER),
                    
                    ft.Text("Chỉnh tốc độ đọc:", size=14, color="amber200"),
                    slider_toc_do,
                    
                    ft.Row(
                        [
                            ft.IconButton(icon="play_circle_filled", icon_color="greenaccent", icon_size=50, tooltip="Phát", on_click=bat_dau_doc_truyen),
                            ft.IconButton(icon="stop_circle", icon_color="redaccent", icon_size=50, tooltip="Dừng", on_click=dung_doc_truyen),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER
                    ),
                    ft.Divider(),
                    ft.Text("NỘI DUNG TRUYỆN:", weight=ft.FontWeight.BOLD, color="amber"),
                    ft.Container(
                        content=txt_noi_dung_truyen,
                        padding=10,
                        border=ft.border.all(1, "grey700"),
                        border_radius=5,
                        bgcolor="black"
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=15
            ),
            padding=20
        )
    )

ft.run(main)
