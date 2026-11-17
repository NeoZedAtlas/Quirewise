# 图像、矢量图与归档

> 状态（2026-11-17）：本页按当前第一方实现重写。图像编码写出、CBR/CB7 漫画路由和
> 受限 7z 解包都已进入发布包；未实现入口稳定返回 `UNSUPPORTED`。

## 1. 图像输入

`quirewise-image` 通过内容探测（`qw_image_probe`）识别并解码以下格式：

JPEG（基线/渐进式）、PNG（含 APNG/MNG 默认帧）、GIF87a/89a（首帧）、BMP、TIFF（顶层 IFD）、
WebP（VP8/VP8L/Alpha/动画帧）、JP2/J2K、PSD/PSB（扁平合成图）、OpenEXR（单 part 扫描线）、
Radiance HDR、Softimage PIC、TGA、PCX、PFM、DDS（BC1/DXT1 首层）、QOI、XPM/XBM/WBMP、
PBM/PGM/PPM/PNM/PAM、ICO/CUR、ICNS、SGI、Sun Raster、MIFF、DICOM（单帧未压缩）、XCF。

GIF/WebP/TIFF/ICO/CUR/ICNS 的多帧/多条目可在库层展开为多页；CLI 目前只取单页转 PDF。

明确不支持（探测可能成功，解码返回 `UNSUPPORTED`）：AVIF、HEIC/HEIF、JPEG XL、PCD、
相机 RAW（DNG/TIFF-CFA、CR3、RAF、X3F、CRW、MRW）。发布包不含去马赛克实现，也不链接
LibRaw。

## 2. 编解码实现归属

| 路线 | 解析/解码 | 说明 |
|---|---|---|
| PNG | 第一方 | 块顺序、CRC、色彩类型、滤波、Adam7、16 位样本 |
| JPEG | 第一方 | marker/段/霍夫曼表/帧与扫描头/熵数据；8 位单/三/四分量，基线+渐进式 |
| WebP | 第一方 | RIFF/VP8X/VP8/VP8L/ALPH/ANIM/ANMF，静态与动画帧 |
| JP2/J2K | 第一方 | 容器、packet、tier-1、DWT、MQ、灰度/sRGB/SYCC/CMYK 子集 |
| TIFF | 第一方 | Classic/BigTIFF、strip、PackBits/LZW/Deflate/G4/受限 JPEG strip |
| GIF/BMP/TGA/PSD/EXR/HDR/PNM/QOI/PCX/DDS/XPM/SGI/RAS/MIFF/DCM | 第一方 | 各自子集见测试与头文件 |
| RAW / AVIF / HEIC / JXL / PCD | 无解码器 | 仅探测，解码返回 `UNSUPPORTED` |
| 归档解压（ZIP/7z/XZ/LZMA） | 第一方 `quirewise-compression` | 不链接 Zlib/LibLZMA/7-Zip |

所有解码器受统一资源限制约束（像素、维度、帧数、字节数）；超限返回 `RESOURCE_LIMIT`。

## 3. 图像输出

`quirewise-image` 公开 `qw_image_encode`、`qw_image_encode_format_name` 与
`qw_image_buffer_free`，可从 Gray8/RGB24 像素写出：

- PNG（deflate 压缩 IDAT）
- BMP（24 位）
- baseline TIFF（未压缩）
- baseline JPEG（JFIF 4:4:4，质量 85）
- lossless WebP（VP8L，无变换/LZ77）
- TGA（未压缩）
- QOI（literal-only）
- 二进制 PPM（P6）
- GIF（单帧，标准 LZW 子块）
- Radiance HDR（RGBE）
- 未压缩 SGI RGB
- 8 位 RLE PCX

CLI 的 `--to png|bmp|tiff|jpg|webp|tga|qoi|ppm|gif|hdr|sgi|pcx` 对任意可解码输入走同一编码器；
`--image-crop L,T,R,B` 和 `--image-resize WxH` 在编码前作用于像素。写出器不保留 EXIF/ICC/动画，
GIF 只写单帧，WebP 只写静态 VP8L。

AVIF/HEIC/JXL/APNG/MNG/PSD/JP2 等历史文档中列出的其它图像写出器仍不在发布范围内。

## 4. 矢量与打印图形

| 格式 | 能力 | 边界 |
|---|---|---|
| SVG/SVGZ | 第一方子集解析与 RGBA8 栅格化（文档单位 2×）；SVGZ 先解 gzip | 仅覆盖自研解析器的图形/路径子集；透明区域白底合成，不保留矢量结构、链接、动画、元数据 |
| EPS / PS / legacy AI | 无实现 | 历史文档声称的 PDF 互转已不在发布包内 |
| EMF/WMF/CGM/CDR/VSD/FODG | 无实现 | 未进入发布包 |

SVG/SVGZ 已接入 CLI：`.svg/.svgz` 可用 `--to pdf`（以及 `--check`）栅格化为单页 PDF；
`--page image|a4` 控制页面框。仅支持自研子集，含 `<text>` 等未支持特性时返回 `UNSUPPORTED`。

## 5. 漫画与归档

| 输入/输出 | 能力 | 边界 |
|---|---|---|
| CBZ | 自研 ZIP reader 读取图像成员，按自然数顺序逐页；支持 Stored/Deflate、ZIP64、CRC 和传统 ZipCrypto | WinZip AES 等加密方法不支持 |
| CBT | 自研 USTAR reader（GNU longname/PAX path）；内容交给图像解码器 | 稀疏 TAR、超大展开不支持 |
| CBR | 归档包解析 RAR4/RAR5 头与条目元数据；comic 路由接受 **stored** 条目并按页解码 | 压缩 RAR 条目、加密 RAR 不支持 |
| CB7 | 7z 容器经受限解包（Copy/LZMA/LZMA2/Delta/BCJ）后按图像成员逐页 | 加密、PPMd、BZip2、多 folder 不支持 |
| 图像目录 | `quirewise-image` 可非递归枚举支持格式的目录 | CLI 没有目录输入 |

归档成员按“文件名 + 支持格式”筛选；页面输出不保留条目名、压缩方式或源元数据。
