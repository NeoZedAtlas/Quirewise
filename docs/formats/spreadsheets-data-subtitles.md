# 表格、结构化数据与字幕

> 状态（2026-11-17）：`quirewise-spreadsheet`、`quirewise-data`、`quirewise-subtitle`
> 的读取与写出接口都已接入统一转换入口。本页按当前公开 API 与 CLI 路线描述；
> 逐项支持矩阵见 [格式能力总览](support-matrix.md)。

## 1. 工作簿与分隔文本

| 格式 | 读取能力 | 写出能力 | 主要限制 |
|---|---|---|---|
| XLSX/XLSM/XLTX | 按工作簿关系读取工作表和共享字符串；单元格值、常规公式缓存值、合并区间 | 写出 XLSX 包：全部工作表、单元格值、合并区间 | 不计算公式；样式、图表、图片、宏、模板行为不保留 |
| XLS/XLT | 读取 CFB 中的 BIFF8 Workbook/Book 流、共享字符串、单元格及缓存公式结果；SST 跨 `CONTINUE` 记录续接 | —（可作为任意工作簿输入转 XLSX/ODS/CSV/TSV） | 仅 BIFF8；不支持加密工作簿；越序单元格跳过 |
| ODS/OTS/FODS | 读取 ODF ZIP 包的 content.xml 或 FODS 平面 XML；值类型、重复行列、公式文本、合并区间 | 写出 ODS 包：全部工作表、单元格值、合并区间 | 公式不重算 |
| CSV/TSV | 识别逗号/制表符/分号；引号、转义引号、多行单元格 | 写出 CSV/TSV；默认首个工作表，可用 `--sheet N` 选择 | 字段按文本保存，不做类型推断；CSV/TSV 没有多工作表概念 |

工作簿写出器保留值的文本与合并区间，但不携带样式、列宽、图表、图片或公式重算结果。
CLI 的 `--to xlsx|ods|csv|tsv` 对应这些写出器；`--sheet N` 只影响 CSV/TSV。

## 2. 结构化数据

| 格式 | 读取能力 | 写出能力 | 主要限制 |
|---|---|---|---|
| JSON | 对象/数组顺序、数字原始词法 | 写出 JSON | 深度、节点数、输出大小受限 |
| JSON Lines | 每个非空物理行一个值 | 写出 JSONL（JSON 数组按每行一个记录输出） | 不支持跨行值或空行 |
| YAML | 单文档 block/flow mapping、sequence、常见标量、注释、引号字符串 | 写出 YAML | 不支持 anchors/aliases、自定义 tag、directives、block scalars、多文档流 |
| TOML | assignments、dotted/quoted keys、tables、arrays of tables、inline tables、日期时间 | 写出 TOML（要求根节点为对象） | 不支持 null |
| XML | 受限 UTF-8 XML 树；创建/查询/序列化；可选内部 DTD 校验 | 写出有序 XML 文档树 | 拒绝外部 DTD/自定义实体；不保留注释和处理指令；命名空间前缀保留但不解析 URI |
| vCard 2.1/3.0/4.0 | 多卡片、属性顺序、分组、原始参数、QP 软换行 | 写出 vCard | 其它旧字符集不支持 |
| OPML / iPynb | 经共享 XML/JSON 树读取；Markdown/TXT 可按标题层级写 OPML、写成单个 markdown cell 的 IPYNB | 写出仅适用于 Markdown/TXT 源 | 专有扩展不保留 |

JSON↔JSONL 会有意改变文档形状；XML 写出只接受读取器产生的 `$xml`/`$name`/`$attributes`/
`$content` 有序树，任意 JSON 树会返回 `UNSUPPORTED` 而不是猜测。DocBook 读取、OPML/iPynb
的专有语义和 `quirewise/xml.h` 的树修改仍不在公开范围内。

## 3. 字幕与定时文本

`quirewise-subtitle` 读取 SRT、WebVTT、LRC、MicroDVD、TTML、ASS/SSA、SAMI、SCC 为共享 cue
模型（开始/结束时间、标识、设置、文本），并写出全部九种格式（含 TTML）。CLI 的
`--to srt|vtt|lrc|sub|ass|ssa|sami|scc|ttml` 走这些写出器；所有字幕输入也可转 PDF
（时间轴文本页）。

主要边界：

- **ASS/SSA 直转**：`Name` 说话人写入 cue identifier；层、左/右/垂直边距和 `Effect` 写入 cue
  settings；`Text` 中 `{\i1}`、`{\pos(...)}` 等覆盖标签以 `|RAW:` 段原样保留，写回 ASS/SSA
  时恢复。转成其它格式时覆盖标签和位置信息会被丢弃。
- MicroDVD 缺少帧率时按 23.976 fps 解释；帧边界量化。
- TTML 支持 clock/offset 时间表达式和 begin/end/dur；样式、区域及嵌套 span 时序会扁平化，
  不支持 seq 容器。TTML 写出器输出 cue 的 begin/end 与转义文本（含 `<br/>`），不写样式、
  区域和元数据。
- SAMI 读取首个字幕 class，展平标记和样式。
- SCC 仅支持 CC1 pop-on 基础/特殊字符子集；WebVTT 的 NOTE/STYLE/REGION、头部元数据和 cue
  样式不保留；LRC 忽略 metadata tags。
- 跨格式写出时，目标格式无法表达的逐 cue 设置、显式结束时间、亚秒精度会被丢弃并在报告中说明。
- 输入和输出（PDF）使用 UTF-8，单文件上限 64 MiB。
