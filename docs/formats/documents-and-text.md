# 文档、电子书与文本

> 状态（2026-11-15）：下表中的 DOCX/ODT 系列、EPUB、FB2、PPTX/ODP 系列、HWPX、EML、
> MOBI/AZW3、MDict MDX/MDD、HTMLZ、TXTZ、PMLZ、RTF、TXT/Markdown/HTML 已接入统一转换
> 入口，可用 CLI 转 PDF；XPS、旧版 .doc/.wps/.pages、CHM/LIT/LRF 等仍只有库 API（或完全
> 没有实现），CLI 返回 `unsupported`。以 [格式能力总览](support-matrix.md) 的三态口径为准。

本文说明版式类文件当前可转换的内容范围。输出通常保留可识别的文字结构，而不是原文件的完整视觉效果或所有元数据。

## 文档与电子书

| 输入格式 | 当前可读取内容 | 主要限制 |
|---|---|---|
| DOCX、DOCM、DOTX、DOTM | 正文、常见字符和段落样式、内置标题、对齐、分节纸张尺寸和边距、分页符、基础表格、水平合并、部分单元格底色、JPEG/PNG/GIF/BMP/TIFF/SVG 图片、安全外链、书签及常见编号列表。 | 宏和模板语义不保留。页眉页脚、复杂表格布局、纵向合并、浮动环绕、主题样式、VML/EMF/WMF 和高级分页尚未映射。图片受单图和累计大小限制；不能解码的图片可能跳过并在报告中说明。 |
| ODT、OTT、FODT | 段落、标题、基础文字/段落样式、列表、表格及部分 PNG/JPEG/GIF/WebP/SVG 图片。 | 模板语义、页眉页脚、高级分页、脚注尾注、批注、修订、图表和嵌入对象不保留。FODT 不读取包外资源。 |
| EPUB、标准封装 KEPUB | 读取章节 XHTML 并输出 PDF；`class`/`style` 属性、样式表链接等纯样式内容会被忽略，章节仍按共享版式模型读出。 | 不支持 DRM/密码保护。表格、列表、图片、嵌入对象等结构内容整章会被跳过；若全部章节都不可读则返回 `unsupported`。KEPUB 专有行为和元数据不保留。 |
| MOBI 7、AZW3/MOBI 8、AZW | 自研 PalmDB/PalmDOC 解析器读取未压缩或 PalmDOC 压缩的 CP1252/UTF-8 文本记录，自研标记处理器把正文 HTML 转成纯文本后按段落排版为 PDF。 | HUFF/CDIC 压缩、DRM、固定版式、嵌入资源、样式和链接重建暂不支持；标记正文会扁平化为段落文本。输入文本上限 32 MiB。 |
| FB2 | 由自研 XML 解析器读取 FictionBook 2 结构并重排为 PDF；可映射标题、段落、强调、引用、诗歌、外链，以及内嵌 JPEG/PNG/GIF 图片。 | 外链图片、其他图片类型或无效 Base64 图片不支持；FB2 元数据和封面信息不映射。 |
| RTF | 自研 RTF 控制字、分组及 ANSI/Unicode 转义解析；支持段落、粗体、斜体、下划线、删除线、字号、对齐、分页符和 `\pict` 内嵌 PNG/JPEG。单张图片载荷上限 32 MiB；图片转为 data URI 后交给通用 HTML/PDF 排版后端。 | 表格扁平化为制表符；其它图片类型、对象、页眉页脚、脚注、颜色和复杂布局未映射。 |
| HWPX | 读取 OWPML section 顺序；段落、简单表格、制表符和换行可排版。 | 样式、分页、图片数据、页眉页脚、元数据和加密部件不支持；嵌入对象以占位文字表示；不支持旧版 HWP；不写出 HWPX。 |
| XPS/OpenXPS | 自研解析包关系和固定页面 XML，提供 Canvas、Path、Glyphs 子集的页面读取 API。 | **CLI 未接入 XPS→PDF 路由**；调用方需要自行把页面 XML 转成 SVG/PDF。XPS 专有资源、复杂绘图属性和字体支持有限。 |
| EML | 读取常见 RFC 5322/MIME 头和正文，优先选择 text/plain；附件信息进入版式模型。 | PDF 中仅列附件名称、类型和大小，不导出附件数据。未知编码、RFC 2231 文件名、签名语义和 MSG 未覆盖。EML 输出使用通用主题及 ASCII 附件名。 |
| MDX（MDict 词典）、MDD（配套资源文件） | 自研 MDict 容器解析器读取引擎 2.0 的键索引与记录块（stored/zlib；`Encrypted="2"` 用块校验和派生 RIPEMD-128 块密钥，无需口令），把词条键和释义统一转成 UTF-8，按"词典标题 + 每个词条一节"排版为 PDF；`--to txt` 输出"键 + 去标签释义"。MDD 只做 `--check` 结构校验，并通过库 API 暴露资源名/内容。 | 引擎 1.2（LZO）与注册码加密（`Encrypted="1"`/`"3"`，Salsa-20）返回 `unsupported`；MDD 图片不嵌入 PDF，`@@@LINK`/`entry://` 交叉链接不解析，样式表和脚本忽略。记录流上限 192 MiB，渲染文本上限 96 MiB。 |

