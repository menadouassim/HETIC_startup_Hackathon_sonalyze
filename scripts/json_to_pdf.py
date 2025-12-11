import json
import os
import numpy as np
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
import matplotlib
matplotlib.use('Agg')
# -------------------------
# 1. LOAD JSON
# -------------------------
def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# -------------------------
# 2. CREATE PDF FROM STRUCTURED JSON WITH GRAPHS
# -------------------------
def create_pdf_with_graphs(data, pdf_path):
    doc = SimpleDocTemplate(
        pdf_path, pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=22, spaceAfter=20)
    section_style = ParagraphStyle('Section', parent=styles['Heading2'], fontSize=16, spaceAfter=12)
    body_style = ParagraphStyle('Body', parent=styles['BodyText'], fontSize=12, leading=16)
    story = []

    # HEADER
    story.append(Paragraph("<b>SONALYZE – Rapport d'Analyse Acoustique</b>", title_style))
    if os.path.exists("logo.png"):
        story.append(Image("logo.png", width=4*cm, height=4*cm))
        story.append(Spacer(1, 10))

    # -------------------------
    # INTERPRETATION
    # -------------------------
    interp = data.get('interpretation', {})
    story.append(Paragraph("1. Interprétation Globale", section_style))
    story.append(Paragraph(f"<b>Note globale:</b> {interp.get('note_globale', 'N/A')}", body_style))
    story.append(Paragraph(f"<b>Explication:</b> {interp.get('explication_note', 'N/A')}", body_style))
    story.append(Paragraph(f"<b>Comparaison aux seuils:</b> {interp.get('comparaison_seuils', 'N/A')}", body_style))
    story.append(Spacer(1, 12))

    # -------------------------
    # ANALYSE DES BRUITS
    # -------------------------
    analyse = data.get('analyse_bruits', {})
    story.append(Paragraph("2. Analyse des Bruits", section_style))
    classification = analyse.get('classification', {})
    story.append(Paragraph(f"<b>Bons bruits:</b> {', '.join(classification.get('bons', [])) or 'N/A'}", body_style))
    story.append(Paragraph(f"<b>Bruits dérangeants:</b> {', '.join(classification.get('derangeants', [])) or 'N/A'}", body_style))
    
    categories = analyse.get('categories', {})
    story.append(Paragraph(f"<b>Extérieur:</b> {categories.get('exterieur', 'N/A')}", body_style))
    story.append(Paragraph(f"<b>Intérieur / Voisinage:</b> {categories.get('interieur_voisinage', 'N/A')}", body_style))
    story.append(Paragraph(f"<b>Équipements:</b> {categories.get('equipements', 'N/A')}", body_style))
    story.append(Paragraph(f"<b>Récurrence:</b> {analyse.get('recurrence', 'N/A')}", body_style))
    story.append(Paragraph(f"<b>Jour / Nuit:</b> {analyse.get('jour_nuit', 'N/A')}", body_style))
    story.append(Spacer(1, 12))

    # -------------------------
    # GENERATE PIE CHART FOR SOURCES
    # -------------------------
    all_sources = classification.get('bons', []) + classification.get('derangeants', [])
    if all_sources:
        source_counts = {}
        for s in all_sources:
            source_counts[s] = source_counts.get(s, 0) + 1

        sorted_sources = sorted(source_counts.items(), key=lambda x: x[1], reverse=True)
        top_n = min(6, len(sorted_sources))
        labels = [s for s, c in sorted_sources[:top_n]]
        sizes = [c for s, c in sorted_sources[:top_n]]
        if len(sorted_sources) > top_n:
            others_count = sum([c for s, c in sorted_sources[top_n:]])
            labels.append('Autres')
            sizes.append(others_count)

        pie_path = "temp_sources_pie.png"
        plt.figure(figsize=(6,6))
        plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
        plt.axis('equal')
        plt.title('Répartition des sources dominantes')
        plt.tight_layout()
        plt.savefig(pie_path, dpi=150)
        plt.close()
        story.append(Paragraph("Graphique: Répartition des sources dominantes", body_style))
        story.append(Image(pie_path, width=10*cm, height=10*cm))
        story.append(Spacer(1, 12))
    else:
        story.append(Paragraph("Pas assez de données pour générer le graphique des sources.", body_style))
        story.append(Spacer(1, 12))

    # -------------------------
    # HYPOTHESES
    # -------------------------
    hypotheses = data.get('hypotheses', {})
    story.append(Paragraph("3. Hypothèses", section_style))
    faiblesses = hypotheses.get('faiblesses_structurelles', [])
    if faiblesses:
        for idx, hypo in enumerate(faiblesses, 1):
            story.append(Paragraph(f"• {hypo}", body_style))
    else:
        story.append(Paragraph("Aucune faiblesse structurelle identifiée.", body_style))
    story.append(Spacer(1, 12))

    # -------------------------
    # RECOMMANDATIONS
    # -------------------------
    recommendations = data.get('recommandations', [])
    story.append(Paragraph("4. Recommandations", section_style))
    if recommendations:
        for rec in recommendations:
            level = rec.get('niveau', 'N/A')
            action = rec.get('action', 'N/A')
            cost = rec.get('cout_estime', 'N/A')
            story.append(Paragraph(f"• Niveau: {level}, Action: {action}, Coût estimé: {cost}", body_style))
    else:
        story.append(Paragraph("Aucune recommandation fournie.", body_style))

    # -------------------------
    # EXPORT PDF
    # -------------------------
    try:
        doc.build(story)
        print(f"PDF généré: {pdf_path}")
    except PermissionError:
        alt_name = pdf_path.replace('.pdf', '') + "_locked.pdf"
        doc = SimpleDocTemplate(alt_name, pagesize=A4,
                                rightMargin=2*cm, leftMargin=2*cm,
                                topMargin=2*cm, bottomMargin=2*cm)
        doc.build(story)
        print(f"Fichier cible verrouillé. PDF enregistré en tant que: {alt_name}")

    # Cleanup temporary images
    if os.path.exists("temp_sources_pie.png"):
        os.remove("temp_sources_pie.png")


# -------------------------
# 3. MAIN
# -------------------------


def json_to_pdf(file_path,export_path):
    data_loaded = load_json(file_path)
    create_pdf_with_graphs(data_loaded,export_path)
