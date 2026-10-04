"""iLovePDF visible-browser workflow. Requires Python 3.10+ and Playwright."""
from pathlib import Path
import hashlib
import json
import sys
import queue
import re
import time
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import traceback
from urllib.parse import urlsplit

BASE = Path(__file__).resolve().parent
CONFIG = BASE / 'settings.json'
POSITIONS = {f'{v}{h}': (vv, hh) for v, vv in [('上','top'),('中','middle'),('下','bottom')] for h, hh in [('左','left'),('中','center'),('右','right')]}
FONTS = {'Arial':'arial', 'Verdana':'verdana', 'Times new roman':'times-new-roman', 'Courier':'courier', 'Arial unicode ms':'arial-unicode-ms'}
COLORS = {'黑色':'#000000', '深灰':'#666666', '浅灰':'#999999', '红色':'#ff0000', '蓝色':'#0000ff'}
DEFAULTS = dict(source='', plain='', stamped='', text='François QIN', font='Arial', size='18', color='黑色', position='下右', transparency='25%', rotation='0', layer='内容上方', mosaic=False, bold=False, italic=False, all_pages=True, first='1', last='2', interval='20', preview=True, scope='全部 PDF')


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()


def pdf_ok(path):
    if not path.is_file() or path.stat().st_size < 8:
        return False
    with path.open('rb') as f:
        return f.read(5) == b'%PDF-'


