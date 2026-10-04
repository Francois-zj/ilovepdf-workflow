# iLovePDF : Word → PDF → PDF avec filigrane

[中文](README.zh-CN.md) | [English](README.md) | **Français**

Un programme pour Windows qui utilise Python, tkinter et Playwright pour piloter le site **www.ilovepdf.com** dans un navigateur visible. Il convertit des documents Word en PDF, puis ajoute un filigrane textuel. Ce projet indépendant n'est pas un outil officiel d'iLovePDF. Il n'utilise ni la conversion intégrée de Microsoft Word ni l'API développeur d'iLovePDF.

## Fonctionnalités

- Choix de trois dossiers : documents Word, PDF ordinaires et PDF avec filigrane.
- Conversion des fichiers `.doc` et `.docx`, puis ajout du filigrane, fichier par fichier.
- Réglage du texte, de la police, de la taille, de la couleur, de la position, de la transparence, de la rotation, du calque et des pages.
- Vérification facultative des paramètres du premier PDF avant son traitement.
- Reprise des tâches validées grâce au suivi et aux empreintes des fichiers ; aucun remplacement automatique d'un résultat existant non vérifié.
- Conservation des documents sources et de leurs noms de base.

## Prérequis

Windows, **Python 3.10 ou supérieur** avec tkinter, **Google Chrome ou Microsoft Edge** installé, et une connexion Internet. Chrome est utilisé en priorité ; Edge est essayé si Chrome n'est pas installé. L'interface et les messages du programme sont actuellement en chinois. La documentation est trilingue, mais l'interface ne propose pas de changement de langue. Les autres systèmes n'ont pas été validés.

## Installation et utilisation

1. Sur GitHub, choisissez **Code → Download ZIP**, puis décompressez l'archive.
2. Ouvrez l'invite de commandes et saisissez `python --version`. Si nécessaire, essayez `py -3 --version`. Si aucune commande ne fonctionne, installez Python 3.10 ou supérieur en cochant **Add Python to PATH**.
3. Double-cliquez sur `setup.bat`. Attendez **Installation complete**. Le script crée `.venv` et installe les dépendances. Il suffit de le lancer lors de l'installation initiale ou d'un changement de dépendances.
4. Double-cliquez sur `start.bat`.
5. Choisissez trois dossiers différents, par exemple `F:\WordInput`, `F:\PDF` et `F:\PDF_Watermarked`. Le dossier source doit exister ; les dossiers de sortie sont créés si nécessaire.
6. Saisissez le texte du filigrane et choisissez sa présentation. Le texte par défaut est `François QIN` : remplacez-le par votre propre texte.
7. Laissez **每一页都加水印** coché pour traiter toutes les pages de chaque document. Les champs de début et de fin sont alors ignorés, quel que soit le nombre de pages du fichier.
8. Choisissez les PDF à traiter lors de la deuxième étape, puis cliquez sur **开始处理**.
9. Fermez la bannière de cookies dans le navigateur et connectez-vous si nécessaire. Revenez à l'invite de commandes et appuyez sur Entrée lorsque vous êtes prêt.
10. Le programme convertit d'abord tous les documents Word. Si la vérification du premier PDF est activée, il s'arrête après avoir configuré son filigrane. Vérifiez les paramètres sur le site, puis appuyez sur Entrée dans la console. Pour modifier les réglages, saisissez `q`, puis relancez le programme. Ce contrôle porte sur les paramètres du site, pas sur le PDF final.
11. Les fichiers suivants sont traités automatiquement avec les mêmes réglages. Gardez le navigateur et la console ouverts. Si le site demande une intervention, suivez les indications de la console.
12. Lorsque le programme annonce la fin du traitement, ouvrez les dossiers de sortie et vérifiez les PDF. Appuyez ensuite sur Entrée au dernier message pour fermer le programme.

## Repères dans l'interface

| Libellé chinois | Signification |
| --- | --- |
| Word 来源目录 | Dossier source des documents Word |
| 普通 PDF 保存目录 | Dossier des PDF ordinaires |
| 水印 PDF 保存目录 | Dossier des PDF avec filigrane |
| 水印文字 / 字体 / 字号 / 文字颜色 | Texte / police / taille / couleur |
| 位置：下右 | Position en bas à droite |
| 水印图层：内容上方 / 内容下方 | Au-dessus / au-dessous du contenu |
| 指定范围：起始页 / 结束页 | Première / dernière page, incluses |
| 第二阶段处理范围：全部 PDF | Tous les PDF du dossier de sortie ordinaire |
| 仅本次 Word 对应的 PDF | Seulement les PDF correspondant aux documents Word du traitement |
| 每个网站任务后的间隔 | Attente après chaque tâche réussie, au moins 20 secondes |
| 每一页都加水印 | Ajouter le filigrane à toutes les pages |
| 平铺 / 加粗 / 斜体 | Mosaïque / gras / italique |
| 首个 PDF 提交前检查预览 | Vérifier les paramètres du premier PDF avant envoi |
| 开始处理 | Démarrer |

Les valeurs de transparence reprennent les choix **Transparency** du site. Si l'option toutes les pages est désactivée, une même plage numérique s'applique à chaque document. Une page de fin supérieure au nombre de pages entraîne une pause. Les plages différentes par fichier ne sont pas prises en charge. Pour changer les paramètres, arrêtez et relancez le programme au lieu de les modifier uniquement dans le navigateur.

## Reprise et dépannage

Conservez `_workflow_progress.json` dans le dossier des PDF avec filigrane. En relançant avec les mêmes dossiers et paramètres, les tâches dont les empreintes source et sortie correspondent sont ignorées. Un déplacement de dossier ou une modification des documents ou du filigrane peut empêcher la reconnaissance d'un résultat existant. Choisissez alors un nouveau dossier de sortie adapté ou déplacez le fichier en conflit. Il ne sera pas remplacé automatiquement.

Le journal est enregistré dans `_workflow_log.txt`. Certains incidents produisent une capture `_workflow_error.png`. Si un téléchargement échoue alors que le navigateur reste accessible, cliquez sur **Download PDF** sur le site, puis reprenez selon la console. Si le navigateur se déconnecte, relancez le programme après avoir lu l'erreur. En cas d'échec de l'installation, consultez le message : un ancien lanceur `py` peut pointer vers une installation supprimée. Le script fourni essaie d'abord `python`.

Le programme ne parcourt pas les sous-dossiers et ignore les fichiers temporaires Word commençant par `~$`. Renommez les fichiers `.doc` et `.docx` ayant le même nom de base.

Les documents sont envoyés à iLovePDF. La connexion au compte, les CAPTCHA, les quotas et les changements du site peuvent nécessiter une intervention ; ils ne sont pas contournés. Le résultat dépend du site et du réseau. Un lot de 11 documents a été traité avec succès lors du test local de l'auteur sous Windows ; la compatibilité avec tous les environnements n'est pas garantie.

## Fichiers du dépôt

`workflow.py` : application ; `requirements.txt` : dépendances ; `setup.bat` : installation ; `start.bat` : lancement ; les trois README : documentation ; `.gitignore` : exclusions locales.

Publiez uniquement ces fichiers. N'ajoutez pas vos Word/PDF personnels, `.venv`, les profils du navigateur, `settings.json`, le suivi, les journaux ou les captures d'erreur. `.gitignore` filtre les ajouts effectués avec Git, pas les fichiers téléversés manuellement sur le site GitHub.
