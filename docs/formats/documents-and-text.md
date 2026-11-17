# 文档、电子书与文本

> 状态（2026-11-17）：DOCX/ODT、EPUB、FB2、PPTX/ODP、HWPX、EML/MSG、MOBI/AZW3、
> MDict MDX/MDD、HTMLZ/TXTZ/PMLZ、RTF、TXT/Markdown/HTML 均已接入统一转换入口。
> 本页描述**当前代码**能读写的子集；逐项三态结论以
> [格式能力总览](support-matrix.md) 为准。

本文说明版式类文件当前可转换的内容范围。输出保留可识别的文字与结构，不重建原文件的
完整视觉效果、全部元数据或域语义。

## 文档与电子书

| 输入格式 | 当前可读取/输出内容 | 主要限制 |
|---|---|---|
| DOCX、DOCM、DOTX、DOTM | 正文、字符/段落样式、标题、对齐、缩进（`w:ind`）、分节纸张与边距、分页符、表格（`gridSpan`/`vMerge`、部分底色）、JPEG/PNG/GIF/BMP/TIFF/SVG 图片、安全外链、书签、常见编号列表、脚注/尾注（引用标记 + 文末列表）、页眉/页脚文本（粗体/斜体/下划线/删除线）。输出 HTML/Markdown/DOCX/EPUB/PDF。 | 宏和模板语义、域/页码、浮动环绕、主题样式、VML/EMF/WMF 和页眉页脚版式不保留；脚注不是 Word 原生脚注对象。 |
| ODT、OTT、FODT | 段落、标题、基础文字/段落样式、对齐与缩进（`fo:margin-left`/`fo:text-indent`）、列表、表格及部分 PNG/JPEG/GIF/WebP/SVG 图片、页眉/页脚文本、脚注/尾注（行内引用 + 正文）。 | 模板语义、批注、修订、图表、嵌入对象和高级分页不保留；FODT 不读取包外资源。 |
| EPUB、标准封装 KEPUB | 读取章节 XHTML 并按共享版式模型输出；表格（`th`/`caption`/`colspan`/`rowspan`）、列表（含嵌套）、引用块、定义列表、`pre`、图片、`figure/figcaption`、`<hr>` 与脚注引用均保留；脚注正文输出带 `id` 的 `epub-footnote` 段落。 | 不支持 DRM/密码保护；SVG/canvas/媒体等仍整章跳过；脚注不生成回链；KEPUB 专有行为不保留。 |
| MOBI 7、AZW3/MOBI 8、AZW | 自研 PalmDB/PalmDOC 解析器读取未压缩或 PalmDOC 压缩的 CP1252/UTF-8 文本记录，标记正文扁平化为段落。 | HUFF/CDIC 压缩、DRM、固定版式、嵌入资源、样式和链接重建不支持；输入文本上限 32 MiB。 |
| FB2 | 读取 FictionBook 2 结构并重排为 PDF；映射标题、段落、强调、引用、诗歌、外链和内嵌 JPEG/PNG/GIF 图片。 | 外链图片、其他图片类型或无效 Base64、元数据和封面不映射。 |
| RTF | 控制字、分组及 ANSI/Unicode 转义；段落、粗体/斜体/下划线/删除线、字号、对齐、分页符和 `\pict` 内嵌 PNG/JPEG。 | 表格扁平化为制表符；其他图片类型、对象、页眉页脚、脚注、颜色和复杂布局不映射。 |
| HWPX | OWPML section 顺序、段落、表格（`cellSpan`/`rowspan`）、图片（含裁剪、90° 倍数旋转、镜像、位置 CSS 外边距）、超链接（`hp:field`）、字符/段落样式、标题、页眉/页脚、脚注/尾注、页面边距、分栏和多节分页。输出 PDF/HTML/Markdown/DOCX/EPUB/HWPX。 | 旧版 HWP、加密部件、复杂字段和未覆盖的高级样式不支持；HWPX 写出为最小 OWPML 包。 |
| XPS/OpenXPS | 解析包关系和固定页面 XML，提供 Canvas、Path、Glyphs 子集；CLI 可转 PDF/HTML/Markdown。 | 矢量路径与精确版面定位不还原；XPS 专有资源、复杂绘图属性和字体支持有限。 |
| EML、MSG | MIME 正文、内嵌图片附件与文本附件；MSG 优先 HTML 正文，其次 Unicode 文本，最后解码 LZFu 压缩 RTF；表格与 PNG/JPEG 图片渲染为 HTML。 | 签名语义不保留；MSG 的其他二进制附件只列元数据。 |
| MDX（MDict 词典）、MDD（配套资源） | 读取引擎 2.0 键索引与记录块（stored/zlib；`Encrypted="2"` 无口令解码），输出词条版式；`--mdd` 可按名解析 MDD 资源并内嵌图片。 | 引擎 1.2（LZO）与注册码加密（`Encrypted="1"`/`"3"`）不支持；`@@@LINK`/`entry://` 交叉链接不解析。 |

