# Xbox OG ISO Extractor & Unpacker to XISO-FOLDER Format

This script automates the process of extracting compressed files (`.zip`, `.rar`, `.7z`, etc.) that contain Xbox Original (OG) game ISOs, and then unpacks those ISOs using the `xdvdfs.exe` tool.

## 🧰 Requirements

- Python 3.6 or higher
- 7-Zip installed and available in the system PATH (`7z` command)
- `xdvdfs.exe` placed in the same directory as this script
- Python packages:
  - `colorama`
  - `termcolor`

Missing Python packages will be automatically installed when the script runs.

## 📁 Folder Structure

```
📂 isos/
  ├─ Game1.zip
  ├─ Game2.7z
```

- Place all compressed files inside the `isos/` folder.
- Extracted and unpacked content will be saved in the `xiso-unpacked/` folder.

## ▶️ How to Use

1. Put your compressed ISO game files in the `isos/` directory.
2. Run the script with:

```bash
python runme.py
```

3. Progress will be shown in the terminal and logged to `process.log`.

## 🧹 Cleanup

- Extracted `.iso` and original compressed files are deleted after processing.
- Any empty subfolders are also removed automatically.

## 📝 Logging

All actions and errors are logged in the `process.log` file.
