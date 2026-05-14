import argparse
import json
import ollama
import sys
import os


def load_prompt(strategy):
    """Lê o prompt do ficheiro correspondente à estratégia escolhida."""
    if strategy.upper() == 'A':
        filepath = 'prompts/prompt_zero_shot.txt'
    else:
        filepath = 'prompts/prompt_few_shot.txt'

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Erro: Não foi possível encontrar o ficheiro de prompt em {filepath}")
        sys.exit(1)


def generate_insights(metrics, strategy):
    system_prompt = load_prompt(strategy)
    user_prompt = f"Métricas calculadas do pipeline Python: {json.dumps(metrics)}"

    print(f"A invocar o Llama3.1 usando a Estratégia {strategy.upper()}...")
    try:
        response = ollama.chat(
            model='llama3.1:8b',
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}
            ],
            format='json',
            options={'temperature': 0}  # Garante reprodutibilidade como pedido
        )
        return json.loads(response['message']['content'])
    except Exception as e:
        print(f"Erro a contactar o Ollama: {e}")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True, help="Path do metrics.json")
    parser.add_argument('--output', required=True, help="Path do output insights.json")
    parser.add_argument('--strategy', default='B', choices=['A', 'B', 'a', 'b'],
                        help="Estratégia de prompting: A (Zero-shot) ou B (Few-shot)")
    args = parser.parse_args()

    with open(args.input, 'r', encoding='utf-8') as f:
        metrics = json.load(f)

    insights_json = generate_insights(metrics, args.strategy)

    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(insights_json, f, indent=4, ensure_ascii=False)
    print(f"✅ Insights gerados com sucesso usando a Estratégia {args.strategy.upper()}!")