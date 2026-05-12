import pandas as pd
import argparse
from datetime import timedelta


def process_events(events_df):
    events_df['timestamp'] = pd.to_datetime(events_df['timestamp'])
    events_df = events_df.sort_values('timestamp')

    active_trajectories = []
    completed_journeys = []
    person_counter = 1

    # Heurística simplificada: Associação Gulosa (Greedy)
    for _, row in events_df.iterrows():
        matched = False

        for traj in active_trajectories:
            # Condições de associação (atributos consistentes e tempo < 5 min)
            time_diff = row['timestamp'] - traj['last_timestamp']

            if (row['gender'] == traj['gender'] and
                    row['age_range'] == traj['age_range'] and
                    time_diff < timedelta(minutes=5)):
                traj['events'].append(row)
                traj['last_timestamp'] = row['timestamp']
                matched = True
                break

        if not matched:
            # Criar novo person_id
            person_id = f"P_{person_counter:04d}"
            person_counter += 1
            active_trajectories.append({
                'person_id': person_id,
                'gender': row['gender'],
                'age_range': row['age_range'],
                'last_timestamp': row['timestamp'],
                'events': [row]
            })

    # Processar trajetórias em formato final (zone_id, entry_time, exit_time, etc.)
    # ATENÇÃO: processar a lista de eventos de cada pessoa para calcular o tempo exato de entrada e saída por zona.
    output_data = []
    # ... (lógica de formatação para journeys.csv) ...

    return pd.DataFrame(output_data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    journeys_df = process_events(df)
    journeys_df.to_csv(args.output, index=False)