---
name: symperturb-analysis-zh
description: 中文执行、审计和解释 SymPerturb 横断面症状网络虚拟扰动分析。适用于 vKO、vKD、vDP、边级/节点中心 communication blocking、组合扰动、序列优化、七个效用维度、VPPS、robustness、完整流程 bootstrap，以及 SymPerturb Methods/Results 的撰写与核查。
---

# SymPerturb 中文分析 Skill

将 SymPerturb 作为**模型化靶点假设生成框架**使用，而不是因果干预估计器。

## 核心工作流程

1. 检查症状数据、模块映射、候选靶点、anchors、量表方向与边界、症状权重和分析配置。
2. 要求所有症状统一为“数值越高表示状态越差”。不要默认 0 具有临床意义；如提供症状特异性 anchor，应优先使用。
3. 用经验协方差 + 对角 ridge 正则化拟合参考高斯网络，求逆得到偏相关；仅在 topology outcomes 中使用 edge threshold。
4. 使用一般 location–scale map 进行状态扰动。linked map 仅作为参考特例，同时支持 location-only、scale-only 和独立参数化 map 的敏感性分析。
5. 严格区分四个原始扰动算子和三个分析过程：
   - vKO、vKD：状态算子；
   - edge-level、node-centred communication blocking：拓扑算子；
   - vDP：强度–反应评估；
   - combination perturbation：联合靶点构造；
   - sequence optimisation：显式决策目标下的优化过程。
6. 将 direct target benefit、beneficial downstream spillover 和 adverse downstream spillover 分开计算。不要把下游系统获益称为总临床获益。
7. 计算七个 utility：efficacy、dose efficiency、breadth、cross-module reach、communication block、combination value、responsiveness。
8. 在预设候选靶点集合内对每个 utility 标准化；常数维度赋 50；随后计算七维 VPPS。Robustness 不进入 VPPS。
9. 单独报告不同 sensitivity scenarios 下的 robustness；如需要不确定性评估，应运行 complete-pipeline bootstrap，每次重新执行网络估计、阈值化、扰动、效用计算、标准化和排序。
10. 输出可审计结果：target scores、raw/normalized utilities、dose curves、pair values、topology metrics、robustness/bootstrap、sequence objective。

## 必须遵守的解释边界

- 不得把横断面无向 GGM 的虚拟扰动描述为已识别的 `do()` intervention 或已证明的治疗效应。
- 不得从 sequence optimisation 推断真实生物学时间。顺序来自目标函数、折扣、成本和约束。
- 不得把 “communication blocking” 解释为已经证实的生物学信号传递；默认仅代表 adjacency attenuation。
- Exact vKO 后，如果目标列为常数，不得保留该列重新标准化或重新估计完整 covariance。需要 post-vKO network 时，应明确选择 induced network、topology-only deletion 或 soft vKO。
- 不得把不同 cohort、network 或 candidate set 的 VPPS 绝对值直接比较。VPPS 是当前候选集合内部的相对分数。
- 检查 efficacy、dose efficiency 和 responsiveness 是否冗余。在无界线性高斯 linked map 下可能有 `G_j(alpha)=alpha G_j(1)`。
- Confirmatory combination analysis 应保留有符号 pair increment，使不利和拮抗组合可见。

## 使用随附资源

- `references/method-specification.md`：数学定义、estimands、默认值和 operator 规范；
- `references/reporting-and-interpretation.md`：论文 Methods、Results、Discussion 和图注的写法；
- `references/input-output-contract.md`：输入/输出文件结构；
- `scripts/run_symperturb.py`：仓库中已安装参考包时运行分析；
- `scripts/check_skill_inputs.py`：用户自带输入文件时先检查格式。

## 完成前检查

最终输出前确认：

- 症状方向和 anchors 明确；
- candidate targets 和 module mapping 明确；
- state-map 及其 sensitivity maps 明确；
- direct / beneficial downstream / adverse downstream 不混淆；
- 七个 utilities 单独报告；
- robustness 未纳入 confirmatory VPPS；
- exact-vKO 的处理方式已说明；
- bounded / unbounded 假设在需要时已说明；
- 结论使用“模型推导的靶点假设”，而不是未经验证的“有效治疗靶点”。
