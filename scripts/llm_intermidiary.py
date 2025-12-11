import json
import time
from pathlib import Path
from scripts.llm_contact import ask_llm, read_file


def send_to_llm(export_path):
    # -------------------------
    # 1. CHARGEMENT DU CONTEXTE
    # -------------------------

    sys_content = read_file("scripts/context.txt")


        

    # -------------------------
    # 2. RÉCUPÉRER TOUS LES FICHIERS JSON D'UN DOSSIER
    # -------------------------
    folder_path = Path("exports/parsed_json")  # Remplacez par votre dossier
    uploaded_files = list(folder_path.glob("*.json"))

    if not uploaded_files:
        print(f"❌ Aucun fichier JSON trouvé dans {folder_path}")
        exit(1)

    analyses_partielles = []

    # -------------------------
    # 3. TRAITEMENT FICHIER PAR FICHIER
    # -------------------------
    for i, file_path in enumerate(uploaded_files, start=1):
        print(f"⚙️ Traitement du fichier {i}/{len(uploaded_files)} : {file_path.name}")

        # Lecture du JSON
        with open(file_path, "r", encoding="utf-8") as f:
            file_content = json.load(f)

        # Minification pour économiser les tokens
        json_str = json.dumps(file_content, separators=(',', ':'), ensure_ascii=False)
        if len(json_str) > 500_000:
            json_str = json_str[:500_000] + "... (tronqué)"

        # --- Appel backend ---
        messages_intermediaires = [
            {"role": "system", "content": sys_content},
            {"role": "user", "content": f"Voici le contenu du fichier '{file_path.name}' à traiter : {json_str}"}
        ]

        stream = ask_llm(chat_history=messages_intermediaires)

        partial_res = ""
        for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                partial_res += content

        analyses_partielles.append(f"--- Résultat pour {file_path.name} ---\n{partial_res}\n")
        print(f"✅ Fichier traité : {file_path.name}\n")

    # -------------------------
    # 4. CONSOLIDATION FINALE
    # -------------------------
    print("📑 Consolidation des résultats...")

    global_context = "\n".join(analyses_partielles)
    final_prompt_content = (
        f"Voici les résultats de l'analyse individuelle de chaque fichier. "
        f"Compile ou présente le résultat final conformément à tes instructions système :\n\n{global_context}"
    )

    stream_final = ask_llm(chat_history=[
        {"role": "system", "content": sys_content},
        {"role": "user", "content": final_prompt_content}
    ])

    full_response = ""
    for chunk in stream_final:
        content = chunk.choices[0].delta.content
        if content:
            full_response += content
        time.sleep(0.005)

    # -------------------------
    # 5. AFFICHAGE / SAUVEGARDE
    # -------------------------
    print("\n=== RÉSULTAT FINAL ===\n")
    print(full_response)

    with open(export_path, "w", encoding="utf-8") as f:
        f.write(full_response)
