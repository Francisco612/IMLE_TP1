import pandas as pd
import argparse
import json
from datetime import timedelta


def load_zones(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f).get('zones', {})
    except FileNotFoundError:
        return {}


def process_events(events_df, zones_data):
    events_df['timestamp'] = pd.to_datetime(events_df['timestamp'])
    events_df = events_df.sort_values('timestamp')

    active_persons = []  # Pessoas atualmente ativas na loja
    completed_journeys = []  # Visitas a zonas concluídas
    person_counter = 1

    for _, row in events_df.iterrows():
        ts = row['timestamp']
        zone = row['zone_id']
        evt_type = row['event_type']
        gender = row['gender']
        age = row['age_range']

        matched_person = None

        if evt_type == 'entry':
            # Procurar pessoa ativa que possa ter entrado nesta zona
            for p in active_persons:
                if p['gender'] == gender and p['age_range'] == age and p['current_zone'] is None:
                    time_since_last = (ts - p['last_exit_time']).total_seconds()

                    # Heurística: gap máximo de 5 minutos (300 segundos)
                    if time_since_last < 300:
                        # Opcional: Verificar tempos de caminhada no zones.json
                        walk_time = 0
                        if p['last_zone'] in zones_data and zone in zones_data[p['last_zone']].get('walk_seconds', {}):
                            walk_time = zones_data[p['last_zone']]['walk_seconds'][zone]

                        if time_since_last >= walk_time:
                            matched_person = p
                            break

            if not matched_person:
                # Criar nova pessoa
                matched_person = {
                    'person_id': f"P_{person_counter:04d}",
                    'gender': gender,
                    'age_range': age,
                    'current_zone': None,
                    'last_zone': None,
                    'last_exit_time': ts
                }
                person_counter += 1
                active_persons.append(matched_person)

            # Iniciar visita à zona
            matched_person['current_zone'] = zone
            matched_person['current_entry_time'] = ts
            matched_person['current_dwell'] = 0

        elif evt_type == 'linger':
            # Atribuir o dwell tempo à pessoa que está atualmente nesta zona
            for p in active_persons:
                if p['current_zone'] == zone and p['gender'] == gender and p['age_range'] == age:
                    p['current_dwell'] += row['duration_s']
                    break

        elif evt_type == 'exit':
            # Fechar a visita na zona
            for p in active_persons:
                if p['current_zone'] == zone and p['gender'] == gender and p['age_range'] == age:
                    completed_journeys.append({
                        'person_id': p['person_id'],
                        'zone_id': zone,
                        'entry_time': p['current_entry_time'],
                        'exit_time': ts,
                        'dwell_s': p['current_dwell'],
                        'gender': gender,
                        'age_range': age,
                        'visit_date': ts.date(),
                        'hour_of_day': ts.hour
                    })
                    p['current_zone'] = None
                    p['last_zone'] = zone
                    p['last_exit_time'] = ts
                    break

    return pd.DataFrame(completed_journeys)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    zones = load_zones('data/zones.json')

    journeys_df = process_events(df, zones)
    journeys_df.to_csv(args.output, index=False)
    print(f"✅ Stitching concluído! {len(journeys_df)} visitas a zonas reconstruídas.")