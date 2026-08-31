# SymPerturb method specification

## Contents

1. Statistical model
2. State intervention
3. Bounded scales
4. Primitive operators and procedures
5. Utility outcomes
6. VPPS
7. Robustness and bootstrap
8. Reference defaults

## 1. Statistical model

Assume continuous or approximately continuous symptom scores:

`X ~ N_p(mu, Sigma)`, with `Theta = Sigma^{-1}`.

Partial correlations are `rho_ij.-ij = -theta_ij / sqrt(theta_ii theta_jj)`.

The manuscript reference finite-sample estimator uses

`Sigma_hat_lambda = S + lambda * diag(S)`

followed by inversion. Partial correlations with absolute magnitude below `tau_W` are set to zero **for topology outcomes**. This is ridge-like covariance regularisation plus hard edge thresholding, not graphical LASSO.

## 2. General location-scale state intervention

Partition targets `S` and non-targets `K`. The Gaussian regression decomposition is

`X_K = mu_K + B (X_S - mu_S) + epsilon`,

where

`B = Sigma_KS Sigma_SS^{-1}`

and

`Omega = Sigma_KK - Sigma_KS Sigma_SS^{-1} Sigma_SK`.

Use symptom-specific anchors `c_S` and separate location and scale maps:

`X_S^(alpha) = c_S + D_mu(alpha)(mu_S-c_S) + D_sigma(alpha)(X_S-mu_S)`.

Hence

- target mean: `c_S + D_mu(alpha)(mu_S-c_S)`;
- target covariance: `D_sigma(alpha) Sigma_SS D_sigma(alpha)`;
- non-target mean: `mu_K + B(post_mu_S-mu_S)`;
- non-target covariance: `Omega + B(post_Sigma_SS)B^T`;
- target/non-target cross-covariance: `B(post_Sigma_SS)`.

Baseline recovery requires `D_mu(0)=D_sigma(0)=I`. Exact knockout at the anchor requires `D_mu(1)=D_sigma(1)=0`.

The linked reference map uses `D_mu = D_sigma = diag(1-alpha_s)` and, in the manuscript simulation, `c_S=0`. Treat both choices as assumptions, not necessities.

Sensitivity maps:

- location-only: `D_sigma=I`;
- scale-only: `D_mu=I`;
- independently parameterised location-scale maps.

## 3. Bounded scales

For a symptom observed on `[L,U]`, use the winsorising measurement map `h(y)=min(U,max(L,y))` when bounded response is required.

For `Y~N(m,s^2)`, the expected clipped value is

`L Phi(a) + m[Phi(b)-Phi(a)] + s[phi(a)-phi(b)] + U[1-Phi(b)]`,

where `a=(L-m)/s` and `b=(U-m)/s`. If `s=0`, use `h(m)`.

This is a winsorised-normal expectation, not a truncated-normal likelihood.

## 4. Primitive operators and analytic procedures

### Virtual knockout (vKO)

Unit-dose state operator `alpha=1`. Exact vKO is a degenerate endpoint at the anchor under the linked reference map.

Do not retain a zero-variance target column and then standardise/re-estimate a full covariance matrix. If a post-vKO network is needed, distinguish:

- induced network on `V\\{j}`;
- topology-only deletion of incident edges;
- soft vKO with prespecified residual variance.

### Virtual knockdown (vKD)

Partial state perturbation `0<alpha<1`.

### Virtual dosage perturbation (vDP)

Evaluate `G_j(alpha)` over a prespecified dose grid. Under the unbounded linked Gaussian mean response,

`Delta mu_-j^(alpha) = -alpha Sigma_-j,j sigma_jj^{-1} mu_j`

and therefore `G_j(alpha)=alpha G_j(1)`. Boundary effects or nonlinear mappings can break this equivalence.

### Edge-level communication blocking

For edge `(u,v)` and block fraction `q`:

`W_uv^(q) = W - q w_uv(e_u e_v^T + e_v e_u^T)`.

### Node-centred communication blocking

Multiply every edge incident to target `j` by `(1-q)`.

The reference finite-step topology functional is

