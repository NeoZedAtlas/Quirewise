# 格式能力总览（三态口径）

> 状态：2026-11-15 按当前代码重新核对。旧版本把"库里有解析器"与"CLI 能转换"混为一谈，
> 本页改用三态描述：
>
> - **CLI 可达**：`quirewise` 可执行文件能完成的转换；
> - **仅库 API**：库包公开了接口，但统一转换入口/CLI 没有路由；
> - **不支持**：没有实现，入口稳定返回 `UNSUPPORTED`。
>
> 三者都以当前 HEAD 的代码为准；历史文档中依赖 Ghostscript、veraPDF、FFmpeg、LibRaw、
> MuPDF 等外部后端的路线不在发布包内。
> 外部依赖与暂不支持项的逐条结论见 [unsupported-rationale.md](unsupported-rationale.md)。
> HTML→Markdown（含 `<hr>`→`---`、`<dl>/<dt>/<dd>`→`term`/`: detail`） 保留表格列对齐（`align` 或 `style=text-align` → `:---:`/`---:`/`:---`）；Markdown 管道表格（含对齐分隔行与转义 `\|`）→ HTML `<table>`，Setext 标题（`===`/`---`）→ h1/h2，围栏代码 info string → `language-*` 类，任务列表 `- [x]` → 禁用复选框，尖括号自动链接 `<https://…>` → `<a>`、行内链接 `"title"` → `title` 属性，删除线 `~~text~~` → `<del>`。

## 1. 输入类别总览

