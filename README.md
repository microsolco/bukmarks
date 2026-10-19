# bukmarks

Bookmarks manager da riga di comando (Python ≥ 3.9, nessuna dipendenza). I bookmarks stanno in un unico
file JSON (`~/.bukmarks/bookmarks.json`, cambiabile con `BUKMARKS_HOME`) dentro un repository git:
**ogni modifica fa commit e, se c'è un remote, push in automatico.**

## Installazione

```bash
pip install -e .        # crea il comando `bukmarks`
# oppure, senza installare: python3 -m bukmarks <comando>
```

## Uso

| Comando | Descrizione |
|---|---|
| `bukmarks add <url> [-t titolo] [-T tag,tag] [-n nota]` | salva un indirizzo (titolo letto dalla pagina) |
| `bukmarks find <testo…> [-T tag] [-a] [-r]` | cerca in nome e indirizzo (`-a` anche tag/note, `-r` regex) |
| `bukmarks list [-T tag] [-s id\|title\|date]` | elenca tutto |
| `bukmarks show <id>` / `open <id…>` | dettagli / apri nel browser |
| `bukmarks edit <id> [--title --url --note --add-tag --rm-tag]` | modifica |
| `bukmarks rm <id…> [-y]` | elimina |
| `bukmarks tags` | tag e conteggi |
| `bukmarks export <file.html> [-f netscape]` | pagina HTML pulita con filtro live, o formato importabile dai browser |
| `bukmarks import <file.json\|.html>` | importa da JSON o dai preferiti di Chrome/Firefox/Safari (le cartelle diventano tag) |
| `bukmarks check [-T tag]` | trova i link non raggiungibili |
| `bukmarks remote [url]` | imposta il repository remoto per il push |
| `bukmarks sync` | pull + push (più computer) |
| `bukmarks log` / `path` | cronologia git / percorso del JSON |

## Backup su GitHub

```bash
bukmarks remote git@github.com:utente/miei-bookmarks.git
```
Da quel momento ogni `add`/`edit`/`rm` fa push. Su un altro computer: `git clone <url> ~/.bukmarks`.
Se il push fallisce (offline) il commit resta locale e viene inviato al prossimo salvataggio o con `sync`.
