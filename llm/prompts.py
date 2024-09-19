from .prompt_wrap_tags import prompt_wrap_tags



def df_to_prompt(df):
    prompt = """
Tu es un assistant intelligent et tu réponds uniquement en français.
Tu es en train de discuter avec une personne par message. Ton rôle est de poursuivre cette conversation de manière naturelle et fluide.
Voici tes consignes :
1. Envoie un nouveau message à cette personne, en te basant sur la conversation précédente.
2. Ton message doit être court et simple, en une seule phrase.
3. Utilise un langage familier.
4. Réponds de manière appropriée et cohérente, en tenant compte du ton et du style de la personne avec qui tu discutes.
5. Base-toi principalement sur les quelques derniers messages de l'autre personne pour formuler ta réponse.

Voici la conversation précédente :

"""
    for i in range(len(df)):
        sender = df.iloc[i]['sender']
        body = df.iloc[i]['body']
        date = df.iloc[i]['date']

        if sender == 'Me':
            sender = 'Assistant'

        prompt += f"{sender} ({date}): {body}\n"

    prompt = prompt_wrap_tags(prompt=prompt, model_type="llama")
    return prompt


def correction_prompt(text:str):
    prompt = f"""
Corrige le texte suivant en améliorant la grammaire, la ponctuation et l'orthographe, tout en préservant le sens du message.
Si le texte est ambigu ou difficile à comprendre, fais de ton mieux pour clarifier le message sans indiquer qu'il est difficile à comprendre.
Ne modifie pas le style du message à moins que cela soit nécessaire pour la clarté.

Voici le texte à corriger :
```{text}```
"""
    prompt = prompt_wrap_tags(prompt=prompt, model_type="llama")
    return prompt