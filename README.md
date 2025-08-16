# filefinder
The File Finder App is a Python-based desktop application built with Tkinter. It allows you to search files on your computer with advanced filtering options.
Key features include:

Search by filename pattern (supports partial/fuzzy matching).

Choose a search path or scan all drives.

Filter by file extension (e.g., .txt, .pdf).

Filter by minimum and maximum file size (in MB).

Sort results by name, path, or size.

View real-time search progress.

Uses a cache system to speed up repeated searches.

⚙️ How It Works

The app scans files under the selected directory or across all drives.

It compares each file against the search conditions:

Filename pattern (case-insensitive, fuzzy match).

Extension filter.

Size filter (min/max in MB).

Matching files are collected, sorted, and displayed in the results box.

Results include:

Full path of each file.

File size (MB).

A simple progress tracker shows when the search is active or finished.

🖥️ How to Use

Run the program

python filefinder.py


Enter search parameters in the GUI:

Filename Pattern → Enter part of the filename (e.g., report will match report.docx).

Search Path → Choose a folder path manually or use "Browse".

Or Select Drive → Choose from available drives (C:\, /home, /media/..., etc.).

File Extension → (Optional) Limit results (e.g., txt, pdf).

Min/Max Size (MB) → (Optional) Only include files within size range.

Sort By → Choose sorting method (Name, Path, or Size).

Click “Search”

Progress updates appear below the button.

Results are shown in a scrollable text box.

📝 Example Usage

Find all PDFs larger than 5 MB in /home:

Filename Pattern: "" (leave empty to match all).

Search Path: /home.

File Extension: pdf.

Min Size: 5.

Find files containing "report" in all drives:

Filename Pattern: report.

Select Drive: All Drives.
