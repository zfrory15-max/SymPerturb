# SymPerturb 中文使用指南

## 1. 最快开始

安装：

```bash
pip install -e .
```

运行仓库示例：

```bash
symperturb \
  --data examples/synthetic_symptoms.csv \
  --modules examples/modules.csv \
  --anchors examples/anchors.csv \
  --config examples/config.yaml \
  --out example-output
```

Windows PowerShell 可以写成一行：

```powershell
symperturb --data examples/synthetic_symptoms.csv --modules examples/modules.csv --anchors examples/anchors.csv --config examples/config.yaml --out example-output
```

## 2. 自己的数据如何准备

### 症状数据

CSV 文件，每行一个研究对象，每列一个症状。分析列应为数值型。

示例：

```csv
Fatigue,Insomnia,Pain,Anxiety
2,3,1,2
1,2,0,1
3,4,2,3
```

### 模块文件

至少包含：

```csv
symptom,module
Fatigue,Sleep-fatigue
Insomnia,Sleep-fatigue
Pain,Somatic
Anxiety,Affective
```

### 锚点文件

推荐显式提供：

```csv
symptom,anchor
Fatigue,0
Insomnia,0
Pain,0
Anxiety,0
```

不要因为量表最低值恰好是 0 就自动认为 0 是临床合理的 knockout anchor。锚点应结合症状编码和临床含义预先规定。

### 症状权重

如果有患者优先级或临床权重，可提供：

```csv
symptom,weight
Fatigue,1
Insomnia,1
Pain,1
Anxiety,1
```

否则参考分析使用等权重。

## 3. 建议的分析顺序

推荐按以下顺序完成：

1. 确认所有症状方向统一为“数值越高越严重”；
2. 预先定义候选靶点；
3. 提供 module map 与 anchor；
4. 拟合参考网络；
5. 运行 vKO / vKD；
6. 运行 vDP，查看剂量–反应曲线；
7. 计算 topology blocking；
8. 计算 pair / combination value；
9. 如有明确决策问题，再运行 sequence optimisation；
10. 计算七个 utility 与 VPPS；
11. 单独完成 sensitivity / robustness；
12. 运行 complete-pipeline bootstrap。

## 4. 最重要的输出文件

### `target_scores.csv`

主要靶点结果表。应优先检查：

- raw efficacy；
- dose efficiency；
- breadth；
- cross-module；
- communication block；
- combination value；
- responsiveness；
- 各标准化分数；
- VPPS；
- rank；
- direct target benefit；
- beneficial downstream spillover；
- adverse downstream spillover。

### `dose_response.csv`

查看不同 `alpha` 下的 `G_j(alpha)`，用于判断反应是否线性、存在边界饱和或出现明显非线性。

### `pair_scores.csv`

查看联合靶点相对于较优单靶点的增量价值。Confirmatory 解读应关注有符号值，而不是只保留正值。

### `robustness.csv`

用于观察不同分析参数情景下的排序敏感性。不要把 robustness 当成第八个 utility 加回 VPPS。

### `bootstrap_summary.csv`

用于评估完整分析流程的不确定性，应重点报告 rank distribution 和 top-k selection probability。

## 5. 论文中推荐如何报告

不要只给一个 VPPS 排名。至少同时呈现：

- 七维 utility profile；
- VPPS 与排序；
- sensitivity / robustness；
- bootstrap uncertainty；
- direct / beneficial spillover / adverse spillover；
- 关键 state-map sensitivity；
- exact vKO 的处理方式。

## 6. 常见错误

### 错误 1：把 VPPS 当作治疗效果

错误：`Fatigue had a VPPS of 92, demonstrating that treating fatigue would improve the system.`

推荐：`Fatigue ranked highest under the prespecified SymPerturb model, generating a model-derived target hypothesis for longitudinal or experimental testing.`

### 错误 2：把 sequence 当作疾病进展顺序

Sequence optimisation 的顺序来自目标函数、成本、折扣与约束，不代表症状自然发生的时间顺序。

### 错误 3：exact vKO 后保留常数列重估网络

这会导致零方差和协方差奇异问题。应采用删除目标后的 induced network、topology-only deletion 或预设 soft vKO。

### 错误 4：跨队列比较 VPPS 的绝对数值

VPPS 在候选集合内部标准化，因此不同网络、队列或候选集合的 0–100 分数不是同一个绝对量尺。