`Q_T(W) = 1^T [sum_{t=1}^T (gamma |W|)^t] 1`.

Report `rho(gamma |W|)` and consider raw, row-normalised, and spectral-normalised adjacency matrices. When edge sign is scientifically meaningful, compare signed and unsigned functionals.

### Combination perturbation

For targets `j,k`, compare joint and single-target interventions on the **same outcome set** `V\\{j,k}`:

`I_jk = G_jk(1,1) - max{G_j^(-jk)(1), G_k^(-jk)(1)}`.

This is incremental pair value beyond the better single target, not causal additive synergy. Confirmatory analyses should preserve signed `I_jk` values.

### Sequence optimisation

For ordered sequence `pi=(pi_1,...,pi_L)` and `S_t={pi_1,...,pi_t}`:

`J(pi) = sum_t eta^(t-1)[G(S_t)-G(S_{t-1})] - lambda_c sum_t c_pi_t`.

The order is created by this decision objective, feasibility constraints, discounting, and costs. It is not biological or temporal direction identified from a cross-sectional GGM.

## 5. Estimands and seven utilities

For target `j` and dose `alpha`, define standardised improvement in non-target symptom `i`:

`Delta_i<-j^(alpha) = [E h(X_i) - E h(X_i^(j,alpha))] / sqrt(Sigma_hat_ii,lambda)`.

Keep three estimands distinct:

- direct target benefit;
- beneficial downstream spillover;
- adverse downstream spillover.

Let `G_j(alpha)` be the weighted mean downstream improvement over the prespecified non-target outcome set.

Seven utility outcomes, all oriented so larger is better:

1. **Efficacy:** `R_eff = G_j(1)`.
2. **Dose efficiency:** mean of `G_j(alpha_k)/alpha_k` over prespecified partial doses.
3. **Breadth:** share of non-target symptoms with `Delta >= tau`.
4. **Cross-module reach:** share of other modules with mean improvement `>= tau_m`.
5. **Communication block:** `[Q_T(W)-Q_T(W_j^block)] / Q_T(W)`.
6. **Combination value:** target-level aggregation of pair incremental values. Use signed averaging for confirmatory work; positive-part averaging only for historical exploratory compatibility.
7. **Responsiveness:** `[G_j(epsilon)-G_j(0)]/epsilon`.

## 6. VPPS

Normalize each raw utility `R_jm` across the prespecified candidate targets by min-max scaling to `0-100`. If a dimension is constant, assign a neutral score of `50`.

The confirmatory VPPS is the weighted mean of the **seven utility dimensions**. The reference methodological analysis uses equal weights. Clinical applications should pre-specify weights from patient priorities, feasibility, safety, and decision-analytic considerations.

VPPS is a relative within-candidate-set ranking. Do not compare it across candidate sets, cohorts, or networks as a transportable clinical utility score.

## 7. Robustness and bootstrap

Robustness is an uncertainty diagnostic and is not included in confirmatory VPPS.

Reference sensitivity scenarios vary ridge regularisation, breadth threshold, module threshold, propagation decay, block fraction, and combination partner-set size. Convert the target's rank standard deviation across scenarios to a normalized robustness diagnostic if desired, but always retain the scenario rank profile.

For applied analyses, perform a complete-pipeline bootstrap: resample participants and repeat network estimation, thresholding, perturbation, outcome calculation, candidate-set normalization, and ranking in every replicate. Report uncertainty intervals, rank distributions, and top-k selection probabilities.

## 8. Reference defaults from the manuscript

- Ridge `lambda = 0.02`
- Topology edge threshold `tau_W = 0.03`
- Symptom bounds `[0,4]` in the reference simulation
- Dose grid `{0, 0.10, 0.25, 0.50, 0.75, 1}`
- Dose-efficiency doses `{0.25,0.50,0.75}`
- Breadth threshold `tau=0.10 SD`
- Module threshold `tau_m=0.20 SD`
- Responsiveness `epsilon=0.10`
- Node block fraction `q=0.80`
- Propagation steps `T=6`
- Propagation decay `gamma=0.45`
- Combination partner set: five highest-efficacy alternatives in the reference implementation
