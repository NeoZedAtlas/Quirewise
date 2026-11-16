# 外部依赖与暂不支持项说明

> 状态：2026-11-16 按当前 HEAD 核对。本页列出发布包内**稳定返回 `UNSUPPORTED`** 的能力，
> 区分“需要外部解码器/授权/规范验证”与“纯 C 可实现但工程量大、尚未排期”两类。
> 这些项目不会静默降级为错误结果；CLI 与库 API 都返回稳定的 `UNSUPPORTED`（或 `RESOURCE_LIMIT`）。
> 若后续引入外部后端，必须作为可选构建特性并保持纯 C 默认构建的现有行为不变。

## 1. 外部依赖类（发布包不内置）

| 能力/格式 | 当前行为 | 阻塞原因 | 可行路径 |
|---|---|---|---|
| AVIF、HEIC/HEIF、JPEG XL、Kodak PCD 解码 | 图像探测可识别部分签名；像素解码返回 `UNSUPPORTED` | AV1/HEVC/JPEG XL 编解码器与专利/实现复杂度；PCD 需要专有色彩流水线 | 以可选后端接入 libavif/libheif/libjxl；PCD 可用独立纯 C 解码器，但收益低 |
| 相机 RAW（DNG/CR3/RAF/X3F/CRW/MRW） | 结构探测；像素解码恒 `UNSUPPORTED` | 去马赛克、相机矩阵、镜头校正依赖 LibRaw 等成熟后端 | 可选 LibRaw 后端；默认构建保持探测-only |
| OCR（扫描 PDF/图片→文本） | PDF→TXT 只输出文本层；扫描件为空 | 需要 OCR 引擎与语言模型数据 | 外部 Tesseract/PaddleOCR 后端，不进入纯 C 核心 |
| PDF/A 一致性 | 可生成普通 PDF；不声明 PDF/A | 需要 veraPDF 等规范验证与字体嵌入策略 | 外部 veraPDF 验证 + 可选字体嵌入后端 |
| 视频/音频容器与编解码 | 不作为文档输入；无视频转码 | FFmpeg 级解码与专利/体积 | 外部 FFmpeg 后端，发布包不内置 |
| 加密词典（MDX `Encrypted="1"`/`"3"`）与 DRM 电子书 | 返回 `UNSUPPORTED` | 注册码/密钥管理与授权；绕过 DRM 不当 | 仅支持用户自有明文词典；不实现绕过 |
| CHM、LIT、LRF、PDB、RB、SNB、TCR | 返回 `UNSUPPORTED` | 历史格式/DRM/压缩变体，规范与样本稀缺 | 单独逆向与解析器；优先级低 |
| 字体、3D、CAD 专有内核 | 不作为文档输入 | 需要几何/字体引擎 | 独立后端或专用库 |

## 2. 纯 C 可实现但尚未排期

| 能力/格式 | 当前行为 | 说明 |
|---|---|---|
| MOBI HUFF/CDIC 压缩 | 返回 `UNSUPPORTED`；PalmDOC 未压缩与普通压缩可读 | HUFF/CDIC 解码器可实现，但需要字典/递归展开与资源上限；排期后补 |
| 压缩 RAR（非 stored） | 仅支持 stored 条目；压缩条目 `UNSUPPORTED` | RAR 解压算法复杂且有授权约束；优先保持 stored 与 CBZ/CBT/CB7 |
| XPS 矢量路径与精确版式 | 文本 + PNG 图片可用；矢量路径跳过 | 需要 XPS 路径→PDF 路径的解释器与坐标变换；属于版式重建工程 |
| DOCX/ODT 复杂版式（浮动环绕、页码字段、EMF/WMF） | 文本/表格/图片/页眉页脚可用；复杂对象跳过 | 需要完整版式模型与图元渲染；当前以 HTML 中间层保真可表达部分 |
| PPTX/ODP 形状位置、图表、动画、母版 | 文字、图片、备注、书签可用；形状位置/图表等不还原 | 需要演示文稿布局引擎与图表解析 |
| EPUB SVG/canvas/媒体 | 整章跳过；全跳过时返回 `UNSUPPORTED` | SVG 渲染或矢量转换需要独立实现；可先做静态 SVG 子集 |
| 邮件签名语义 | 正文/附件可用；签名验证不实现 | 需要 S/MIME/PGP 信任链与证书验证 |

## 3. 验收约束

- 上述项目在 `app/docs/formats/support-matrix.md` 中保持“不支持”或“仅部分支持”的准确描述；
- `run_acceptance.py` 的 smoke 不把 `UNSUPPORTED` 当作成功；
- 任何新增支持必须先有夹具、单测与 smoke，再更新矩阵；
- 外部后端只能作为可选构建特性，默认纯 C 构建的行为与错误码保持稳定。
