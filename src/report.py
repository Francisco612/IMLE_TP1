import argparse
import json


def generate_markdown(insights_data):
    md = "# Briefing Semanal - Inteligência Operacional de Loja\n\n"

    # 1. Resumo Executivo
    md += "## 1. Resumo Executivo\n"
    for bullet in insights_data.get('resumo_executivo', []):
        md += f"- {bullet}\n"

    # 2. Insights e Recomendações
    md += "\n## 2. Insights Operacionais\n"
    for ins in insights_data.get('insights', []):
        urgencia_icone = "🔴" if ins.get('urgencia', '').lower() == 'imediata' else "🟡"

        md += f"### {urgencia_icone} {ins.get('titulo', 'Insight')} (Categoria: {ins.get('categoria', 'Geral').capitalize()})\n"
        md += f"**O que os dados mostram:** {ins.get('observacao', '')}\n\n"
        md += f"**Impacto Operacional:** {ins.get('implicacao', '')}\n\n"
        md += f"**Acção Recomendada:** {ins.get('recomendacao', '')}\n\n"
        md += f"> *Nível de Confiança da IA: {float(ins.get('confianca', 0)) * 100}% | Urgência: {ins.get('urgencia', '').upper()}*\n\n"
        md += "---\n\n"

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
    print(f"✅ Relatório Semanal pronto! Verifica o ficheiro {args.output}")