import json
# Had to run this on the training data after i realized Whatsapp Stickers show up as NULL.

def remover_mensagens_nulas(arquivo_json):
    with open(arquivo_json, 'r', encoding='utf-8') as f:
        mensagens = json.load(f)

    # Filter all but NULL
    mensagens_filtradas = [m for m in mensagens if m.get("mensagem") != "null"]

    with open(arquivo_json, 'w', encoding='utf-8') as f:
        json.dump(mensagens_filtradas, f, indent=2, ensure_ascii=False)

    print(f"✅ Mensagens com 'null' removidas de: {arquivo_json}")

if __name__ == "__main__":
    try:
        remover_mensagens_nulas("YOUR_DATASET_PATH")
    except Exception as e:
        print(f"❌ Erro ao limpar o JSON: {e}")

    input("\nPressione Enter para sair...")
