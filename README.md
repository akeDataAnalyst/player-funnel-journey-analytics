# Player Funnel & Journey Analytics

End-to-end analytics pipeline for mobile/casual game player funnel, conversion drop-offs, cohort retention, and behavioral clustering.


## Project Highlights

- Realistic synthetic 50,000-player dataset  
- Full funnel visualization (install → D30 retention)  
- Cohort retention heatmaps & curves (D1/D7/D30)  
- K-Means clustering → 5 player personas  
- Interactive Streamlit dashboard combining funnel + cohorts + personas

## Business Problem & Key Findings

**Core question**  
Where do players drop off in the journey, how does retention decay over time, and who are the most valuable player types?

### Funnel Overview (50,000 installs)

| Stage                  | Players   | Conversion % | Drop-off % | Notes                                      |
|------------------------|-----------|--------------|------------|--------------------------------------------|
| Install                | 50,000    | 100.0%       | 8.2%       | Starting point                             |
| Registered             | 45,905    | 91.8%        | 28.2%      | Excellent early conversion                 |
| Tutorial Completed     | 35,902    | 71.8%        | 53.7%      | Solid but significant loss                 |
| First Game Played      | 23,168    | 46.3%        | 98.4%      | Biggest leak (53.7% drop-off)              |
| First Purchase         | 811       | 1.6%         | 79.5%      | Typical F2P conversion                     |
| D1 Return              | 10,228    | 20.5%        | 89.8%      | Decent Day 1 stickiness                    |
| D7 Return              | 5,077     | 10.2%        | 95.8%      | Mid-tier casual benchmark                  |
| D30 Return             | 2,079     | 4.2%         | —          | Typical long-term retention                |

### Cohort Retention Summary (Jan–Feb 2023 cohorts)

| Cohort Month | Cohort Size | D1 Return       | D7 Return       | D30 Return      |
|--------------|-------------|-----------------|-----------------|-----------------|
| 2023-01      | 44,640      | 9,181 (20.6%)   | 4,555 (10.2%)   | 1,880 (4.2%)    |
| 2023-02      | 5,360       | 1,047 (19.5%)   | 522 (9.7%)      | 199 (3.7%)      |

**Average across cohorts**  
- D1: 20.1%  
- D7: 10.0%  
- D30: 4.0%

### Player Personas (k=5 clustering)

| Cluster| Persona                     | Players  | Total Revenue | Key Traits                                            | Recommendation                                                                 |
|--------|-----------------------------|----------|---------------|-------------------------------------------------------|--------------------------------------------------------------------------------|
| 0      | Early Tutorial Drop-offs    | 19,583   | $0            | Complete tutorial but never play real game            | Fix tutorial → first game transition. Add instant reward. Reduce friction.     |
| 1      | Pre-Tutorial Churners       | 14,098   | $0            | Drop before or during tutorial                        | Simplify registration/login. Test play-without-account mode.                  |
| 2      | Non-Spending Loyalists      | 13,507   | $0            | Strong progression/retention but never spend          | Target conversion: soft IAP after 3–5 sessions, personalized packs.           |
| 3      | Long-term Free Players      | 2,002    | $0            | 100% D30 retention, no spending                       | High LTV potential. Test premium content, exclusive events, limited offers.   |
| 4      | Paying Core Players         | 810      | $7,327        | Highest revenue, 100% first purchase, good retention  | VIP segment. Protect with loyalty rewards, exclusive items, personalized events. |

**Biggest opportunities**  
- Reduce Tutorial → First Game drop-off (53.7%) → could add 6,000–7,000 active players  
- Convert Non-Spending Loyalists and Long-term Free Players → high retention base with zero revenue → biggest monetization upside  
- Protect Paying Core Players → they drive almost all revenue

## Tech Stack

- Python 3.10+
- pandas, numpy
- duckdb (SQL queries on dataframes)
- scikit-learn (K-Means clustering)
- plotly, seaborn, matplotlib (visualizations)
- Streamlit (interactive dashboard)
