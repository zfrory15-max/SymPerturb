# SymPerturb 方法概述

本文档是 SymPerturb 中文版的人类可读方法摘要。更完整的数学定义见中文版 Skill 中的 `references/method-specification.md`，参考代码位于 `src/symperturb/`。

## 1. 概念架构

SymPerturb 可分为三个层次：

- **状态层（state layer）**：vKO、vKD、vDP；
- **拓扑层（topology layer）**：边级 communication blocking、节点中心 communication blocking；
- **多靶点层（multi-target layer）**：组合扰动与序列优化。

这些组件并不是同一数学类型。vKO、vKD 和两种 communication blocking 是原始扰动算子；vDP 是强度–反应评估过程；组合扰动是联合靶点构造；序列优化是显式决策目标下的优化过程。

## 2. 基础统计模型

参考实现使用连续或近似连续症状的高斯模型：

`X ~ N_p(mu, Sigma)`。

有限样本下，对经验协方差矩阵进行对角 ridge 正则化，再求逆得到精度矩阵和偏相关。仅在拓扑类结局中对较小偏相关进行阈值化。

这里的网络估计过程属于 ridge-like covariance regularisation + hard edge thresholding，不应误写为 graphical LASSO。

## 3. 一般 location–scale 状态扰动

对目标症状集合 `S`，设临床可解释锚点为 `c_S`。一般状态扰动允许 location 与 scale 分别变化：

`X_S^(alpha) = c_S + D_mu(alpha)(mu_S-c_S) + D_sigma(alpha)(X_S-mu_S)`。

参考 linked map 令 `D_mu = D_sigma = diag(1-alpha_s)`。该设定同时收缩目标症状相对锚点的均值偏移和标准差，但它只是参考建模假设，并不是治疗改善必然同时降低均值和方差的临床规律。

应用分析建议至少比较：

- linked map；
- location-only；
- scale-only；
- 独立参数化 location–scale map。

## 4. 主要估计对象

默认 `G_j(alpha)` 是一个**下游 spillover estimand**：即目标症状受到扰动后，非目标症状的加权平均标准化改善。

必须把以下三个量分开：

1. 目标症状本身的直接获益；
2. 有利的下游 spillover；
3. 不利或有害的下游 spillover。

因此，默认 `G_j(alpha)` 不能直接称为“总临床获益”。

## 5. 四个原始扰动算子

### vKO：虚拟敲除

单位剂量 `alpha=1`。在参考 linked map 中，目标症状被固定到指定锚点并可具有零残余方差。

Exact vKO 会产生常数目标列，因此不能保留该列后重新标准化或重新估计完整协方差矩阵。

### vKD：虚拟敲降

`0<alpha<1`，用于模拟目标症状的部分改善。

### 边级 communication blocking

对某一选定边进行比例衰减，用于评估特定图函数对该边的依赖程度。

### 节点中心 communication blocking

同时衰减目标节点所有 incident edges，用于评估图拓扑功能对该节点连接结构的依赖。

“communication” 仅为框架中的名称，不代表已经证明症状之间存在生物学信号传递。

## 6. 三个分析过程

### vDP：虚拟剂量扰动

在预设剂量网格上计算 `G_j(alpha)`，观察反应是否线性、出现阈值或趋于饱和。

在无界、线性、高斯 linked map 下，可能出现：

`G_j(alpha)=alpha G_j(1)`。

因此 efficacy、dose efficiency 和 responsiveness 可能高度冗余，应在实际数据中检查。

### 组合扰动

对两个或多个目标施加联合扰动，并在相同的非目标结局集合上与单靶点结果比较。配对增量价值的核心问题是：联合靶点是否优于其中较好的单靶点？

Confirmatory 分析应保留有符号增量值，使拮抗或有害组合仍然可见。

### 序列优化

在显式的收益、折扣、成本和约束条件下搜索靶点顺序。该顺序来自决策目标，而不是由横断面网络识别出的真实生物学时间顺序。

## 7. 七个效用维度

SymPerturb 采用七个方向统一为“越高越好”的效用维度：

1. 下游效力（efficacy）；
2. 剂量效率（dose efficiency）；
3. 广度（breadth）；
4. 跨模块覆盖（cross-module reach）；
5. communication-block value；
6. 组合价值（combination value）；
7. 响应性（responsiveness）。

## 8. VPPS

每个原始效用维度在预先指定的候选靶点集合内进行 0–100 min–max 标准化。如果某个维度所有候选靶点取值完全相同，则赋予中性分数 50。

最终 VPPS 是七个标准化效用维度的加权平均。参考方法学实现使用等权重。

**Robustness 不属于临床效用维度，不纳入 confirmatory VPPS。**

## 9. Robustness 与 bootstrap

Robustness 用于描述分析设定变化时排序的敏感性，应与 VPPS 分开报告。

应用数据还应采用 complete-pipeline bootstrap：每次重采样都重新执行网络估计、阈值选择、扰动、效用计算、候选集合标准化和排序，并输出：

- 效用及 VPPS 的不确定性区间；
- rank distribution；
- top-k selection probability。

## 10. 解释原则

SymPerturb 回答的是：

> 在给定拟合统计系统中，施加一个明确规定的虚拟扰动算子后，系统的模型化响应如何变化？

它本身不能回答：

> 对真实患者施加某项治疗后会产生什么因果效果？
