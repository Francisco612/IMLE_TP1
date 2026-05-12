import pandas as pd
import argparse
import json


def calculate_metrics(journeys_df):
    metrics = {}

    # Exemplo 1: Tráfego total único
    metrics["total_unique_visitors"] = int(journeys_df['person_id'].nunique())

    # Exemplo 2: Visitantes que chegaram às zonas de checkout
    checkout_zones = ['Z_C1', 'Z_C2', 'Z_C3', 'Z_CK']
    checkout_visitors = journeys_df[journeys_df['zone_id'].isin(checkout_zones)]['person_id'].nunique()
    metrics["checkout_conversion_rate"] = checkout_visitors / metrics["total_unique_visitors"]

    # implementar as restantes


    return metrics


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    metrics_data = calculate_metrics(df)

    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(metrics_data, f, indent=4, ensure_ascii=False)