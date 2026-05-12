import argparse
import json
import ollama


def generate_insights(metrics, strategy="few-shot"):
    # Lê os teus ficheiros de prompt
    # system_prompt = open(f"prompts/system_prompt_{strategy}.txt").read()

    system_prompt = """"""

    user_prompt = f"Aqui estão as métricas da loja: {json.dumps(metrics)}"

    response = ollama.chat(
        model='llama3.1:8b',
        messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt}
        ],
        format='json',  # Força a resposta estruturada
        options={'temperature': 0}  # Reprodutibilidade exigida
    )

    return json.loads(response['message']['content'])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()

    with open(args.input, 'r') as f:
        metrics = json.load(f)

    insights_json = generate_insights(metrics, strategy="few-shot")

    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(insights_json, f, indent=4, ensure_ascii=False)