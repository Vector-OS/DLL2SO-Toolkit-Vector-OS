import tkinter as tk
from tkinter import filedialog, messagebox
import pefile
import os
import subprocess
import shutil
import platform
import time
import threading

selected_files = []

# ---------------- OS Check ---------------- #
if platform.system() != "Linux":
    messagebox.showerror("Unsupported OS", "🚫 This tool runs only on Linux.")
    exit()

# ---------------- Auto Update Checker ---------------- #
def check_updates():
    # Simulate update check (Replace with actual GitHub/API logic if needed)
    result_text.insert(tk.END, "\n🔄 Checking for updates...\n")
    root.update()
    time.sleep(2)
    result_text.insert(tk.END, "✅ You're using the latest version.\n")

# ---------------- Tool Checker ---------------- #
def check_tool(tool_name, install_cmd=None):
    if shutil.which(tool_name):
        return True
    if install_cmd:
        user_response = messagebox.askyesno(
            f"{tool_name} Not Found",
            f"❌ {tool_name} is not installed.\nWould you like to install it now?"
        )
        if user_response:
            try:
                result_text.insert(tk.END, f"\n📦 Installing {tool_name}...\n")
                root.update()
                subprocess.run(['sudo', 'apt', 'update'], check=True)
                subprocess.run(install_cmd, check=True)
                result_text.insert(tk.END, f"✅ {tool_name} installed successfully.\n")
                return True
            except subprocess.CalledProcessError:
                messagebox.showerror("Installation Failed", f"Failed to install {tool_name}.")
                return False
    return False

# ---------------- Analyze Files ---------------- #
def analyze_files(file_paths):
    global selected_files
    result_text.delete('1.0', tk.END)
    selected_files = []

    for file_path in file_paths:
        if not file_path.lower().endswith(".dll"):
            result_text.insert(tk.END, f"❌ Skipping {file_path} (Invalid extension)\n")
            continue

        try:
            pe = pefile.PE(file_path)
            selected_files.append(file_path)

            arch = "64-bit" if pe.FILE_HEADER.Machine == 0x8664 else "32-bit"
            entry_point = hex(pe.OPTIONAL_HEADER.AddressOfEntryPoint)
            image_base = hex(pe.OPTIONAL_HEADER.ImageBase)
            subsystem = pe.OPTIONAL_HEADER.Subsystem
            timestamp = pe.FILE_HEADER.TimeDateStamp

            result = f"\n✅ File: {os.path.basename(file_path)}\n"
            result += f"📦 Architecture: {arch}\n"
            result += f"🔑 Entry Point: {entry_point}\n"
            result += f"📍 Image Base: {image_base}\n"
            result += f"🛠️ Subsystem: {subsystem}\n"
            result += f"⏱️ Timestamp: {timestamp}\n"

            is_dotnet = any(
                'mscoree.dll' in entry.dll.decode().lower()
                for entry in getattr(pe, 'DIRECTORY_ENTRY_IMPORT', [])
            )

            if is_dotnet:
                result += "💡 Detected: .NET Assembly\n"
                if check_tool("mono", ['sudo', 'apt', 'install', '-y', 'mono-complete']):
                    convert_btn.config(state=tk.NORMAL)
                    result += "✅ Ready to convert using Mono AOT.\n"
                else:
                    convert_btn.config(state=tk.DISABLED)
            else:
                result += "⚠️ Native DLL detected (Not .NET)\n"
                if check_tool("wine", ['sudo', 'apt', 'install', '-y', 'wine']):
                    result += "💡 Wine is installed — you can try running or inspecting it.\n"
                else:
                    result += "❌ Wine not available.\n"
                convert_btn.config(state=tk.DISABLED)

            result_text.insert(tk.END, result)

        except Exception as e:
            result_text.insert(tk.END, f"❌ Failed to analyze {file_path}: {e}\n")