| 输入类别 | 代表格式 | CLI 可达 | 仅库 API | 不支持 |
|---|---|---|---|---|
| PDF | PDF 1.x–1.7 | PDF→PDF（透传；多文档合并并把各输入书签汇总、校正页码/层级）、PDF→TXT（无 OCR）、PDF→PNG/JPEG/BMP/TIFF/WebP（首页 144 dpi 栅格化）、PDF→HTML/Markdown（文本层）、PDF→DOCX/EPUB（每页 120 dpi 页面图，保留版式）；加密 PDF 支持用户口令（`--pdf-password`） | 逐页栅格化、文本抽取、多文档合并、h1–h6 自动生成嵌套书签大纲（非 ASCII 用 UTF-16BE）、`/Info` 标题/作者读取与写入（非 ASCII 用 UTF-16BE）、书签大纲读取（`qw_pdf_document_title`/`qw_pdf_document_author`/`qw_pdf_bookmark_count`/`qw_pdf_bookmark_at`，加密 PDF 为空） | PDF/A（需外部 veraPDF）、OCR、可编辑的版式/表格重建（页面为图片） |
| Office 文本 | DOCX/DOCM/DOTX/DOTM、ODT/OTT/FODT | →PDF（DOCX/ODT 的 data URI 图片与 FODT 的 office:binary-data 图片会嵌入并绘制）、→HTML、→Markdown、→DOCX、→EPUB；DOCX 标题样式与 ODT text:h(outline-level) 映射为 h1–h6 并在 PDF 中生成嵌套书签；DOCX 页眉/页脚文本按 `docx-header`/`docx-footer` 段落插入；表格 `gridSpan`/`vMerge` 映射为 `colspan`/`rowspan`；ODT 主页面页眉/页脚文本按 `odt-header`/`odt-footer` 插入 | 版式模型（`qw_docx_parse`、`qw_odt_parse`） | 旧版 .doc、宏语义、页眉页脚版式/页码字段、浮动环绕、EMF/WMF |
| 演示文稿 | PPTX/PPTM/POTX/POTM/PPSX/PPSM、ODP/OTP/FODP | →PDF（文字 + PPTX 内嵌图片）、→HTML、→Markdown、→DOCX、→EPUB | 幻灯片文字/版式 HTML；PPTX/ODP 图片解析为 data URI（ODP 含 FODP office:binary-data 内嵌图）；PPTX 每页幻灯片生成 PDF 书签（Slide N），ODP 同时带幻灯片名称；PPTX 备注页与 ODP 备注页文本以 notes 段落追加 | 形状位置、图表、动画、母版；PPTX `a:srcRect` 与 ODP `fo:clip` 图片裁剪会应用，其他图片效果不还原；ODP 图片按 svg:width 缩放 |
| HWPX | HWPX | →PDF（段落/简单表格 + BinData 图片）、→HTML、→Markdown、→DOCX、→EPUB、→HWPX（最小 OWPML 包） | 版式 HTML；`hp:pic`→`hp:img` 引用按 content.hpf 映射为 PNG data URI | 旧版 HWP、样式、加密部件；图片按 hp:sz 显示尺寸绘制、hp:imgclip 裁剪应用到像素，hp:rotationInfo 90° 倍数旋转、表格 cellSpan 映射 colspan/rowspan、borderFill 背景色与边框、单元格垂直对齐/竖排/内边距、flip 水平/垂直镜像、段落对齐 `text-align`、图片位置转为 CSS 外边距、`charPr` 粗体/斜体/下划线/删除线/上标/下标/字距/字符缩放/文字色/背景色、`paraPr` 对齐/缩进/段距/行距/分页前、标题映射 h1–h6 |
| 邮件 | EML、MSG | →PDF（正文 + 内嵌图片附件）、→HTML、→Markdown、→DOCX、→EPUB | MIME 解析；文本附件内联为 `attachment-text`，图片附件按 PNG data URI 嵌入并绘制；MSG 优先 HTML 正文，其次 Unicode 文本正文，最后解码 LZFu 压缩 RTF 正文（表格与 PNG/JPEG 图片渲染为 HTML） | 签名语义；MSG 的其它二进制附件仍只列元数据 |
| XPS | XPS/OpenXPS | →PDF、→HTML、→Markdown（页面文本与 PNG 图片 data URI） | 页面 XML 读取 | 矢量路径与精确版面定位不还原 |
| 电子书 | EPUB/KEPUB、MOBI/AZW3/AZW、FB2、PMLZ、TXTZ、HTMLZ | →PDF、→HTML、→Markdown、→DOCX、→EPUB、→HTMLZ（包内图片按相对路径内联为 data URI）、→TXTZ、→PMLZ | 段落/章节模型 | DRM、HUFF/CDIC 压缩的 MOBI、CHM/LIT/LRF/PDB/RB/SNB/TCR；EPUB 表格按行输出为 `<table>`（连续行合并到一个表，`<th>` 表头、`<caption>` 与 `colspan`/`rowspan` 保留、`figure/figcaption` 保留、`<hr>` 保留、脚注引用保留为片段链接且脚注内容保留为段落（不生成回链锚点））、列表为 `<ul><li>`/`<ol><li>`（嵌套列表按层级缩进）、引用块为 `<blockquote>`、定义列表为 `<dl>/<dt>/<dd>`、`<pre>` 保留换行、图片内嵌为 data URI；SVG/canvas/媒体等仍整章跳过（全部跳过时返回 `unsupported`） |
| 词典 | MDict MDX（词条）+ MDD（资源包），引擎 1.2–2.0（LZO/zlib） | MDX→PDF（词条版式）、MDX→TXT（键 + 去标签释义）、MDX→HTML/Markdown/DOCX/EPUB、MDD `--check` 结构校验；`--mdd` 将词条 `<img>` 按名解析到 MDD 资源并内嵌为 data URI（PDF/HTML） | 词条/资源枚举、MDD 资源按名查找、HTML/纯文本整册渲染 | 注册码加密词典（`Encrypted="1"`/`"3"`）、StarDict/DSL/KDIC 等其它词典格式 |
| 轻量标记 | TXT、Markdown、HTML、RTF、AsciiDoc、LaTeX、Org、RST、Textile、Typst、MediaWiki、Man | →PDF（HTML 中的 data URI 图片会绘制）、TXT/Markdown/HTML 互转、→DOCX（data URI 图片写入 `word/media`、http/https/mailto 链接写入关系）、→EPUB（图片写入 `OEBPS/images`）、→HTMLZ、→TXTZ、→PMLZ、→HWPX | 读取后转 HTML/Markdown；轻量标记输入先由 text 解析器转为 Markdown（Man 转 HTML）再走统一管线，`--check` 同样可用 | DocBook 的统一转换入口、上述标记语言的完整语法保真 |
| 工作簿 | XLSX/XLSM/XLTX、BIFF8 XLS/XLT、ODS/OTS/FODS、CSV/TSV | →PDF（按工作表渲染表格）、表格→CSV/TSV（可用 `--sheet N` 选择工作表）、表格→XLSX/ODS（全部工作表、单元格值、合并区间）、表格→HTML | 单元格/公式缓存读取；XLSX `mergeCells`、ODS 跨度属性与 BIFF8 `MERGEDCELLS` 映射为 `colspan`/`rowspan` | 公式重算、图表/图片/合并区域样式；BIFF8 的 SST 跨 `CONTINUE` 记录字符串已支持（含编码切换与富文本偏移） |
| 结构化数据 | JSON、JSONL、YAML（核心 `!!str/!!int/!!bool/!!float/!!null` 标签）、TOML、XML、OPML、IPYNB、vCard | →PDF（值树渲染为表格/列表）、JSON/JSONL/YAML/TOML/vCard/XML 互转；Markdown/TXT→IPYNB（单 markdown cell）、→OPML（标题层级 outline） | 类型化值树、XML 序列化 | YAML 自定义 tag、外部 DTD 校验（内部实体已展开） |
| 字幕 | SRT、WebVTT、LRC、MicroDVD、TTML、ASS/SSA、SAMI、SCC | →PDF（时间轴文本页）、SRT/WebVTT/LRC/MicroDVD/TTML/ASS/SSA/SAMI/SCC 互转 | cue 模型；TTML 写出（begin/end + 文本，XML 转义、`<br/>` 换行） | 样式/定位/特效保留、字幕封装；ASS/SSA 的 `Name` 说话人与层/边距/Effect 写入 cue identifier/settings，ASS/SSA 写出时保留 |
| 单页图像 | JPEG、PNG、BMP、GIF、TIFF、WebP、JP2/J2K、QOI、Netpbm、PSD/PSB、EXR、HDR、TGA、PCX/ICO/ICNS、DDS、XPM/XBM、SGI、RAS、MIFF、DCM 等 | →PDF（单页）、图像重编码 →PNG/BMP/TIFF/JPEG/WebP/TGA/QOI/PPM/GIF/HDR/SGI/PCX（任意可解码输入） | 解码、动画/多页展开 | AVIF/HEIC/JXL/PCD 解码、RAW 去马赛克 |
| 相机 RAW | DNG/TIFF-CFA、CR3、RAF、X3F、CRW、MRW | — | 文件签名/结构探测 | **像素解码恒返回 `UNSUPPORTED`**（发布包不含 LibRaw 或自研去马赛克） |
| 矢量 | SVG/SVGZ | →PDF（自研子集；`<text>` 等未支持特性返回 `unsupported`） | 子集解析 + RGBA 栅格化 | EPS/PS/AI |
| CAD | DXF（ASCII/binary）、DWG R13–R2018 | →PDF（A4 栅格）、→TXT（文本清单） | 文档模型、RGBA/SVG 渲染（SVG 文本可读） | DWG 图层句柄/块/ATTRIB、MTEXT/HATCH/ACIS/3D/代理对象、精确 NURBS、CJK 字形 |
| 漫画归档 | CBZ、CBT、CB7、CBR（stored 条目） | →PDF（图像页；坏页告警，`--check` 失败） | 归档页序/页字节 | 压缩 RAR 条目、其它归档 |
| 图像目录 | 目录 | — | 非递归枚举（`quirewise-image` 的 image_folder） | CLI 目录输入 |
| 标准音频 | WAV/RIFX/RF64/BW64/Wave64、AIFF/AIFC、CAF、AU、DSF/DFF/DSS、VOC、FLAC、MP1/2/3、AAC、AMR、AC-3/E-AC-3、DTS、TTA、TAK、WavPack、APE、Musepack、WMA/ASF、M4A/MP4、Matroska/WebM、Ogg/Opus | `--check` 容器/包解析 | 包读取、加密音乐解密（NCM/QMC/KGM/KWM） | 解码到 PCM、重采样、编码/封装、播放 |
| 视频、字体、3D | MP4 视频、TTF/OTF 等、STL/GLTF | — | — | 没有对应库 |

