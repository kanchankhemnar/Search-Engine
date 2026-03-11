import numpy as np
import ast

def extract_scheme_ids(results):

    return [r["_source"]["scheme_id"] for r in results]


def evaluate_system(df, search_function):

    top1, top3, top5, top10, mrr, precision = [], [], [], [], [], []

    for _, row in df.iterrows():

        query = row["query"]
        correct_ids = ast.literal_eval(row["relevant_scheme_ids"])

        results = search_function(query)
        pred_ids = extract_scheme_ids(results)

        top1.append(any(cid in pred_ids[:1] for cid in correct_ids))
        top3.append(any(cid in pred_ids[:3] for cid in correct_ids))
        top5.append(any(cid in pred_ids[:5] for cid in correct_ids))
        top10.append(any(cid in pred_ids[:10] for cid in correct_ids))

        rr = 0
        for i, pid in enumerate(pred_ids):
            if pid in correct_ids:
                rr = 1/(i+1)
                break

        mrr.append(rr)

        precision.append(
            sum(1 for pid in pred_ids[:3] if pid in correct_ids) / 3
        )

    return {
        "Top-1 Accuracy": np.mean(top1),
        "Top-3 Accuracy": np.mean(top3),
        "Top-5 Accuracy": np.mean(top5),
        "Top-10 Accuracy": np.mean(top10),
        "MRR": np.mean(mrr),
        "Precision@3": np.mean(precision)
    }