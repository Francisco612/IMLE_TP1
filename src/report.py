import argparse
import json


def generate_markdown(insights_data):
    md = "# Briefing Semanal - Inteligência de Loja\n\n"

    md += "## 1. Resumo Executivo\n"
    for bullet in insights_data.get('resumo_executivo', []):
        md += f"- {bullet}\n"

    md += "\n## 2. Insights e Recomendações\n"
    for ins in insights_data.get('insights', []):
        md += f"### {ins['titulo']} ({ins['categoria']})\n"
        md += f"- **Observação:** {ins['observacao']}\n"
        md += f"- **Implicação:** {ins['implicacao']}\n"
        md += f"- **Recomendação:** {ins['recomendacao']} (Urgência: {ins['urgencia']})\n"

    return md


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()

    with open(args.input, 'r', encoding='utf-8') as f:
        data = json.load(f)

    markdown_content = generate_markdown(data)

    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(markdown_content)