#!/usr/bin/env python3
"""Resumen de cartera para el teaser de Swanlaab — datos ficticios.

Lee sample_portfolio.csv y produce dos salidas desde la misma fuente:
  1. un resumen en la terminal,
  2. portfolio_report.html, un dashboard listo para proyectar.
"""

from __future__ import annotations

import csv
from datetime import datetime
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CSV_PATH = ROOT / "sample_portfolio.csv"
HTML_PATH = ROOT / "portfolio_report.html"

STATUS_LABEL = {"on_track": "Según plan", "watch": "En seguimiento"}
STATUS_TONE = {"on_track": "good", "watch": "warn"}

MESES = ["ene", "feb", "mar", "abr", "may", "jun",
         "jul", "ago", "sep", "oct", "nov", "dic"]


def es_num(value: float, decimals: int = 0) -> str:
    """Formatea a convención es-ES: miles con '.', decimales con ','."""
    text = f"{value:,.{decimals}f}"
    return text.replace(",", "\x00").replace(".", ",").replace("\x00", ".")


def load_rows() -> list[dict]:
    rows = list(csv.DictReader(CSV_PATH.open(encoding="utf-8")))
    if not rows:
        raise SystemExit(f"{CSV_PATH.name} no tiene filas de datos.")
    for r in rows:
        r["arr_keur"] = float(r["arr_keur"])
        r["mom_growth_pct"] = float(r["mom_growth_pct"])
        r["ownership_pct"] = float(r["ownership_pct"])
    return rows


def summarize(rows: list[dict]) -> dict:
    watch = [r["company"] for r in rows if r["status"] == "watch"]
    return {
        "count": len(rows),
        "total_arr": sum(r["arr_keur"] for r in rows),
        "avg_growth": sum(r["mom_growth_pct"] for r in rows) / len(rows),
        "watch": watch,
    }


def print_summary(summary: dict) -> None:
    watch = summary["watch"]
    print(f"Participadas en muestra: {summary['count']}")
    print(f"ARR agregado (k€, inventado): {summary['total_arr']:.0f}")
    print(f"Crecimiento MoM medio: {summary['avg_growth']:.1f}%")
    print(f"En watch: {', '.join(watch) if watch else 'ninguna'}")


def _tooltip(r: dict) -> str:
    """Detalle de una participada, escapado para vivir en un atributo HTML."""
    return escape(
        f"<b>{r['company']}</b><br>{r['sector']} · {es_num(r['ownership_pct'], 1)} % en cartera"
        f"<br>ARR {es_num(r['arr_keur'])} k€ · MoM {es_num(r['mom_growth_pct'], 1)} %"
        f"<br>{STATUS_LABEL.get(r['status'], r['status'])}",
        quote=True,
    )


def arr_rows_html(rows: list[dict]) -> str:
    """Barras de magnitud: una sola serie, un solo color, de mayor a menor."""
    top = max(r["arr_keur"] for r in rows)
    out = []
    for r in sorted(rows, key=lambda r: -r["arr_keur"]):
        pct = r["arr_keur"] / top * 100 if top else 0.0
        out.append(
            f'<div class="row" tabindex="0" data-tip="{_tooltip(r)}">'
            f'<span class="row__name">{escape(r["company"])}</span>'
            f'<span class="track"><span class="bar" style="width:{pct:.2f}%"></span></span>'
            f'<span class="val">{es_num(r["arr_keur"])}</span>'
            "</div>"
        )
    return "\n".join(out)


def growth_rows_html(rows: list[dict]) -> str:
    """Barras divergentes sobre el cero: azul crece, rojo cae."""
    top = max(abs(r["mom_growth_pct"]) for r in rows) or 1.0
    out = []
    for r in sorted(rows, key=lambda r: -r["mom_growth_pct"]):
        value = r["mom_growth_pct"]
        half = abs(value) / top * 50  # % del carril completo; cada mitad son 50
        side = "pos" if value >= 0 else "neg"
        out.append(
            f'<div class="row" tabindex="0" data-tip="{_tooltip(r)}">'
            f'<span class="row__name">{escape(r["company"])}</span>'
            f'<span class="dtrack">'
            f'<span class="dbar dbar--{side}" style="width:{half:.2f}%"></span></span>'
            f'<span class="val">{es_num(value, 1)} %</span>'
            "</div>"
        )
    return "\n".join(out)