## 2. 统一边界

1. 格式支持按"输入格式 × 输出格式 × 路线"定义；能解析不等于能写出，扩展名识别也不等于完整兼容。
2. 版式转换只保留已映射的文字、段落、列表、表格和部分图片；源格式的样式、布局、附件、公式和元数据可能丢失。
3. 栅格化会丢失矢量结构、文本选择能力和源元数据；PDF→TXT 只抽取可读文本，不执行 OCR。
4. 公式按文件内缓存结果读取，不重新计算。
5. 页面/图像/归档/结构化数据都有尺寸、页数、节点数和展开大小上限；超限返回 `RESOURCE_LIMIT` 或 `UNSUPPORTED`，不静默降级。
6. 需要后端的路线（PDF/A、RAW 去马赛克、视频）在发布包内一律返回 `UNSUPPORTED`。

## 3. 命令行注记（2026-11-15）

- `quirewise INPUT [--to pdf|txt|png|json|jsonl|yaml|toml|xml|vcf|srt|vtt|lrc|sub|ass|ssa|sami|scc|csv|tsv|html|md|docx|epub|bmp|tiff|jpg|webp|gif|hdr|sgi|pcx|tga|qoi|ppm|htmlz|txtz|pmlz|opml|ipynb|hwpx]` 覆盖上表"CLI 可达"列；`-o` 的扩展名必须与 `--to` 一致（否则退出码 2）。
- 非 PDF 输出分四类：PDF→TXT/PNG/JPEG/BMP/TIFF/WebP（首页栅格化）、PDF→HTML/Markdown（文本层）、PDF→DOCX/EPUB（每页 120 dpi 页面图，保留视觉版式，最多 24 页，文本不可编辑）、CAD→TXT、MDX→TXT（源格式专用路线）；数据/字幕/表格家族的互转（JSON↔YAML 等、SRT↔VTT 等、表格→CSV/TSV、表格→XLSX/ODS）；布局类输入→HTML/Markdown/DOCX/EPUB/HTMLZ/TXTZ/PMLZ/HWPX（HTML 是公开的版式中间表示）；图像→PNG/BMP/TIFF/JPEG/WebP/TGA/QOI/PPM/GIF/HDR/SGI/PCX（解码后重编码，不做缩放；GIF 输出为单帧，RGB 走 3:3:2 调色板）。DOCX 为最小 WordprocessingML 包（段落/标题/强调/列表文本、超链接关系、Word 表格（colspan→gridSpan、rowspan→vMerge）；PDF 源改为每页图片 + inline drawing），EPUB 为最小 EPUB 2 包（单章 XHTML + OPF + NCX；PDF 源为页面图片章 + 提取文本章）。字幕输入没有版式路线，返回 `unsupported`。
- `--page image|a4` 作用于 DjVu/PDZ/UVZ/CBZ/CBT 和直接图片输入的页面框（默认 image = 像素尺寸）；CAD 输出固定 A4。
- `--pages auto|body|body+att|all` 只作用于 PDG/PDZ 容器；`--archive-password` 传给 CBZ/CBT 与库的 ZIP 路线；`--audio-track` 只用于音频 `--check`；`--sheet N` 为一基工作表序号，作用于 CSV/TSV 输出。
- TTML（`.ttml`/`.dfxp`）由 subtitle 路由解析；document 层不再把 TTML 误报为 FODT。
- EPUB 的 `class`/`style`/样式表链接按样式忽略，表格/列表/图片等结构章节整章跳过；若所有章节都不可读，返回 `unsupported`。
- 徽标/密钥/扫描预处理/PDF-A/目录批量仍未接线；`--pdfa` 等未识别选项返回退出码 2。
