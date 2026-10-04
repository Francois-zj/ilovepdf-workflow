# iLovePDF Word → PDF → Watermarked PDF

[中文](README.zh-CN.md) | **English** | [Français](README.fr.md)

A Windows desktop workflow that uses the visible **www.ilovepdf.com** website to convert Word documents into PDFs, then add a text watermark. It uses Python, tkinter and Playwright. It does not use Microsoft Word's conversion feature or the iLovePDF developer API. This is an independent project, not an official iLovePDF tool.

## Features

- Choose separate folders for Word sources, ordinary PDFs and watermarked PDFs.
- Convert `.doc` and `.docx` files in the source folder, then watermark PDFs sequentially.
- Set watermark text, font, size, colour, position, transparency, rotation, layer and page range.
- Optionally check the first document's watermark settings before submitting it.
- Resume verified completed tasks using a progress file; refuse to overwrite unverified existing outputs.
- Keep the source documents unchanged. Output names match the original base names.

## Requirements

Windows, Python **3.10 or newer** with tkinter, installed **Google Chrome or Microsoft Edge**, and an internet connection. Chrome is tried first; Edge is used if Chrome is not installed. The interface and console messages are currently in Chinese; this documentation explains their meaning. Other operating systems have not been validated.

## Installation and use

1. Download this repository with **Code → Download ZIP**, then extract it.
2. Open Command Prompt and run `python --version`. If unavailable, try `py -3 --version`. Install Python 3.10+ if neither works; select **Add Python to PATH**.
3. Double-click `setup.bat`. It creates `.venv` and installs the dependencies. Wait for **Installation complete**. Run setup only on initial installation or when dependencies change.
4. Double-click `start.bat`.
5. Select three different folders. The source folder must exist; output folders are created if needed. Example: `F:\WordInput`, `F:\PDF`, `F:\PDF_Watermarked`.
6. Enter your watermark text and select its appearance. The default text is `François QIN`; change it for your own documents.
7. Keep **每一页都加水印** selected to watermark every page of each PDF, regardless of its length. The start/end fields are ignored in this mode.
8. Choose the second-stage scope, then click **开始处理**.
9. In the browser, close the cookie notice and complete any required sign-in. Return to Command Prompt and press Enter when ready.
10. All Word conversions run first. If first-document preview is enabled, the workflow pauses after configuring the first PDF. Check the website's watermark settings, then press Enter in the console. Enter `q` to stop if you need to change settings and restart. This checkpoint checks the website settings; it is not a verification of the finished PDF.
11. Remaining files use the same settings automatically. Keep the browser and console open. If prompted for a website issue, handle it in the browser, then follow the console instructions.
12. When the console reports completion, open your output folders and inspect the PDFs. Press Enter at the final prompt to close the program.

## Interface reference

| Chinese label | Meaning |
| --- | --- |
| Word 来源目录 | Source Word folder |
| 普通 PDF 保存目录 | Ordinary PDF output folder |
| 水印 PDF 保存目录 | Watermarked PDF output folder |
| 水印文字 / 字体 / 字号 / 文字颜色 | Text / font / size / colour |
| 位置：下右 | Bottom right position |
| 水印图层：内容上方 / 内容下方 | Above / below PDF content |
| 指定范围：起始页 / 结束页 | First / last page, inclusive |
| 第二阶段处理范围：全部 PDF | Watermark every PDF in the ordinary output folder |
| 仅本次 Word 对应的 PDF | Watermark only PDFs corresponding to Word sources in this run |
| 每个网站任务后的间隔 | Delay after each successful task, at least 20 seconds |
| 每一页都加水印 | Watermark all pages |
| 平铺 / 加粗 / 斜体 | Mosaic / bold / italic |
| 首个 PDF 提交前检查预览 | Check first PDF settings before submission |
| 开始处理 | Start processing |

Transparency values follow the website's **Transparency** choices. With all-pages disabled, the same numeric range applies to every file. A range exceeding a document's page count pauses the workflow; individual ranges per file are not supported. To modify options, stop and restart rather than editing settings in the browser alone.

## Resume and troubleshooting

Keep `_workflow_progress.json` in the watermarked output folder. Restart with the same folders and settings to skip outputs whose source and output hashes still match. If you move folders, change a source, or change watermark settings, an existing output may no longer be recognised. Use a new relevant output folder or move the conflicting output aside. The program never silently replaces it.

`_workflow_log.txt` records progress. `_workflow_error.png` may capture the page on a recoverable error. A download failure with a live browser prompts you to click **Download PDF** and continue. If the browser disconnects, restart after checking the error. If setup fails, read its error output; if `py` refers to a deleted installation, ensure a working `python` command is available. The bundled setup tries `python` first.

Only the first folder level is scanned; subfolders and Word temporary files beginning with `~$` are excluded. Same-stem `.doc` and `.docx` sources must be renamed before processing.

Files are uploaded to iLovePDF for processing. Login requirements, task limits, CAPTCHA and website changes can require intervention; the program does not bypass them. Website processing depends on the service and the network. A Windows batch of 11 documents completed successfully in the author's local test; universal compatibility is not guaranteed.

## Repository files

`workflow.py` — application; `requirements.txt` — dependencies; `setup.bat` — initial setup; `start.bat` — launcher; the three README files — instructions; `.gitignore` — local-file exclusions.

When publishing the source, upload only these files. Keep personal Word/PDF files, `.venv`, browser profiles, `settings.json`, progress files, logs and error screenshots out of the repository. `.gitignore` protects Git-based additions; it does not filter files you manually upload through the website.