def settings():
    old = DEFAULTS.copy()
    if CONFIG.exists():
        old.update(json.loads(CONFIG.read_text(encoding='utf-8')))
    root = tk.Tk()
    root.title('iLovePDF：Word → PDF → 水印 PDF')
    frame = ttk.Frame(root, padding=18)
    frame.grid(sticky='nsew')
    values = {}
    result = []
    def entry(key, label, row, choices=None, folder=False):
        ttk.Label(frame, text=label).grid(row=row, column=0, sticky='w', pady=5)
        var = tk.StringVar(value=str(old[key]))
        values[key] = var
        widget = ttk.Combobox(frame, textvariable=var, values=choices, state='readonly', width=53) if choices else ttk.Entry(frame, textvariable=var, width=56)
        widget.grid(row=row, column=1, sticky='ew')
        if folder:
            def choose():
                p = filedialog.askdirectory(parent=root, title=label)
                if p:
                    var.set(p)
            ttk.Button(frame, text='选择目录', command=choose).grid(row=row, column=2, padx=6)
    entry('source', 'Word 来源目录', 0, folder=True)
    entry('plain', '普通 PDF 保存目录', 1, folder=True)
    entry('stamped', '水印 PDF 保存目录', 2, folder=True)
    entry('text', '水印文字', 3)
    entry('font', '字体', 4, list(FONTS))
    entry('size', '字号（1—100；默认 18）', 5)
    entry('color', '文字颜色', 6, list(COLORS))
    entry('position', '位置（下右 = 右下角）', 7, list(POSITIONS))
    entry('transparency', '网站 Transparency 选项', 8, ['无透明','75%','50%','25%'])
    entry('rotation', '旋转角度', 9, ['0','45','90','180','270'])
    entry('layer', '水印图层', 10, ['内容上方','内容下方'])
    entry('first', '指定范围：起始页', 11)
    entry('last', '指定范围：结束页', 12)
    entry('scope', '第二阶段处理范围', 13, ['全部 PDF','仅本次 Word 对应的 PDF'])
    entry('interval', '每个网站任务后的间隔（秒，至少 20）', 14)
    options = ttk.Frame(frame)
    options.grid(row=15, columnspan=3, pady=12)
    for i, (key,label) in enumerate([('all_pages','每一页都加水印'),('mosaic','平铺'),('bold','加粗'),('italic','斜体'),('preview','首个 PDF 提交前检查预览')]):
        var = tk.BooleanVar(value=bool(old[key])); values[key] = var
        ttk.Checkbutton(options, text=label, variable=var).grid(row=i//3, column=i%3, sticky='w', padx=8)
    ttk.Label(frame, text='点击开始后，所选 Word/PDF 会上传到 www.ilovepdf.com。\n依次处理；验证码、登录、限额或页面变化时暂停。原文件不修改。').grid(row=16, columnspan=3, pady=10, sticky='w')
    def start():
        c = {k:v.get() for k,v in values.items()}
        try:
            paths = [Path(c[k]).expanduser().resolve() for k in ('source','plain','stamped')]
            if any(not c[k].strip() for k in ('source','plain','stamped')):
                raise ValueError('请选择三个目录。')
            if not paths[0].is_dir():
                raise ValueError('Word 来源目录不存在。')
            if len(set(paths)) != 3:
                raise ValueError('三个目录必须各不相同。')
            if not c['text'].strip():
                raise ValueError('请输入水印文字。')
            if not 1 <= int(c['size']) <= 100 or int(c['interval']) < 20:
                raise ValueError('字号须为 1—100；任务间隔至少 20 秒。')
            if not c['all_pages'] and not 1 <= int(c['first']) <= int(c['last']):
                raise ValueError('页码范围无效。')
            for k,p in zip(('source','plain','stamped'),paths):
                c[k]=str(p)
            for p in paths[1:]:
                p.mkdir(parents=True, exist_ok=True)
            CONFIG.write_text(json.dumps(c,ensure_ascii=False,indent=2),encoding='utf-8')
            result.append(c); root.destroy()
        except (ValueError,OSError) as e:
            messagebox.showerror('请检查设置',str(e),parent=root)
    ttk.Button(frame,text='开始处理',command=start).grid(row=17,columnspan=3,pady=6)
    root.mainloop()
    return result[0] if result else None


class Runner:
    def __init__(self, page, c):
        self.page = page; self.c = c
        self.plain = Path(c['plain']); self.stamped = Path(c['stamped'])
        self.statefile = self.stamped / '_workflow_progress.json'
        self.state = json.loads(self.statefile.read_text(encoding='utf-8')) if self.statefile.exists() else {}
        self.downloads = queue.Queue()
        self.logfile = self.stamped / '_workflow_log.txt'
        self.crashed = False
        self.pending_uploads = set()
        self.upload_error = None
        self.last_upload_activity = time.monotonic()
        self.watch_page(page)
        page.context.on('page', self.watch_page)
        self.preview_done = False
    def watch_page(self, page):
        page.on('download', self.downloads.put)
        page.on('crash', lambda _: self.browser_crash())
        page.on('request', self.upload_started)
        page.on('requestfinished', self.upload_finished)
        page.on('requestfailed', self.upload_failed)
    def upload_started(self, request):
        host = (urlsplit(request.url).hostname or '').lower()
        if (host == 'ilovepdf.com' or host.endswith('.ilovepdf.com')) and '/upload' in urlsplit(request.url).path.lower() and request.method in ('POST', 'PUT'):
            self.pending_uploads.add(request)
            self.last_upload_activity = time.monotonic()
    def upload_finished(self, request):
        if request in self.pending_uploads:
            self.pending_uploads.discard(request)
            self.last_upload_activity = time.monotonic()
            response = request.response()
            if response and response.status >= 400:
                self.upload_error = '上传服务器返回 HTTP '+str(response.status)
    def upload_failed(self, request):
        if request in self.pending_uploads:
            self.pending_uploads.discard(request)
            self.last_upload_activity = time.monotonic()
            self.upload_error = '上传请求失败：'+str(request.failure)
    def wait_upload_ready(self):
        start = time.monotonic()
        self.log('等待上传和文件载入完成……')
        while time.monotonic()-start < 60:
            self.page.wait_for_timeout(250)
            self.ensure_browser()
            if self.upload_error:
                raise RuntimeError(self.upload_error+'。请停止后重新运行并上传。')
            if self.pending_uploads or time.monotonic()-start < 8 or time.monotonic()-self.last_upload_activity < 3:
                continue
            button = self.page.locator('#processTask')
            if not button.is_visible() or not button.is_enabled():
                continue
            if self.is_watermark:
                end = self.page.locator('input[name=page_end]').input_value()
                if not end.isdigit() or int(end) < 1:
                    continue
            self.log('文件载入检查通过。')
            return
        raise RuntimeError('文件尚未完成上传或载入。请检查网页后继续等待，或输入 q 停止。')
    def browser_crash(self):
        self.crashed = True
        self.log('浏览器页面发生崩溃。')
    def ensure_browser(self):
        if self.crashed or self.page.is_closed():
            raise RuntimeError('处理页面已关闭或崩溃。请重新启动；已完成的文件会跳过。')
        try:
            self.page.evaluate('1')
        except Exception as e:
            raise RuntimeError('浏览器连接已中断。请重新启动；已完成的文件会跳过。') from e
    def submit(self):
        # Pump pending preview events before accepting result downloads.
        self.page.wait_for_timeout(200)
        while not self.downloads.empty(): self.downloads.get_nowait()
        self.page.locator('#processTask').click(timeout=60000)
    def log(self, text):
        line = time.strftime('%Y-%m-%d %H:%M:%S ') + text
        print(line, flush=True)
        with self.logfile.open('a',encoding='utf-8') as f: f.write(line+'\n')
    def save_state(self):
        p = self.statefile.with_suffix('.tmp')
        p.write_text(json.dumps(self.state,ensure_ascii=False,indent=2),encoding='utf-8')
        p.replace(self.statefile)
    def pause(self, reason):
        self.log(reason)
        reply = input('在浏览器处理提示后按回车继续；输入 q 停止：').strip().lower()
        if reply == 'q': raise KeyboardInterrupt
    def perform(self, description, action):
        # No automatic retry loop: a human explicitly chooses whether to continue.
        while True:
            try:
                return action()
            except Exception as e:
                self.log(f'{description} 暂停：{e}')
                try: self.page.screenshot(path=str(self.stamped/'_workflow_error.png'))
                except Exception: pass
                self.pause('请检查浏览器是否有登录、验证码、限额或控件变化。程序不会绕过这些提示。')
    def upload(self, file, url):
        while not self.downloads.empty(): self.downloads.get_nowait()
        self.page.goto(url,wait_until='domcontentloaded',timeout=60000)
        self.pending_uploads.clear()
        self.upload_error = None
        self.last_upload_activity = time.monotonic()
        self.is_watermark = '/pdf_add_watermark' in url
        self.perform('上传',lambda:self.page.locator('input[type=file]').first.set_input_files(str(file),timeout=60000))
        self.perform('等待文件载入',self.wait_upload_ready)
    def download(self, target):
        clicked = False
        while True:
            until = time.monotonic()+60
            while time.monotonic()<until:
                if '/problem/' in self.page.url:
                    self.pause('网站报告处理失败，尚未生成结果。请输入 q 停止并检查；仅按回车不会重新上传文件。')
                    continue
                if not self.downloads.empty():
                    d = self.downloads.get_nowait()
                    temp = target.with_suffix('.pdf.part')
                    try:
                        self.log('收到下载：'+d.suggested_filename)
                        failure = d.failure()
                        if failure:
                            raise RuntimeError('浏览器报告下载失败：'+failure)
                        d.save_as(str(temp))
                        if not pdf_ok(temp):
                            raise RuntimeError('下载结果不是 PDF（可能是错误页或 ZIP）。')
                        if target.exists():
                            raise FileExistsError(f'目标已存在，未覆盖：{target}')
                        temp.replace(target)
                    except FileExistsError:
                        raise
                    except Exception as e:
                        # A canceled download can lose its artifact while the
                        # processing page is still alive. Verify separately.
                        self.ensure_browser()
                        self.log('本次下载未保存：'+str(e))
                        try: self.page.screenshot(path=str(self.stamped/'_workflow_error.png'))
                        except Exception: pass
                        self.pause('浏览器仍可连接。请在网页找到 Download PDF 并点击；如果网页尚在处理，请等待。然后按回车继续接收下载。')
                        clicked = False
                        continue
                    finally:
                        if temp.exists(): temp.unlink()
                    return
                # The site may download automatically or present a download link.
                if not clicked:
                    link = self.page.get_by_role('link',name=re.compile(r'Download.*PDF', re.I))
                    if link.count() and link.first.is_visible():
                        link.first.click(); clicked=True
                self.page.wait_for_timeout(500)
            self.pause('60 秒内尚未取得 PDF。若页面显示下载按钮，可以手动点击；任务限额请稍后再运行。')
    def convert(self, source):
        target = self.plain/(source.stem+'.pdf')
        key = 'word:'+str(source)
        fingerprint = digest(source)
        prior = self.state.get(key,{})
        if target.exists():
            if prior.get('input') == fingerprint and prior.get('output') == str(target) and pdf_ok(target) and prior.get('hash') == digest(target):
                self.log('跳过已完成转换：'+source.name); return target
            raise FileExistsError(f'普通 PDF 已存在但无法确认与此 Word 相符：{target}。请选择新的输出目录，或先将该 PDF 移走。')
        self.log('Word → PDF：'+source.name)
        self.upload(source,'https://www.ilovepdf.com/word_to_pdf')
        self.perform('提交转换',self.submit)
        self.download(target)
        self.state[key] = dict(input=fingerprint,output=str(target),hash=digest(target))
        self.save_state(); self.log('已保存：'+str(target))
        time.sleep(int(self.c['interval']))
        return target
    def toolbar(self, field):
        box=self.page.locator('.editor__toolbar__option').filter(has=self.page.locator(field))
        box.locator('.editor__option__selector').click()
    def watermark_options(self):
        p=self.page; c=self.c
        p.locator('input[name=text]').fill(c['text'])
        p.locator('.font-selected').click()
        p.locator(f'.font-selector[data-value="{FONTS[c["font"]]}"]').click()
        self.toolbar('#textFormatOptionsFontSizeText')
        p.locator('#textFormatOptionsFontSizeText').fill(c['size'])
        p.locator('#textFormatOptionsFontSizeText').press('Tab')
        # Close the floating toolbar through a visible heading outside it.
        # The text input can be covered by the font-size/color popup.
        p.get_by_text('Position:', exact=True).click()
        p.locator('.toolbar-color > .editor__option__selector').click()
        p.locator('.toolbar-color .col').first.locator(f'[title="{COLORS[c["color"]]}"]').first.click()
        # Close the floating toolbar through a visible heading outside it.
        # The text input can be covered by the font-size/color popup.
        p.get_by_text('Position:', exact=True).click()
        for name in ('bold','italic'):
            e=p.locator('.editor__option.'+name)
            active='active' in (e.get_attribute('class') or '')
            if active != c[name]: e.click()
        vertical,horizontal=POSITIONS[c['position']]
        p.locator(f'.option__page__position[data-vertical="{vertical}"][data-horizontal="{horizontal}"]').click()
        p.locator('#mosaic').set_checked(c['mosaic'])
        p.locator('#transparency').select_option('100' if c['transparency']=='无透明' else c['transparency'].rstrip('%'))
        p.locator('select[name=rotation]').select_option(c['rotation'])
        p.locator(f'[data-name=layer][data-value={"above" if c["layer"]=="内容上方" else "below"}]').click()
        if c['all_pages']:
            # Each newly uploaded document initializes the end field to its page count.
            p.locator('input[name=page_init]').fill('1')
            end=p.locator('input[name=page_end]').input_value()
            if not end or int(end)<1:
                raise RuntimeError('页面总数尚未载入；请等 PDF 预览出现后继续。')
        else:
            end=p.locator('input[name=page_end]').input_value()
            if end and int(c['last'])>int(end):
                raise RuntimeError('指定的结束页超过当前 PDF 页数。请停止并修改页码设置。')
            p.locator('input[name=page_init]').fill(c['first'])
            p.locator('input[name=page_end]').fill(c['last'])
        p.locator('input[name=page_init]').press('Tab')
    def watermark(self, source):
        target=self.stamped/source.name
        watermark={k:self.c[k] for k in ('text','font','size','color','position','transparency','rotation','layer','mosaic','bold','italic','all_pages','first','last')}
        key='pdf:'+str(source)
        fingerprint=digest(source); prior=self.state.get(key,{})
        if target.exists():
            if prior.get('input')==fingerprint and prior.get('settings')==watermark and prior.get('output')==str(target) and pdf_ok(target) and prior.get('hash')==digest(target):
                self.log('跳过已完成水印：'+source.name); return
            raise FileExistsError(f'水印目标已存在，未覆盖：{target}。更改水印后请使用新的水印输出目录。')
        self.log('添加水印：'+source.name)
        self.upload(source,'https://www.ilovepdf.com/pdf_add_watermark')
        self.perform('设置水印',self.watermark_options)
        if self.c['preview'] and not self.preview_done:
            self.pause('首个 PDF 的水印参数已设置。请检查浏览器中的位置、文字和样式。满意后按回车；需要修改设置则输入 q 后重新启动。')
            self.preview_done=True
        self.perform('提交水印',self.submit)
        self.download(target)
        self.state[key]=dict(input=fingerprint,settings=watermark,output=str(target),hash=digest(target))
        self.save_state(); self.log('已保存：'+str(target))
        time.sleep(int(self.c['interval']))
    def run(self):
        words=sorted((p for p in Path(self.c['source']).iterdir() if p.is_file() and p.suffix.lower() in ('.doc','.docx') and not p.name.startswith('~$')),key=lambda p:p.name.casefold())
        names=[p.stem.casefold() for p in words]
        if len(names)!=len(set(names)):
            raise ValueError('有 Word 文件具有相同基本文件名（例如同名 .doc 与 .docx），请先重命名。')
        self.log(f'第一阶段：{len(words)} 个 Word。只扫描目录第一层。')
        for source in words: self.convert(source)
        pdfs=sorted((p for p in self.plain.iterdir() if p.is_file() and p.suffix.lower()=='.pdf'),key=lambda p:p.name.casefold())
        if self.c['scope']!='全部 PDF': pdfs=[self.plain/(p.stem+'.pdf') for p in words]
        self.log(f'第二阶段：{len(pdfs)} 个 PDF。')
        for source in pdfs:
            if not pdf_ok(source): raise ValueError('无效 PDF：'+str(source))
            self.watermark(source)
        self.log(f'全部完成。普通 PDF：{self.plain}；水印 PDF：{self.stamped}')


def launch_browser(pw):
    if sys.platform != 'win32':
        return pw.chromium.launch(headless=False), 'Chromium'
    # Use installed Stable browsers, and never reuse the crashed profile.
    for channel, label in (('chrome', 'Google Chrome'), ('msedge', 'Microsoft Edge')):
        try:
            return pw.chromium.launch(channel=channel, headless=False), label
        except Exception as e:
            if 'executable' not in str(e).lower() or 'exist' not in str(e).lower():
                raise
    raise RuntimeError('没有找到 Chrome 或 Edge。请安装其中一个浏览器后重新运行。')


def main():
    c=settings()
    if c is None: return
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        browser, label = launch_browser(pw)
        context=browser.new_context(accept_downloads=True,locale='en-US',viewport={'width':1280,'height':900})
        page=context.new_page(); page.set_default_timeout(30000)
        runner=Runner(page,c)
        runner.log('浏览器：'+label+' '+browser.version+'；本次使用全新运行环境。')
        browser.on('disconnected', lambda _: runner.log('浏览器连接已断开。'))
        try:
            page.goto('https://www.ilovepdf.com/word_to_pdf',wait_until='domcontentloaded',timeout=60000)
            runner.pause('浏览器已打开。如需登录请在浏览器完成；关闭 Cookie 提示。准备好后按回车开始批处理。')
            runner.run()
        except KeyboardInterrupt:
            runner.log('已停止。完成的文件和进度已保留，下次可继续。')
        except Exception as e:
            runner.log('处理停止：'+str(e))
            traceback.print_exc()
        finally:
            input('按回车关闭浏览器和程序：')
            if browser.is_connected():
                context.close()
                browser.close()

if __name__=='__main__':
    try: main()
    except Exception:
        traceback.print_exc(); input('启动失败，按回车退出：')
