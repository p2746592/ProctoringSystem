#compiles text logs into a single session summary PDF
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os

def generate_pdf_from_txt(session_folder, output_path):
    #read all session log files in a defined order and write them into a PDF
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4
    margin = 50
    line_height = 14
    y = height - margin

    def write_section(title, text):
        #write log section into PDF
        nonlocal y
        c.setFont("Helvetica-Bold", 12)
        c.drawString(margin, y, title)
        y -= line_height + 4
        c.setFont("Helvetica", 10)

        for line in text.splitlines():
            if y <= margin:
                c.showPage()
                y = height - margin
                c.setFont("Helvetica", 10)

            #format screenshot log for cleaner PDF
            if title == "SCREENSHOTS LOG":
                parts = line.split("]")
                if len(parts) == 2:
                    timestamp = parts[0] + "]"
                    filename = os.path.basename(parts[1].strip())
                    line = f"{timestamp} {filename}"

            c.drawString(margin, y, line.strip())
            y -= line_height

        y -= line_height  #spacing after section

    #order which log files are inserted into PDF
    section_order = [
        "session_summary.txt",
        "keystrokes.txt",
        "screenshots_log.txt",
        "websites.txt",
        "alerts_log.txt",
        "mouse_log.txt"
    ]

    printed_something = False

    for filename in section_order:
        file_path = os.path.join(session_folder, filename)
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                if content.strip():
                    section_title = filename.replace("_", " ").replace(".txt", "").upper()
                    write_section(section_title, content)
                    printed_something = True
                else:
                    print(f"[ERROR] Skipped empty file: {filename}")
            except Exception as e:
                print(f"[ERROR] Could not read {filename}: {e}")
        else:
            print(f"[ERROR] Missing file: {filename}")

    if not printed_something:
        c.setFont("Helvetica", 12)
        c.drawString(margin, y, "No valid logs found in this PDF")

    c.save()
    print(f"[SUCCESS] PDF generated at: {output_path}")
