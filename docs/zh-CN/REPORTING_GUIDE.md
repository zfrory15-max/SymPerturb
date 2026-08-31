# SymPerturb 中文报告与解释规范

## Methods 中至少交代

- 网络模型与估计方法；
- ridge 或其他正则化设置；
- topology edge threshold；
- 症状方向；
- 候选靶点集合；
- 症状特异性 anchor；
- state map：linked / location-only / scale-only / independent；
- 量表边界及 bounded expectation 的处理；
- vKO、vKD、vDP、blocking、combination、sequence 的具体设置；
- 七个 utility 的定义；
- VPPS 权重；
- robustness 与 bootstrap 方案。

## Results 中建议分开呈现

1. 网络与候选靶点概况；
2. 单靶点 state perturbation；
3. dose-response；
4. topology blocking；
5. combination；
6. sequence optimisation（如果使用）；
7. 七维 utility profile + VPPS；
8. sensitivity / robustness；
9. bootstrap uncertainty。

## 推荐术语

推荐：

- model-derived intervention priority
- virtual perturbation priority
- target hypothesis
- downstream spillover
- topology dependence

谨慎或避免：

- causal target
- proven intervention target
- treatment effect
- symptom transmission
- biological sequence

## Discussion 中需要明确的限制

- 横断面无向 GGM 不识别干预方向；
- 未测量混杂仍然存在；
- state-map 与 anchor 是建模选择；
- breadth/module threshold 不等于 MCID；
- VPPS 权重不自动代表患者偏好；
- sequence optimisation 不等于 dynamic treatment regime；
- 需要纵向和实验验证。
