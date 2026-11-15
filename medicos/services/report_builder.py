"""Genera el reporte para médicos de vuelo en HTML (apto para QTextDocument/PDF)."""
from __future__ import annotations

from ..domain.enums import Status
from .health_service import RECOMMENDATIONS, HealthService, fx, signed


def build_report_html(svc: HealthService) -> str:
    m, p = svc.mission, svc.psych
    risk = round(svc.global_risk() * 100)
    inds = svc.indicators()
    follow = [a for a in inds if a.status is not Status.OK]

    rows = "".join(
        f"<tr><td>{a.spec.name}</td><td>{fx(a.mean, a.spec.decimals)}</td><td>{fx(a.last, a.spec.decimals)} {a.spec.unit}</td>"
        f"<td>{signed(a.delta, a.spec.decimals)}</td><td>{signed(a.slope, 2)}</td><td>{a.status.label}</td></tr>" for a in inds)
    pred = "".join(
        f"<tr><td>{a.spec.short_name}</td><td>{a.spec.threshold:g} {a.spec.unit}</td><td>{svc.window_text(a)}</td></tr>"
        for a in inds if a.days_to_threshold is not None)
    recs = "".join(f"<li>{RECOMMENDATIONS[a.spec.id]}</li>" for a in follow)
    comp = ", ".join(f"{c.name} {c.done}/{c.total}" for c in svc.compliance)
    phq = " → ".join(f"{v:g}" for v in p.phq9)
    gad = " → ".join(f"{v:g}" for v in p.gad7)
    th = "style='text-align:left;border-bottom:1px solid #d7dee8;color:#55627a'"
    return f"""
<h2 style="color:#0a3d91">Reporte para médicos de vuelo</h2>
<p style="color:#55627a">Tripulante demostrativo · {m.name} · Periodo: 30 días · Datos simulados</p>
<h3 style="color:#0a3d91">Resumen</h3>
<p>Estado general: {svc.overall_status().label}. Riesgo global estimado {risk} % (prototipo).
{len(follow)} indicadores y el bienestar psicológico requieren seguimiento.</p>
<h3 style="color:#0a3d91">Cambios respecto a valores basales y tendencias</h3>
<table width="100%" cellspacing="0" cellpadding="4">
<tr><th {th}>Indicador</th><th {th}>Base</th><th {th}>Actual</th><th {th}>Cambio</th><th {th}>Tendencia/día</th><th {th}>Estado</th></tr>{rows}</table>
<h3 style="color:#0a3d91">Evaluaciones psicológicas</h3>
<p>PHQ-9: {phq}. GAD-7: {gad}. Instrumentos de tamizaje, no diagnóstico. Cumplimiento: {comp}.</p>
<h3 style="color:#0a3d91">Estimaciones predictivas (IC 95 %)</h3>
<table width="100%" cellspacing="0" cellpadding="4"><tr><th {th}>Indicador</th><th {th}>Umbral</th><th {th}>Ventana estimada</th></tr>{pred}</table>
<h3 style="color:#0a3d91">Recomendaciones de seguimiento</h3>
<ul>{recs}<li>Comentar la tendencia de los cuestionarios con el médico de vuelo.</li></ul>
<p style="color:#55627a">Documento de apoyo a la decisión generado con datos simulados. No constituye diagnóstico.</p>
"""
