# PDF 与页面格式

> 状态（2026-11-17）：统一 `quirewise` CLI 已覆盖 PDF 读取/栅格化/文本抽取/合并、
> 加密 PDF 用户口令、书签大纲、PDF→HTML/Markdown 与保留版式的 PDF→DOCX/EPUB。
> 本页按当前代码描述；逐项矩阵见 [格式能力总览](support-matrix.md)。

## 输入

- PDF：xref 表/xref 流/hybrid、`/Type /ObjStm` 对象流；RC4（V1/V2）、AES-128（V4 `/AESV2`）
  与 AES-256（V5/R5–R6 `/AESV3`）加密文档可在提供用户口令时打开（CLI 用
  `--pdf-password`），其他 security handler 返回稳定的 `UNSUPPORTED`。
- 页面容器：UVZ / PDZ / CAJ / CEB 由 `quirewise-page` / `quirewise-pdg` 解析；CAJ 的 JP2
  负载经内部 Image 解码；CEB 解密后输出 PDF。
- DjVu：`quirewise-page` 内部解码 BZZ、JB2、IW44、DJVM/DIRM bundled 多页与文本层。
- PDG/PDZ：由 `quirewise-pdg` 解码、解密和渲染。页载荷本身是 PDF 的成员由
  `quirewise-pdg` 返回 `PDG_ERR_EXTERNAL_DECODER_REQUIRED`（库不依赖文档 PDF 引擎）；
  组合层（`quirewise-pipeline` 的 page_routes）调用 Document 引擎按 300 dpi 栅格化，并按成员顺序合并
  `pdg_type 0x1A` 发行版 PDF。加密的 0x1A 成员仍会显式失败。

## 输出

- PDF：透传、多文档合并（汇总并校正输入书签的页码/层级）、从 HTML/Office/演示/电子书布局生成；
  `/Info` 标题/作者可写（非 ASCII 用 UTF-16BE），h1–h6 自动生成嵌套书签，书签目标为
  `/XYZ` 坐标而不是整页 `/Fit`。
- 页面图像：RGB24/Gray8 栅格化。PDF 首页可栅格化为 PNG/JPEG/BMP/TIFF/WebP（144 dpi），
  供封面、缩略图或图像重编码使用。
- 文本：PDF 文本提取为 UTF-8（无 OCR）；DjVu 文本层提取；CAD `--to txt` 输出图纸文本清单。
- 文本层重建：PDF→HTML/Markdown 由文本层生成。
- 保留版式重建：PDF→DOCX/EPUB 把每页按 120 dpi 栅格化为 JPEG 后嵌入（最多 24 页）；
  视觉版式保留，但文本不可编辑、表格不重建。

## 限制

- PDF/A 需要外部 Ghostscript/veraPDF，不属于本发布包范围；`--pdfa` 等选项返回用法错误。
- OCR、精确字形栅格化（PDF 页面栅格化使用内置近似字体）和对象流作为输出格式仍不在范围内。
- 有用户口令的加密 PDF 可**读取/转换**；但加密 PDF 不参与 `qw_pdf_merge`，合并请求会被拒绝。
- JBIG2 仅覆盖 generic region（MMR/T.88 算术）、symbol dictionary 与 text region 子集；
  Huffman 字典、refinement、halftone、pattern dictionary、转置 text region 返回
  `UNSUPPORTED`。
- PDF→DOCX/EPUB 是页面图片路线，不生成可编辑段落、表格或域。
- 所有尺寸、DPI、页数、输出字节数都有上限；超限返回 `RESOURCE_LIMIT`。