def table_rows_html(rows: list[dict]) -> str:
    out = []
    for r in sorted(rows, key=lambda r: -r["arr_keur"]):
        tone = STATUS_TONE.get(r["status"], "good")
        label = STATUS_LABEL.get(r["status"], r["status"])
        out.append(
            "<tr>"
            f'<td>{escape(r["company"])}</td>'
            f'<td>{escape(r["sector"])}</td>'
            f'<td class="num">{es_num(r["ownership_pct"], 1)}</td>'
            f'<td class="num">{es_num(r["arr_keur"])}</td>'
            f'<td class="num">{es_num(r["mom_growth_pct"], 1)}</td>'
            f'<td><span class="pill"><span class="dot dot--{tone}"></span>'
            f"{escape(label)}</span></td>"
            "</tr>"
        )
    return "\n".join(out)


def render_html(rows: list[dict], summary: dict) -> str:
    now = datetime.now()
    stamp = f"{now.day} {MESES[now.month - 1]} {now.year}, {now:%H:%M}"
    watch = summary["watch"]
    return (
        TEMPLATE
        .replace("__STAMP__", escape(stamp))
        .replace("__CSV__", escape(CSV_PATH.name))
        .replace("__ARR_TOTAL__", es_num(summary["total_arr"]))
        .replace("__COUNT__", str(summary["count"]))
        .replace("__GROWTH_AVG__", es_num(summary["avg_growth"], 1))
        .replace("__WATCH_COUNT__", str(len(watch)))
        .replace("__WATCH_NAMES__", escape(" · ".join(watch)) if watch else "Ninguna")
        .replace("__ARR_MAX__", es_num(max(r["arr_keur"] for r in rows)))
        .replace("__GROWTH_MAX__", es_num(max(abs(r["mom_growth_pct"]) for r in rows), 1))
        .replace("__ARR_ROWS__", arr_rows_html(rows))
        .replace("__GROWTH_ROWS__", growth_rows_html(rows))
        .replace("__TABLE_ROWS__", table_rows_html(rows))
    )


def main() -> None:
    rows = load_rows()
    summary = summarize(rows)
    print_summary(summary)
    HTML_PATH.write_text(render_html(rows, summary), encoding="utf-8")
    print(f"Dashboard: {HTML_PATH}")


TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Snapshot de cartera</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@500;600&family=IBM+Plex+Sans:wght@400;500;600&display=swap">
<style>
:root{
  --plane:#f9f9f7; --surface:#fcfcfb;
  --ink:#0b0b0b; --ink-2:#52514e; --muted:#898781;
  --grid:#e1e0d9; --axis:#c3c2b7; --hair:rgba(11,11,11,.10);
  --accent:#2a78d6; --neg:#e34948;
  --good:#0ca30c; --warn:#fab219;
  --hover:rgba(42,120,214,.07);
  --shadow:0 1px 2px rgba(11,11,11,.04);
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --plane:#0d0d0d; --surface:#1a1a19;
    --ink:#ffffff; --ink-2:#c3c2b7; --muted:#898781;
    --grid:#2c2c2a; --axis:#383835; --hair:rgba(255,255,255,.10);
    --accent:#3987e5; --neg:#e66767;
    --hover:rgba(57,135,229,.14);
    --shadow:none;
  }
}
:root[data-theme="dark"]{
  --plane:#0d0d0d; --surface:#1a1a19;
  --ink:#ffffff; --ink-2:#c3c2b7; --muted:#898781;
  --grid:#2c2c2a; --axis:#383835; --hair:rgba(255,255,255,.10);
  --accent:#3987e5; --neg:#e66767;
  --hover:rgba(57,135,229,.14);
  --shadow:none;
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{
  margin:0;background:var(--plane);color:var(--ink);
  font-family:"IBM Plex Sans",system-ui,-apple-system,"Segoe UI",sans-serif;
  font-size:15px;line-height:1.5;-webkit-font-smoothing:antialiased;
}
.wrap{max-width:1060px;margin:0 auto;padding-inline:20px;padding-block:36px 56px}
code{font-family:"IBM Plex Mono",ui-monospace,SFMono-Regular,Menlo,monospace;font-size:.92em;color:var(--ink-2)}

.eyebrow{
  display:inline-block;font-family:"IBM Plex Mono",ui-monospace,monospace;
  font-size:10.5px;font-weight:600;letter-spacing:.14em;text-transform:uppercase;
  color:var(--ink-2);background:var(--surface);
  border:1px solid var(--hair);border-radius:999px;padding:4px 11px;
}
h1{font-size:clamp(27px,4.4vw,36px);line-height:1.12;letter-spacing:-.015em;
   font-weight:600;margin:14px 0 6px;text-wrap:balance}
.lede{margin:0;color:var(--ink-2);font-size:13.5px}

.kpis{display:grid;gap:12px;grid-template-columns:repeat(2,minmax(0,1fr));margin-top:28px}
@media (min-width:780px){.kpis{grid-template-columns:repeat(4,minmax(0,1fr))}}
.kpi{background:var(--surface);border:1px solid var(--hair);border-radius:10px;
     box-shadow:var(--shadow);padding:16px 17px;display:flex;flex-direction:column;gap:5px}
.kpi__label{font-size:12.5px;font-weight:500;color:var(--ink-2)}
.kpi__value{font-size:27px;font-weight:600;letter-spacing:-.02em;line-height:1.05;margin-top:auto}
.kpi--hero .kpi__value{font-size:clamp(38px,6.4vw,50px)}
.kpi__unit{font-size:.44em;font-weight:500;color:var(--ink-2);margin-left:.28em;letter-spacing:0}
.kpi__foot{font-size:11.5px;color:var(--muted);line-height:1.35}

.charts{display:grid;gap:12px;margin-top:12px;grid-template-columns:1fr}
@media (min-width:880px){.charts{grid-template-columns:1fr 1fr}}
.card{position:relative;background:var(--surface);border:1px solid var(--hair);
      border-radius:10px;box-shadow:var(--shadow);padding:18px}
.card--table{margin-top:12px}
.card__title{font-size:14px;font-weight:600;margin:0;letter-spacing:-.005em}
.card__note{font-size:11.5px;color:var(--muted);margin:3px 0 18px}

.rows{display:flex;flex-direction:column;gap:11px}
.row{display:grid;grid-template-columns:minmax(78px,120px) 1fr 56px;align-items:center;
     gap:12px;padding:4px 5px;margin:-4px -5px;border-radius:6px}
.row:hover{background:var(--hover)}
.row:focus-visible{background:var(--hover);outline:2px solid var(--accent);outline-offset:1px}
.row__name{font-size:12.5px;color:var(--ink-2);line-height:1.25;overflow-wrap:anywhere}
.val{font-size:12.5px;font-weight:600;text-align:right;font-variant-numeric:tabular-nums;color:var(--ink-2)}

.track{position:relative;height:14px;border-left:1px solid var(--axis)}
.bar{position:absolute;left:0;top:0;height:14px;border-radius:0 4px 4px 0;background:var(--accent)}
.dtrack{position:relative;height:14px}
.dtrack::before{content:"";position:absolute;left:50%;top:-5px;bottom:-5px;width:1px;background:var(--axis)}
.dbar{position:absolute;top:0;height:14px}
.dbar--pos{left:50%;background:var(--accent);border-radius:0 4px 4px 0}
.dbar--neg{right:50%;background:var(--neg);border-radius:4px 0 0 4px}

.tooltip{position:absolute;z-index:6;pointer-events:none;max-width:230px;
  background:var(--ink);color:var(--plane);border-radius:7px;padding:8px 10px;
  font-size:11.5px;line-height:1.5;box-shadow:0 6px 18px rgba(0,0,0,.2)}
.tooltip b{font-weight:600}

.tablewrap{overflow-x:auto}
table{width:100%;min-width:540px;border-collapse:collapse;font-size:13px}
th{text-align:left;padding:0 10px 9px;white-space:nowrap;border-bottom:1px solid var(--hair);
   font-family:"IBM Plex Mono",ui-monospace,monospace;font-size:10.5px;font-weight:600;
   letter-spacing:.09em;text-transform:uppercase;color:var(--muted)}
td{padding:10px;border-bottom:1px solid var(--grid);font-variant-numeric:tabular-nums}
tbody tr:last-child td{border-bottom:none}
th.num,td.num{text-align:right}
.pill{display:inline-flex;align-items:center;gap:7px;white-space:nowrap;font-size:12.5px;color:var(--ink-2)}
.dot{width:8px;height:8px;border-radius:50%;flex:none}
.dot--good{background:var(--good)}
.dot--warn{background:var(--warn)}

.foot{margin-top:22px;font-size:11.5px;color:var(--muted);line-height:1.5}
@media (prefers-reduced-motion: reduce){*{transition:none!important;animation:none!important}}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <span class="eyebrow">Demo · datos ficticios</span>
    <h1>Snapshot de cartera</h1>
    <p class="lede">Generado por <code>summarize_portfolio.py</code> desde <code>__CSV__</code> · __STAMP__</p>
  </header>

  <section class="kpis" aria-label="Indicadores de cartera">
    <div class="kpi kpi--hero">
      <span class="kpi__label">ARR agregado</span>
      <span class="kpi__value">__ARR_TOTAL__<span class="kpi__unit">k€</span></span>
      <span class="kpi__foot">Suma de la cartera en muestra</span>
    </div>
    <div class="kpi">
      <span class="kpi__label">Participadas</span>
      <span class="kpi__value">__COUNT__</span>
      <span class="kpi__foot">Filas del CSV</span>
    </div>
    <div class="kpi">
      <span class="kpi__label">Crecimiento MoM medio</span>
      <span class="kpi__value">__GROWTH_AVG__<span class="kpi__unit">%</span></span>
      <span class="kpi__foot">Media simple, sin ponderar por ARR</span>
    </div>
    <div class="kpi">
      <span class="kpi__label">En seguimiento</span>
      <span class="kpi__value">__WATCH_COUNT__</span>
      <span class="kpi__foot">__WATCH_NAMES__</span>
    </div>
  </section>

  <section class="charts">
    <div class="card" data-chart>
      <h2 class="card__title">ARR por participada</h2>
      <p class="card__note">Miles de euros · máximo __ARR_MAX__ k€</p>
      <div class="rows">
__ARR_ROWS__
      </div>
      <div class="tooltip" hidden></div>
    </div>
    <div class="card" data-chart>
      <h2 class="card__title">Crecimiento MoM</h2>
      <p class="card__note">Variación mensual sobre el cero · máximo __GROWTH_MAX__ %</p>
      <div class="rows">
__GROWTH_ROWS__
      </div>
      <div class="tooltip" hidden></div>
    </div>
  </section>

  <section class="card card--table">
    <h2 class="card__title">Detalle</h2>
    <p class="card__note">Las mismas cifras, en tabla.</p>
    <div class="tablewrap">
      <table>
        <thead>
          <tr>
            <th scope="col">Participada</th>
            <th scope="col">Sector</th>
            <th scope="col" class="num">% cartera</th>
            <th scope="col" class="num">ARR k€</th>
            <th scope="col" class="num">MoM %</th>
            <th scope="col">Estado</th>
          </tr>
        </thead>
        <tbody>
__TABLE_ROWS__
        </tbody>
      </table>
    </div>
  </section>

  <footer class="foot">
    Cifras inventadas para una demo de Claude Code — no representan ninguna cartera real.
    La fuente de verdad es <code>__CSV__</code>: cambia el CSV, vuelve a ejecutar el script
    y esta página se regenera entera.
  </footer>
</div>
<script>
(function () {
  document.querySelectorAll("[data-chart]").forEach(function (card) {
    var tip = card.querySelector(".tooltip");
    if (!tip) return;
    card.querySelectorAll(".row").forEach(function (row) {
      function show() {
        tip.innerHTML = row.getAttribute("data-tip") || "";
        tip.hidden = false;
        var c = card.getBoundingClientRect(), r = row.getBoundingClientRect();
        var top = r.top - c.top - tip.offsetHeight - 8;
        if (top < 4) top = r.bottom - c.top + 8;
        var left = r.left - c.left + 10;
        left = Math.max(8, Math.min(left, c.width - tip.offsetWidth - 8));
        tip.style.top = top + "px";
        tip.style.left = left + "px";
      }
      function hide() { tip.hidden = true; }
      row.addEventListener("mouseenter", show);
      row.addEventListener("mouseleave", hide);
      row.addEventListener("focus", show);
      row.addEventListener("blur", hide);
    });
  });
})();
</script>
</body>
</html>
"""


if __name__ == "__main__":
    main()
