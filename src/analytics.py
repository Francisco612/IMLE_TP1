# src/analytics.py
import pandas as pd
import argparse
import json
import numpy as np


def calculate_metrics(df):
    metrics = {}
    df['entry_time'] = pd.to_datetime(df['entry_time'])
    df['visit_date'] = pd.to_datetime(df['visit_date'])

    # 1. Métricas de Tráfego
    metrics['trafego_total_unicos'] = int(df['person_id'].nunique())
    metrics['visitantes_por_dia'] = df.groupby(df['visit_date'].dt.strftime('%Y-%m-%d'))[
        'person_id'].nunique().to_dict()
    metrics['visitantes_por_hora'] = df.groupby('hour_of_day')['person_id'].nunique().to_dict()

    # Tempo médio de visita à loja por pessoa
    visit_durations = df.groupby('person_id').apply(
        lambda x: (pd.to_datetime(x['exit_time'].max()) - pd.to_datetime(x['entry_time'].min())).total_seconds() / 60
    )
    metrics['tempo_medio_loja_minutos'] = round(visit_durations.mean(), 2)

    # 2. Métricas por Zona
    zone_traffic = df.groupby('zone_id')['person_id'].nunique()
    zone_dwell = df[df['dwell_s'] > 0].groupby('zone_id')['dwell_s'].mean()

    metrics['zonas'] = {}
    for zone in zone_traffic.index:
        metrics['zonas'][zone] = {
            'visitantes_unicos': int(zone_traffic.get(zone, 0)),
            'dwell_medio_s': round(zone_dwell.get(zone, 0), 2)
        }

    # 3. Funil de Cliente
    checkout_zones = ['Z_C1', 'Z_C2', 'Z_C3', 'Z_CK']
    chegaram_caixa = df[df['zone_id'].isin(checkout_zones)]['person_id'].unique()
    total_pessoas = df['person_id'].unique()

    metrics['funil'] = {
        'taxa_conversao_caixa_perc': round((len(chegaram_caixa) / len(total_pessoas)) * 100, 2),
        'perfil_nao_converteram': df[~df['person_id'].isin(chegaram_caixa)]['age_range'].value_counts().to_dict()
    }

    # 4. Deteção de Anomalias (Dia 7 vs Dias 1-6)
    dias_ordenados = sorted(df['visit_date'].dt.date.unique())
    if len(dias_ordenados) >= 7:
        dia_7 = dias_ordenados[6]
        dias_1_a_6 = dias_ordenados[:6]

        anomalias = []
        for zone in df['zone_id'].unique():
            for hour in range(9, 22):
                # Tráfego histórico
                hist_data = df[
                    (df['zone_id'] == zone) & (df['hour_of_day'] == hour) & (df['visit_date'].dt.date.isin(dias_1_a_6))]
                historico = hist_data.groupby(hist_data['visit_date'].dt.date)['person_id'].nunique()

                media = historico.mean() if not historico.empty else 0

                # Tráfego dia 7
                dia7_data = df[
                    (df['zone_id'] == zone) & (df['hour_of_day'] == hour) & (df['visit_date'].dt.date == dia_7)]
                trafego_dia7 = dia7_data['person_id'].nunique()

                # Desvio superior a 20%
                if media > 5 and abs(trafego_dia7 - media) > (0.20 * media):
                    anomalias.append({
                        'zona': zone,
                        'hora': hour,
                        'media_esperada': round(media, 1),
                        'observado_dia7': int(trafego_dia7),
                        'desvio_perc': round(((trafego_dia7 - media) / media) * 100, 2)
                    })
        metrics['anomalias_dia_7'] = anomalias

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
    print("✅ Analytics concluído! Ficheiro metrics.json gerado.")