## 文本与网页

| 输入格式 | 当前行为 | 主要限制 |
|---|---|---|
| HTML | 文件转换可按源文件位置读取相对图片、CSS 和字体；内存转换没有文件系统资源基址。 | CSS、字符集、字体和外链资源取决于页面后端能力。 |
| TXT | 识别 UTF-8/UTF-16 BOM 和有效 UTF-8；无 BOM 且非有效 UTF-8 时尝试 GBK/CP936，然后排版。 | 编码检测为启发式；不自动识别 Big5、Shift-JIS 等。 |
| Markdown | 标题（ATX/Setext）、段落、强调/删除线、链接（含 title）、引用、有序/无序/任务列表、分隔线、围栏/缩进代码、管道表格（对齐与转义 `\|`）、自动链接、图片、内联 `<br>` 与块级 `<hr>`。 | 不承诺完整 CommonMark；图片在解析阶段保留为 `<img>`，不主动下载远端资源。 |
| HTMLZ | 读取 index.html/index.htm 并加载包内 CSS 和相对图片；**可写出**含 index.html 的 ZIP。 | 包级元数据、未映射附件和复杂 CSS/背景图不保留。 |
| TXTZ | 读取 index.txt，支持 UTF-16 BOM、UTF-8 和 GBK；**可写出** ZIP 容器。 | 容器元数据和其它成员不保留。 |
| PMLZ | 读取 index.pml 并处理基础段落控制符，**可写出** PMLZ。 | 高级 PML 控制、复杂布局和元数据不保留；内置字体不能表示的字符替换为问号。 |

## 演示文稿

PPTX/PPTM/POTX/POTM/PPSX/PPSM 与 ODP/OTP/FODP 可按演示顺序读取页面文字、图片和备注，
并输出 PDF/HTML/Markdown/DOCX/EPUB。

- HTML 输出保留文本框/图片位置（CSS margins）、图片与文本框旋转（CSS transform）、图片裁剪
  以及每页备注段落。
- PDF 输出保留文字、PPTX/ODP 内嵌图片和每页书签；不消费 CSS 定位/旋转。
- 页面尺寸、母版、字体、图表、动画、模板行为和 Z-order 不重建；不写原生 PPTX/ODP。

## 共享版式模型与输出边界

共享版式模型包含标题、段落、列表、表格、链接、图片、脚注和水平分隔线。DOCX/ODT/PPTX/ODP/
HWPX/EML/XPS/EPUB/FB2 的读取器都产出它，再由 HTML→PDF 写出器生成 PDF。

公开输出为 **HTML、Markdown、DOCX、EPUB、HTMLZ、TXTZ、PMLZ 与 HWPX**：

- HTML 是公开的版式中间表示；Markdown 由 `qw_markdown_from_html` 生成。
- DOCX 是最小 WordprocessingML 包（段落、标题、强调、列表文本、超链接关系、Word 表格与图片）；
  不写脚注对象或页眉页脚部件。
- EPUB 是最小 EPUB 2 包（单章 XHTML + OPF + NCX）。
- HTMLZ/TXTZ/PMLZ 由 `quirewise-ebook` 的容器写出器生成；HWPX 由 `qw_hwpx_create` 生成最小
  OWPML 包。
- PDF→DOCX/EPUB 走**保留版式**路线：每页按 120 dpi 栅格化为 JPEG 后嵌入（最多 24 页，
  视觉版式保留、文本不可编辑）；PDF→HTML/Markdown 仍只重建文本层。

源文件中未映射的高级样式、布局、附件、封面和元数据不会保留。
