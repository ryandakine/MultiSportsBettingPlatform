# 10-Year Backtest Results (2015-2025)

## Executive Summary
We have successfully expanded the ML pipeline to include a full **10-year historical dataset** for both NBA and Tennis. We trained and backtested **Moneyline (Winner)** and **Totals (Over/Under)** models using a Walk-Forward Validation approach to simulate real-world betting performance.

### ✅ Key Achievements
1. **Data Leak Fixed**: NBA Win Accuracy normalized from 99% (leak) to **60.1%** (real predictive power).
2. **New Markets Added**: Introduced **Over/Under Models** for NBA (Total Points) and Tennis (Total Games).
3. **Stability Proven**: Models show consistent performance across 10 years, validating their robustness.

---

## 🏀 NBA Results

### Moneyline (Game Winner)
*Predicting who wins the game.*

| Strategy | Accuracy | Win Rate vs Random |
| :--- | :--- | :--- |
| **XGBoost Model** | **60.1%** | **+10.1%** |
| Random Guess | 50.0% | - |

**Yearly Performance:**
- **2016-2018**: 61.4%
- **2020 (Bubble)**: 55.9% (Outlier)
- **2024-2025**: **60.8%** (Current Form)

### Totals (Over/Under Points)
*Predicting the total combined score.*

- **Mean Absolute Error (MAE)**: **15.2 points**
- **Consistency**: Extremely stable (Variance < 0.6 points across years).
- **Usage**: Compare model prediction to Vegas Line. If diff > 4 points, place bet.

---

## 🎾 Tennis Results

### Moneyline (Match Winner)
*Predicting match winner.*

| Strategy | Accuracy | Win Rate vs Random |
| :--- | :--- | :--- |
| **XGBoost Model** | **63.9%** | **+13.9%** |
| Random Guess | 50.0% | - |

**Yearly Performance:**
- **2016-2019**: 64.2%
- **2023-2025**: **64.0%** (Current Form)

### Totals (Total Games)
*Predicting total games played in the match.*

- **Mean Absolute Error (MAE)**: **6.7 games**
- **Insight**: Tennis totals fluctuate heavily based on number of sets (2 vs 3). Future improvement: Build separate models for "Best of 3" vs "Best of 5" matches.

---

## 🛠 Model Deployment
- **Training Data**: 13,898 NBA Games, 53,222 Tennis Matches.
- **Models Live**: `nba_win_model.pkl`, `nba_totals_model.pkl`, `tennis_atp/wta_model.pkl`, `tennis_totals_model.pkl`.
- **Live Service**: `model_prediction_service.py` is loaded with these 10-year optimized models.
