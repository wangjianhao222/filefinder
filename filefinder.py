import os
import platform
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import string
from threading import Thread
import fnmatch
import time
from queue import Queue

class FileFinderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Enhanced File Finder")
        self.root.geometry("800x600")
        self.search_queue = Queue()
        self.cache = {}  # 缓存目录结构
        self.system = platform.system()  # 初始化 system 属性
        self.setup_gui()

    def get_drives(self):
        """获取系统中的可用磁盘"""
        drives = []
        if self.system == "Windows":
            for drive in string.ascii_uppercase:
                drive_path = f"{drive}:\\"
                if os.path.exists(drive_path):
                    drives.append(drive_path)
        elif self.system in ("Linux", "Darwin"):
            drives.append("/home")
            media_path = "/media" if self.system == "Linux" else "/Volumes"
            if os.path.exists(media_path):
                drives.extend([os.path.join(media_path, d) for d in os.listdir(media_path) if os.path.isdir(os.path.join(media_path, d))])
        else:
            drives.append("/")
        return drives

    def find_file(self, filename_pattern, search_path, ext_filter, min_size, max_size, result_text, progress_label):
        """在指定路径中查找文件，支持过滤和模糊匹配"""
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, f"Searching for '{filename_pattern}' in '{search_path}'...\n")
        progress_label.config(text="Progress: Searching...")

        found_files = []
        start_time = time.time()

        # 检查缓存
        cache_key = (search_path, filename_pattern, ext_filter, min_size, max_size)
        if cache_key in self.cache:
            found_files = self.cache[cache_key]
            result_text.insert(tk.END, "Using cached results...\n")
        else:
            try:
                for root, dirs, files in os.walk(search_path, followlinks=False):
                    for file in files:
                        if fnmatch.fnmatch(file.lower(), f"*{filename_pattern.lower()}*"):
                            if ext_filter and not file.lower().endswith(ext_filter.lower()):
                                continue
                            file_path = os.path.join(root, file)
                            try:
                                file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
                                if (min_size is not None and file_size < min_size) or (max_size is not None and file_size > max_size):
                                    continue
                                found_files.append((file, file_path, file_size))
                            except:
                                continue
                    self.search_queue.put(1)  # 更新进度
            except Exception as e:
                result_text.insert(tk.END, f"Error while searching: {e}\n")
            self.cache[cache_key] = found_files

        # 排序结果
        sort_option = self.sort_var.get()
        if sort_option == "Name":
            found_files.sort(key=lambda x: x[0])
        elif sort_option == "Path":
            found_files.sort(key=lambda x: x[1])
        elif sort_option == "Size":
            found_files.sort(key=lambda x: x[2], reverse=True)

        # 显示结果
        if found_files:
            result_text.insert(tk.END, f"\nFound {len(found_files)} file(s) in {time.time() - start_time:.2f} seconds:\n")
            for file, file_path, file_size in found_files:
                result_text.insert(tk.END, f"{file_path} (Size: {file_size:.2f} MB)\n")
        else:
            result_text.insert(tk.END, "\nNo files found.\n")
        progress_label.config(text="Progress: Done")

    def browse_directory(self):
        """打开目录选择对话框"""
        directory = filedialog.askdirectory()
        if directory:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, directory)

    def start_search(self):
        """启动文件搜索"""
        filename = self.filename_entry.get().strip()
        search_path = self.path_entry.get().strip() or self.drive_var.get()
        ext_filter = self.ext_entry.get().strip().lstrip(".")
        min_size = self.min_size_entry.get().strip()
        max_size = self.max_size_entry.get().strip()

        if not filename:
            messagebox.showwarning("Input Error", "Please enter a filename pattern.")
            return

        min_size = float(min_size) if min_size else None
        max_size = float(max_size) if max_size else None

        if search_path == "All Drives":
            drives = self.get_drives()
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"Searching in all drives: {', '.join(drives)}...\n")
            for drive in drives:
                Thread(target=self.find_file, args=(filename, drive, ext_filter, min_size, max_size, self.result_text, self.progress_label), daemon=True).start()
        else:
            Thread(target=self.find_file, args=(filename, search_path, ext_filter, min_size, max_size, self.result_text, self.progress_label), daemon=True).start()

    def update_progress(self):
        """更新搜索进度"""
        while not self.search_queue.empty():
            self.search_queue.get()
            self.root.update()
        self.root.after(100, self.update_progress)

    def setup_gui(self):
        """创建图形化界面"""
        # 文件名输入
        tk.Label(self.root, text="Filename Pattern:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.filename_entry = tk.Entry(self.root, width=50)
        self.filename_entry.grid(row=0, column=1, padx=5, pady=5, columnspan=2)
        tk.Label(self.root, text="(e.g., doc for document.txt)").grid(row=0, column=3, padx=5, pady=5, sticky="w")

        # 搜索路径输入
        tk.Label(self.root, text="Search Path:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.path_entry = tk.Entry(self.root, width=40)
        self.path_entry.insert(0, "C:\\" if self.system == "Windows" else "/home")
        self.path_entry.grid(row=1, column=1, padx=5, pady=5)
        tk.Button(self.root, text="Browse", command=self.browse_directory).grid(row=1, column=2, padx=5, pady=5)

        # 磁盘选择
        tk.Label(self.root, text="Or Select Drive:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.drive_var = tk.StringVar(value="All Drives")
        drives = ["All Drives"] + self.get_drives()
        tk.OptionMenu(self.root, self.drive_var, *drives).grid(row=2, column=1, padx=5, pady=5, sticky="w")

        # 文件类型过滤
        tk.Label(self.root, text="File Extension:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.ext_entry = tk.Entry(self.root, width=20)
        self.ext_entry.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        tk.Label(self.root, text="(e.g., txt, pdf)").grid(row=3, column=2, padx=5, pady=5, sticky="w")

        # 文件大小过滤
        tk.Label(self.root, text="Min Size (MB):").grid(row=4, column=0, padx=5, pady=5, sticky="e")
        self.min_size_entry = tk.Entry(self.root, width=10)
        self.min_size_entry.grid(row=4, column=1, padx=5, pady=5, sticky="w")
        tk.Label(self.root, text="Max Size (MB):").grid(row=4, column=2, padx=5, pady=5, sticky="e")
        self.max_size_entry = tk.Entry(self.root, width=10)
        self.max_size_entry.grid(row=4, column=3, padx=5, pady=5, sticky="w")

        # 排序选项
        tk.Label(self.root, text="Sort By:").grid(row=5, column=0, padx=5, pady=5, sticky="e")
        self.sort_var = tk.StringVar(value="Name")
        tk.OptionMenu(self.root, self.sort_var, "Name", "Path", "Size").grid(row=5, column=1, padx=5, pady=5, sticky="w")

        # 搜索按钮
        tk.Button(self.root, text="Search", command=self.start_search).grid(row=6, column=1, padx=5, pady=10)

        # 进度指示
        self.progress_label = tk.Label(self.root, text="Progress: Idle")
        self.progress_label.grid(row=7, column=0, columnspan=4, padx=5, pady=5)

        # 结果显示
        self.result_text = scrolledtext.ScrolledText(self.root, width=80, height=20, wrap=tk.WORD)
        self.result_text.grid(row=8, column=0, columnspan=4, padx=5, pady=5)

        # 启动进度更新
        self.root.after(100, self.update_progress)

if __name__ == "__main__":
    root = tk.Tk()
    app = FileFinderApp(root)
    root.mainloop()
