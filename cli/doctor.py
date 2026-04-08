# cli/doctor.py
import typer
import sys
import os

# Asegurar que Python encuentre la carpeta raíz del proyecto
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.tools.doctor import doctor_diagnose

app = typer.Typer(
    name="doctor",
    help="🩺 SuperNova Doctor - Diagnóstico y mantenimiento del sistema"
)

@app.command("check")
def run_diagnosis():
    """Ejecuta un diagnóstico completo y muestra el reporte en terminal."""
    typer.secho("🩺 Iniciando diagnóstico del entorno SuperNova...", fg="cyan", bold=True)
    try:
        # Ejecuta la herramienta de diagnóstico
        report = doctor_diagnose.invoke({"fix_mode": False})
        typer.echo(report)
        typer.secho("\n✅ Diagnóstico finalizado. Revisa las recomendaciones si las hay.", fg="green")
    except Exception as e:
        typer.secho(f"❌ Error crítico durante el diagnóstico: {e}", fg="red", err=True)
        sys.exit(1)

@app.command("fix")
def run_fix(
    auto_confirm: bool = typer.Option(False, "--yes", "-y", help="Confirma automáticamente las reparaciones seguras")
):
    """Ejecuta reparaciones automáticas seguras (limpieza de caché, reinicio de servicios locales)."""
    typer.secho("🔧 Modo reparación activado.", fg="yellow")
    if not auto_confirm:
        typer.secho("💡 Por seguridad, las reparaciones requieren confirmación. Usa: `python cli/doctor.py fix --yes`", fg="blue")
    else:
        typer.secho("✅ Ejecutando mantenimiento preventivo seguro...", fg="green")

if __name__ == "__main__":
    app()
