# 7. Machine learning

## The question

"Which accounts are likely to cancel?" A general churn rate (18.6%) does not
tell customer success who to call. A **model** gives each account a risk
score, so the team can start with the riskiest.

## What machine learning means here

You show an algorithm many past examples (accounts, with facts about each, and
whether they eventually churned). It finds patterns linking the facts to the
outcome. Then you give it an account it has not seen and ask for a guess.

No magic. It is pattern-finding on past data, and it is only as good as the
data and the honesty of the test.

## The pieces

**The label** (what we predict): `churned`, 1 if the account cancelled, else 0.

**The features** (facts we give the model), in
[`ml/features.py`](../../ml/features.py):

| Feature | Meaning |
|---|---|
| `plan_tier`, `industry`, `region` | Who the customer is |
| `current_seat_count` | How big the account is |
| `distinct_feature_types_used` | How many parts of the product they use |
| `total_events_90d` | How active they have been recently |
| `days_since_last_login` | How long since anyone logged in |

Notice these are about **behaviour**, not just who they are. An account's
health depends on how deeply it uses the product.

**The algorithm:** `GradientBoostingClassifier`, a method that builds many
small decision rules one after another, each correcting the last one's
mistakes. You do not need the maths. Say "a tree-based model that is good at
tabular data".

## Train and test: never grade on what it studied

The most important rule in machine learning. If you test the model on the same
accounts it learned from, it can just memorize them and look perfect.

So the data is split in two, in
[`ml/train_churn_model.py`](../../ml/train_churn_model.py):

- **Training set:** 374 accounts (75%). The model learns from these.
- **Test set:** 125 accounts (25%). Held back, only used to grade.

`random_state=42` fixes the split so it is the same every run, and `stratify`
keeps the churn share the same in both parts (about 18.5% each).

## Judging it: why not just accuracy?

Only 18.6% of accounts churn. A model that says "nobody will ever churn" is
right **81.4%** of the time and completely useless. So accuracy is the wrong
scoreboard for lopsided data. The project reports better ones:

**AUC** (area under the curve). Picture picking one account that churned and
one that did not, at random. AUC is how often the model gives the churner the
higher risk score. 0.5 means a coin flip. 1.0 means perfect. This model:
**0.6675**. Better than chance, but modest.

**Precision.** Of the accounts the model **flags** as risky, how many really
churned? 45.5%.

**Recall.** Of all the accounts that really churned, how many did the model
catch? 21.7%.

In the 125-account test set there were about 23 real churners. Those two
numbers work out to: the model flagged 11 accounts, 5 of them really churned,
and it missed the other 18. Say that in plain words: **it is a rough way to
rank accounts, not a crystal ball.**

## Why the score wobbles

Only 23 churners are in the test set. That is few, so which accounts land in
it matters a lot. Train the identical model with four different random splits
and the AUC comes out:

| Split seed | AUC |
|---|---|
| 1 | 0.573 |
| 7 | 0.656 |
| 42 (the project's) | 0.668 |
| 99 | 0.691 |

The number is exactly reproducible (fixed seeds), but it is **fragile**: a
different split moves it from 0.57 to 0.69. Any honest report says "about
0.6 to 0.7, modest, from a small test set", not just "0.6675".

## Known limitations

The code's own comments flag the biggest one. The features are measured up to
one fixed date for **every** account. But an account that has already churned
stopped logging in, so a long `days_since_last_login` is partly a **result** of
leaving, not an early warning of it. This is called **leakage**: information
from after the outcome sneaking into the features. A careful version measures
each account's features as of a cutoff date **before** it churned. This is a
demo dataset, so it is documented and left as is, and you should be ready to
explain it.

Other honest limits: the data is fake, the model has no idea about things like
pricing changes or support problems, and 499 accounts is small.

## What the model is for

The dashboard's Account Risk tab scores every **active** account and lists the
riskiest. The right use: give customer success a **starting order** for
outreach. The wrong use: treating any single score as a certainty about a
customer.

## Try it

Train the model and read the scores:

```bash
python -m ml.train_churn_model
```

You should see `"auc": 0.6675`, precision 0.4545 and recall 0.2174.

Check the "useless model" idea yourself:

```bash
python - <<'PY'
from ml.features import build_feature_frame, TARGET_COLUMN
df = build_feature_frame()
print("churn rate:", round(df[TARGET_COLUMN].mean(), 3))
print("accuracy of always guessing 'no churn':", round(1 - df[TARGET_COLUMN].mean(), 3))
PY
```

Then see the wobble for yourself:

```bash
python - <<'PY'
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
from ml.features import build_feature_frame, FEATURE_COLUMNS, TARGET_COLUMN
from ml.train_churn_model import build_pipeline

df = build_feature_frame()
X, y = df[FEATURE_COLUMNS], df[TARGET_COLUMN]
for seed in (1, 7, 42, 99):
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.25, random_state=seed, stratify=y)
    model = build_pipeline().fit(Xtr, ytr)
    print(seed, round(roc_auc_score(yte, model.predict_proba(Xte)[:, 1]), 3))
PY
```

You should get 0.573, 0.656, 0.668, 0.691.

**Your own task:** which feature do you think matters most for churn? Write
down a guess, then check. Run this:

```bash
python - <<'PY'
from sklearn.model_selection import train_test_split
from ml.features import build_feature_frame, FEATURE_COLUMNS, TARGET_COLUMN
from ml.train_churn_model import build_pipeline

df = build_feature_frame()
X, y = df[FEATURE_COLUMNS], df[TARGET_COLUMN]
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)
model = build_pipeline().fit(Xtr, ytr)

names = model.named_steps["preprocess"].get_feature_names_out()
importance = model.named_steps["classify"].feature_importances_
for name, value in sorted(zip(names, importance), key=lambda t: -t[1])[:5]:
    print(name, round(value, 3))
PY
```

With this seed-42 split, the top features are recent activity
(`total_events_90d`, about 0.30) and days since last login (about 0.19),
followed by seat count and plan tier. Usage beats who the customer is, which
matches the reasoning in the feature list. Notice that `days_since_last_login`
is the leakage suspect described above, so the second-ranked feature is
also the one to be careful about.

## Check yourself

- Why is the test set kept separate from the training set?
- Why is 81% accuracy meaningless here?
- What do precision and recall each tell you?
- What is leakage, and where might it be in this model?
- Why should you say "0.6 to 0.7" and not just "0.6675"?