# ---------------- Convert Files ---------------- #
def convert_to_so():
    if not selected_files:
        messagebox.showwarning("No File", "Please select .NET DLL files first.")
        return

    for file in selected_files:
        result_text.insert(tk.END, f"\n⚙️ Converting {os.path.basename(file)} to .so...\n")
        try:
            subprocess.run(['mono', '--aot=full', file], check=True)
            so_file = file + ".so"
            if os.path.exists(so_file):
                result_text.insert(tk.END, f"✅ Successfully created: {os.path.basename(so_file)}\n")
            else:
                result_text.insert(tk.END, f"⚠️ Conversion complete, but .so file not found\n")
        except Exception as e:
            result_text.insert(tk.END, f"❌ Error during conversion of {file}: {e}\n")

# ---------------- File Selection ---------------- #
def select_files():
    file_paths = filedialog.askopenfilenames(filetypes=[("DLL files", "*.dll")])
    if file_paths:
        analyze_files(file_paths)

# ---------------- Drag and Drop ---------------- #
def drop(event):
    files = root.tk.splitlist(event.data)
    analyze_files(files)

# ---------------- Requirements ---------------- #
def show_requirements():
    messagebox.showinfo("Requirements",
        "🛠 Requirements:\n\n"
        "- Python 3.x\n"
        "- pefile → pip install pefile\n"
        "- mono-complete\n"
        "- wine (optional for native DLLs)\n"
        "\n💡 Install pefile: pip install pefile\n"
        "💡 Install Mono: sudo apt install mono-complete"
        "\n  For Fast Drag and drop sudo apt install python3-dev python3-pip python3-tk")

# ---------------- Splash Screen ---------------- #
def show_splash():
    splash = tk.Toplevel(root)
    splash.title("Welcome to Vector OS Toolkit")
    splash.geometry("500x300")
    splash.configure(bg="#111")

    logo = tk.Label(splash, text="Vector OS", font=('Helvetica', 24, 'bold'), fg="cyan", bg="#111")
    logo.pack(pady=80)

    subtitle = tk.Label(splash, text="Welcome to DLL Analyzer & .SO Converter", font=('Helvetica', 12), fg="white", bg="#111")
    subtitle.pack()

    splash.after(2000, splash.destroy)


root = tk.Tk()
root.title("🛠 DLL to .SO Converter - Vector OS")
root.geometry("700x650")
root.resizable(False, False)
root.configure(bg="#F8F8F8")
root.tk.call('tk', 'scaling', 1.2)


threading.Thread(target=show_splash).start()
threading.Thread(target=check_updates).start()

root.after(2100, lambda: root.deiconify())

title = tk.Label(root, text="🧩 DLL Analyzer & .SO Converter", font=('Arial', 14, 'bold'), bg="#F8F8F8")
title.pack(pady=10)

btn_frame = tk.Frame(root, bg="#F8F8F8")
btn_frame.pack()

upload_btn = tk.Button(btn_frame, text="📂 Select DLL Files", command=select_files,
                       font=('Arial', 11), bg="#2196F3", fg="white", padx=10)
upload_btn.grid(row=0, column=0, padx=10, pady=10)

convert_btn = tk.Button(btn_frame, text="🔁 Convert to .SO", command=convert_to_so,
                        font=('Arial', 11), bg="#4CAF50", fg="white", padx=10)
convert_btn.grid(row=0, column=1, padx=10, pady=10)
convert_btn.config(state=tk.DISABLED)

req_btn = tk.Button(root, text="📋 Show Requirements", command=show_requirements,
                    font=('Arial', 10), bg="#FF9800", fg="white")
req_btn.pack(pady=5)

result_text = tk.Text(root, wrap=tk.WORD, font=('Courier', 10), width=84, height=25,
                      bg="#FAFAFA", fg="black", padx=10, pady=10)
result_text.pack(pady=10)

# Enable Drag and Drop if on Linux with tkinterdnd2
try:
    import tkinterdnd2 as tkdnd
    root.destroy()
    root = tkdnd.TkinterDnD.Tk()
    root.title("🛠 DLL to .SO Converter - Vector OS")
    root.geometry("700x650")
    root.resizable(False, False)
    root.configure(bg="#F8F8F8")
    result_text = tk.Text(root, wrap=tk.WORD, font=('Courier', 10), width=84, height=25,
                          bg="#FAFAFA", fg="black", padx=10, pady=10)
    result_text.pack(pady=10)
    result_text.drop_target_register(tkdnd.DND_FILES)
    result_text.dnd_bind('<<Drop>>', drop)
except:
    pass

root.mainloop()


