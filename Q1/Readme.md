## CKD Stage Transition Analysis
This script analyzes how patients move through different stages of **Chronic Kidney Disease (CKD)** over time.

### Usage:
``` python
python Q1.py
```
### Results:
| FROM     | TO       | count | mean   | median |
|----------|----------|-------|--------|--------|
| Stage 1  | Stage 2  | 5     | 2973.6 | 966.0  |
| Stage 2  | Stage 3  | 4     | 3368.75| 2523.5 |
| Stage 3  | Stage 4  | 1     | 238.0  | 238.0  |

### Code details:

1. **Load the Data**
   Start by loading two files:
   * `conditions.csv` → has medical condition records.
   * `patients.csv` → has patient info like names.

2. **Find CKD Diagnoses**
  Look through all the condition descriptions to find anything that mentions a CKD stage (like *"Stage 3"* or *"End-stage renal disease"*).
   These are filtered out for further analysis. \
Note: ICD codes where not found in the data so went with descriptions.

3. **Extract CKD Stage Info**
   From the descriptions, pull out the exact stage using regex.
   So, if the description says "Chronic kidney disease stage 4", it tags that row as `"Stage 4"`.

4. **Sorting the Data by Patient and Time**
   For each patient, sorting the CKD records by date, so we can see how their condition progressed over time.

5. **Tracking Stage Progression**
   For every patient:

   * Record the **first time** each CKD stage appears.
   * Then checks how long it took for the patient to go from one stage to the next.

6. **Building a Transitions Table**
   Creates a table showing:
   * Which patient went from which stage to which
   * And how many days it took between those two stages

7. **Adding Patient Names**
   Join the patient table so that the output shows actual names instead of just IDs.

8. **Summarizing the Transitions**
   Group the transitions by stage (like Stage 3 → Stage 4), and calculate:

   * How many people made that transition
   * The average time it took
   * The median time it took

9. **Visualization**
   * A **Sankey diagram**, which visually shows how patients flow from one stage to another.
