# SymPerturb 输入与输出规范（中文版）

## 输入

### 1. 症状矩阵

CSV：每行一个参与者，每列一个症状变量。症状分析列应为数值型，并统一方向为“数值越高越严重”。

### 2. 模块映射

CSV：

```csv
symptom,module
Fatigue,Sleep-fatigue
Insomnia,Sleep-fatigue
```

症状名称必须与症状矩阵列名一致。

### 3. Anchors（推荐）

```csv
symptom,anchor
Fatigue,0
Insomnia,0
```

Anchor 应具有临床或量表解释，不应机械设为 0。

### 4. Weights（可选）

```csv
symptom,weight
Fatigue,1
Insomnia,1
```

未提供时采用参考等权重。

### 5. YAML config

用于指定：

- 量表上下界；
- ridge 参数；
- edge threshold；
- state map；
- dose grid；
- breadth/module threshold；
- topology blocking 参数；
- combination partner set；
- bootstrap 次数；
- sequence optimisation 的折扣、成本和约束。

## 主要输出

### `target_scores.csv`

靶点层面主表：七个 raw utilities、七个 normalized utilities、VPPS、rank、direct target benefit、beneficial spillover、adverse spillover。

### `dose_response.csv`

各靶点在不同剂量下的系统响应。

### `pair_scores.csv`

联合靶点与共同结局集合上的有符号增量 pair value。

### `robustness.csv`

不同分析情景下的排序敏感性。Robustness 与 VPPS 分开。

### `bootstrap_summary.csv`

完整流程 bootstrap 的不确定性摘要、排名分布和 top-k 选择概率。

### `sequence_optimization.csv`

在显式决策目标下得到的序列及其边际价值。不要解释为自然病程时间顺序。

### `network_edges.csv`

参考拟合网络中的边信息，主要用于审计 topology outcomes。

### 图形与报告

包括 VPPS ranking、dose-response 图和 Markdown 自动报告。图形仅用于解释模型结果，不改变科学解释边界。
