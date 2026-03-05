# Research Report

Momentum Variations
Andrew Hall, Brandon Waits, Grant Rich
3/5/26

---

## 1. Summary

This memo investigates two extensions to the standard momentum strategy currently implemented by Silver Fund: idiosyncratic momentum and volatility-scaled momentum. We evaluate idiosyncratic momentum signals constructed from four factor models—CAPM, Fama-French 3-Factor, Fama-French 5-Factor, and the Barra model—and find that signal performance improves monotonically with the explanatory power of the underlying factor model, with Barra idiosyncratic momentum achieving the highest Sharpe ratio among residual-based signals. We then apply volatility scaling to the top-performing signals and show that it improves risk-adjusted returns for both standard and idiosyncratic momentum. While standard volatility-scaled momentum achieves the highest full-sample Sharpe ratio, we demonstrate that volatility-scaled Barra idiosyncratic momentum exhibits substantially stronger performance during the COVID-19 crash period, consistent with its reduced exposure to systematic factor reversals. Based on these findings, we recommend replacing Silver Fund's current standard momentum signal with volatility-scaled Barra idiosyncratic momentum.

- Sources:

Blitz, D., Pang, H., & van Vliet, P. (2013). The idiosyncratic momentum anomaly. Journal of Business & Economic Statistics, 31(1), 44–56. https://doi.org/10.1080/07350015.2012.723155

---

Hanauer, M. X., & Lauterbach, R. (2023). Enhanced momentum strategies. Journal of Banking & Finance, 154, 106939. https://doi.org/10.1016/j.jbankfin.2023.106939

## 2. Data Requirements

Experiments require Barra and Fama-French data, all found within the Silver Fund data collection.
 
---

## 3. Approach / System Design

The economic intuition for the momentum anomaly has been extensively discussed within Silver Fund, specifically the underreaction hypothesis. In this memo, we focus on the rationale for idiosyncratic and volatility-scaled momentum. Standard momentum, as currently implemented by Silver Fund, uses total return momentum, implying that higher-momentum stocks may be high-momentum because the underlying factors they’re exposed to outperform. In reality, the underreaction hypothesis primarily concerns investors' underreaction to firm-specific information.  By using the idiosyncratic component, we can isolate this effect without incorporating unwanted factor risk. Furthermore, volatility scaling addresses the crash risk of standard momentum while limiting the strategy to selecting stocks solely on the basis of high volatility. 

In calculating the idiosyncratic component, we consider the four different factor models familiar to Silver Fund. These factor models are the Capital Asset Pricing Model, Fama-French 3-Factor Model, Fama-French 5-Factor Model, and Barra Factor Model. 

In our research, we examined the performance of idiosyncratic momentum across these factor models. We recognized that using a residual from a factor model with fewer factors would inherently trade momentum on the excluded factors. However, we didn’t know if that would ever be desired or if we should always use Barra. When consulting with Brandon, we received the following explanation for why the idiosyncratic component from Barra is superior:

Suppose the true model of returns is $r_{it} = \sum_{j=1}^{k} \beta_{ij}f_{jt} + e_{it}$. So, you have $k + 1$ things you could forecast if you knew the true model. Suppose there are $Q$ possible actual factor models to choose from to estimate and you choose model $q$. Suppose your proposed factor model is $r_{it} = \sum_{j=1}^{m^q} \gamma_{ij}^q g_{jt}^q + u_{it}^q$, giving you a maximum of $m^q + 1$ things to actually forecast. You can create a momentum signal on those $m^q + 1$ individually or any version of $\sum_{j \in J} \gamma_{ij}^q g_{jt}^q + u_{it}^q$, where $J$ is the set of all subsets of natural numbers up to $m^q$ and including or excluding the "idiosyncratic" term, $u^q$. The cleanest version is computing [signal] separately on each factor and on the idiosyncratic term. Computing [signal] on any of the subsets assumes that the loadings $g^q$ are the same as the optimal signal weights you would have used to combine the signals computed on each component separately, which is weakly suboptimal. The next point is which $q \in Q$ to pick. Pick the one that best explains the contemporaneous cross-section of returns, which is Barra.

The signal construction process begins with standard Momentum, which is calculated by taking daily log returns, applying a 230-day rolling sum for each stock, and shifting the result by 21 days to create a $t_{12} - t_{2}$ time period. To extract the idiosyncratic portion for subsequent signals (excluding Barra), a rolling OLS regression is performed using a desired factor model such as CAPM, FF3, or FF5 to generate beta coefficients. For Idiosyncratic Momentum (CAPM, FF3, FF5), these coefficients are used to subtract the predicted factor returns from each stock’s excess return, followed by the standard momentum calculation on the remaining values. Idiosyncratic Momentum (Barra) is constructed by taking the daily log of the Barra-specific return for each stock and performing a 230-day rolling sum shifted by 21 days. Finally, Volatility Scaled Momentum follows the standard signal construction process but adds a step where each rolling return is divided by its rolling 230-day standard deviation before the 21-day shift is applied.

