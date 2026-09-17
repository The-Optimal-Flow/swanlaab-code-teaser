# Demo · Claude Code teaser (sanitized)

Repo de demostración para la sesión Swanlaab (17 sep 2026).

**Qué es:** un ejemplo mínimo y público de cómo un equipo puede dejar un artefacto versionado (README + script) listo para iterar con Claude Code / agentes.

**Qué no es:** no contiene datos de la firma, deals, LPs ni secretos. Los números del CSV son inventados.

## Uso rápido

```bash
python3 summarize_portfolio.py
```

Dos salidas desde el mismo CSV:

1. **Terminal** — el resumen de 4 líneas: participadas, ARR agregado, crecimiento MoM medio y cuáles están en watch.
2. **`portfolio_report.html`** — un dashboard para proyectar: los KPIs, dos gráficos (ARR por participada y crecimiento MoM sobre el cero) y la tabla de detalle. Para abrirlo:

```bash
open portfolio_report.html      # macOS
xdg-open portfolio_report.html  # Linux
```

El HTML es un artefacto generado y no se versiona (está en `.gitignore`). La fuente de verdad es `sample_portfolio.csv`: cambia el CSV, vuelve a ejecutar el script y la página se regenera entera.

## Frontera útil

- **Claude (chat / Project):** redactar, cruzar cifras, preparar el memo.
- **Claude Code + GitHub:** versionar el script, el CSV y el prompt que lo genera.
- **Vercel (opcional):** publicar un front mínimo si el artefacto es una app.

Si Code interesa de verdad, mejor una sesión aparte que forzarlo en los últimos minutos.