## 文本与网页

| 输入格式 | 当前行为 | 主要限制 |
|---|---|---|
| HTML | 文件转换可按源文件位置读取相对图片、CSS 和字体；内存转换没有文件系统资源基址。 | CSS、字符集、字体和外链资源取决于页面后端能力。 |
| TXT | 识别 UTF-8/UTF-16 BOM 和有效 UTF-8；无 BOM 且不是有效 UTF-8 时尝试 GBK/CP936，之后排版为 PDF。 | 编码检测为启发式；不自动识别 Big5、Shift-JIS 等编码。 |
| Markdown（项目自研解析子集） | 支持标题、段落、强调、链接、引用、列表、分隔线、围栏代码块和缩进代码块。 | 不承诺完整 CommonMark 兼容；图片使用 alt 文本，不加载图片资源。 |
| HTMLZ | 读取 index.html 或 index.htm，并可加载包内 CSS 和相对图片。 | 不支持写出 ZIP 归档；不保留包级元数据、未映射附件及其它成员；复杂 CSS、背景图片和动画图片有限。 |
| TXTz | 读取 index.txt，缺失时尝试选择支持的 .txt 成员；支持 UTF-16 BOM、UTF-8 和 GBK 文本归一化。 | 不支持写出 ZIP32 容器；不保留容器元数据和其它成员。 |
| PMLz | 读取 index.pml 并处理基础段落控制符。 | 高级 PML 控制、复杂布局和元数据不保留。内置字体不能表示的字符会替换为问号。 |

## 演示文稿

PPTX/PPTM/POTX/POTM/PPSX/PPSM 与 ODP/OTP/FODP 可按演示顺序读取页面文字，并将页面内容排版为 PDF。当前主要保留标题、段落和简单列表。

页面尺寸、母版、形状位置、字体、图片、图表、备注、动画、模板行为和复杂样式不保留；不生成原生 PowerPoint 或 OpenDocument 演示文稿。

## 共享版式模型与输出边界

文档包内部有一个共享版式模型（标题、段落、列表、表格、链接、图片），DOCX/ODT/PPTX/ODP/HWPX/EML/XPS/EPUB/FB2 的读取器都会产出它，再由 HTML→PDF 写出器生成 PDF。

需要明确的是：版式模型的公开输出是 **HTML、Markdown、DOCX、EPUB、HTMLZ、TXTZ 与 HWPX**。每个版式读取器都公开自己的 `*_document_html`（共享版式模型最终都落成 HTML），`document` 的 `qw_convert_*` 增加对应目标：HTML 直接返回中间表示；Markdown 由 `quirewise-text` 的 `qw_markdown_from_html` 生成；DOCX 页眉/页脚以文本段落进入 HTML；DOCX 是最小 WordprocessingML 包（段落、标题、强调、列表文本，链接与表格扁平化，图片降为 alt 文本）；EPUB 是最小 EPUB 2 包（单章 XHTML + OPF + NCX）；HTMLZ 是含 index.html 的 ZIP，TXTZ 是含 index.txt 的 ZIP（由 `quirewise-ebook` 的 `qw_htmlz_create`/`qw_text_archive_create` 写出）；HWPX 是最小 OWPML 包（`qw_hwpx_create`，段落/文本，表格扁平化）。PDF 输入 DOCX/EPUB 时改为保留版式路线：每页按 120 dpi 栅格化为 JPEG 后嵌入（最多 24 页；视觉版式保留、文本不可编辑）；PDF 输入 HTML/Markdown 时仍只重建文本层。PMLZ 仍只有读取/PDF 路线；数据/字幕/表格目标转交给各自包的公开写出器。历史文档中"可写出 Org、DocBook、AsciiDoc、Typst、LaTeX、RST、Textile、MediaWiki、Man、OPML、IPYNB"的列表仍不成立；HTML/Markdown/DOCX/EPUB/HTMLZ/TXTZ/HWPX 现在成立。

转换到 PDF 时，源文件中未映射的高级样式、布局、附件、封面和元数据不会保留。