---

## 4. Code Structure

```text
sf-research-momentum/
├── research/
│   ├── experiments/
│   │   └── [All experiment files]
│   ├── signals/
│   │   └── [Signal construction images]
│   └── utils/
│       ├── __init__.py
│       ├── backtest.py
│       └── mvo.py
├── results/
│   └── [All experiment results files]
└── README.md
```

---

## 5. Performance Discussion

The experimental process begins by constraining portfolios to a zero beta relative to the market and ensuring portfolio weights sum to zero, while applying a $5 price filter prior to construction. For each signal, a gamma is selected to achieve approximately 5% active risk over the period from 1996-07-31 to 2024-12-31, with weights and forward returns then used to highlight performance across the full sample. Standard momentum is constructed by taking daily log returns, applying a 230-day rolling sum, and shifting by 21 days. Idiosyncratic momentum for CAPM, FF3, and FF5 requires a rolling OLS regression to extract residuals by subtracting predicted factor returns from each stock's excess return, while the Barra version uses the daily log of specific returns. Volatility-scaled momentum adds a step of dividing each rolling return by its rolling 230-day standard deviation. Analysis of non-volatility-scaled signals shows that while standard momentum has the highest Sharpe ratio, increasing the number of factors in idiosyncratic models—culminating in the Barra model—improves the strategy's Sharpe ratio. Although volatility scaling improves performance for both standard and Barra idiosyncratic signals, standard momentum maintains a higher Sharpe ratio in the full sample. However, the idiosyncratic momentum strategy is shown to be preferable because it is less affected by market crashes, as evidenced by its significantly higher Sharpe ratio during the COVID-19 sample period from 2019-01-01 to 2022-12-31.

In conclusion, we find that signal performance improves monotonically with the explanatory power of the underlying factor model, volatility scaling improves all momentum variations, and idiosyncratic momentum outperforms standard momentum during the COVID-19 pandemic. Accordingly, we vote to replace the current standard momentum signal with volatility-scaled Barra idiosyncratic momentum in the Silver Fund portfolio.

---

## Appendix: Figures and Results

| Description | Visualization |
| :--- | :--- |
| **Figure 1:** Standard Momentum Signal | <img width="792" height="638" alt="Image" src="https://github.com/user-attachments/assets/744a6f5f-c1c6-4d36-9c22-c9a9fa16cb15" /> |
| **Figure 2:** Fama-French 3 Idiosyncratic Momentum | <img width="1154" height="1070" alt="Image" src="https://github.com/user-attachments/assets/9dcabe23-dd38-43d3-82c1-e754429aa6cc" /> |
| **Figure 3:** Barra Idiosyncratic Momentum | <img width="1120" height="638" alt="Image" src="https://github.com/user-attachments/assets/3b82a6da-b8c4-4724-a0a1-3d9516c73457" /> |
| **Figure 4:** Volatility-Scaled Momentum | <img width="1198" height="692" alt="Image" src="https://github.com/user-attachments/assets/cf68284b-512b-46d2-90c4-21b9cb0ce1d6" /> |

### Full Sample Backtests (Non-Volatility Scaled)
| Chart | Data Table |
| :---: | :---: |
| <img width="1966" height="926" alt="Image" src="https://github.com/user-attachments/assets/38db8f2a-8a83-47da-b165-b7ab2e4250d9" /> | <img width="786" height="516" alt="Image" src="https://github.com/user-attachments/assets/3288f91f-9624-48ba-9920-69a69160762c" /> |
| *Figure 5: Full Sample Active Backtest Chart* | *Figure 6: Full Sample Active Backtest Table* |

### Volatility-Scaled & COVID-19 Analysis
| Analysis Type | Chart | Table |
| :--- | :---: | :---: |
| **Full Sample (Scaled)** | <img width="1999" height="903" alt="Image" src="https://github.com/user-attachments/assets/72cf9e4a-bf0e-4f47-84db-be289e81ea8c" /> | <img width="952" height="308" alt="Image" src="https://github.com/user-attachments/assets/eedd81ea-999e-4692-bb32-f0d6eaa42bce" /> |
| **COVID-19 Period** | <img width="1999" height="913" alt="Image" src="https://github.com/user-attachments/assets/e591b4f6-c813-4e0f-abf0-77e4e17404e2" /> | <img width="956" height="306" alt="Image" src="https://github.com/user-attachments/assets/0bd9e85b-d10b-4102-8bc6-40cf142effdc" /> |