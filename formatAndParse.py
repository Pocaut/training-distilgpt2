import re
import json
# This formats chatlogs exported from WhatsApp.

def limpar_chat_whatsapp(arquivo_entrada, arquivo_saida):
    mensagens = []

    regex_mensagem = re.compile(r'^(\d{1,2}/\d{1,2}/\d{4})\s+(\d{1,2}:\d{2})\s+-\s+([^:]+):\s+(.*)$')



    # Added the <Mensagem Editada> after i trained the model, will fix later.
    palavras_sistema = [
        "adicionou", "removeu", "saiu", "mudou o assunto",
        "mudou o nome", "criou o grupo", "alterou as configurações",
        "excluiu esta mensagem", "Mensagem Editada", "null"
    ]

    with open(arquivo_entrada, 'r', encoding='utf-8') as arquivo:
        for linha in arquivo:
            linha = linha.strip()

            match = regex_mensagem.match(linha)
            if match:
                remetente = match.group(3)
                mensagem = match.group(4)

                # Filter system messages
                if any(palavra in mensagem.lower() for palavra in palavras_sistema):
                    continue

                # Filter media system messages
                if re.search(r"<.*?ocult[ao]>", mensagem.lower()):
                    continue


                # Filter @ mentions
                if re.search(r"@\d{5,}", mensagem):
                    continue

                # Filter links
                if re.search(r"https://\S+", mensagem):
                    continue


                mensagens.append({"remetente": remetente, "mensagem": mensagem})

    # Saves as JSON
    with open(arquivo_saida, 'w', encoding='utf-8') as saida:
        json.dump(mensagens, saida, indent=2, ensure_ascii=False)

    print(f"✅ Chat limpo salvo em: {arquivo_saida}")

if __name__ == "__main__":
    try:
        limpar_chat_whatsapp("YOUR_DATASET_INPUT", "YOUR_DESIRED_OUTPUT_PATH")
    except Exception as e:
        print(f"❌ Ocorreu um erro: {e}")

    input("\nPressione Enter para sair...")
