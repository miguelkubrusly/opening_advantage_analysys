# Lichess API — Download de partidas de um usuário

_(Games → Export games of a user)_

Exporta as partidas de qualquer usuário do Lichess em **stream NDJSON** (um jogo por linha) ou em **PGN**, com filtros por período, rating, modo (blitz/rapid/etc.), cor, oponente e flags para incluir **clocks**, **evals**, **opening**, **accuracy**, etc.

---

## Endpoint

```
GET /api/games/user/{username}
```

### Formatos e cabeçalhos

- **NDJSON** (recomendado p/ processamento):  
  Envie `Accept: application/x-ndjson`
- **PGN**:  
  Envie `Accept: application/x-chess-pgn`

> **Dica:** o NDJSON é um **stream** — cada linha é um objeto JSON de uma partida. Em muitas libs HTTP, você deve ler linha-a-linha.

---

## Autenticação & Rate limit

- Jogos públicos podem ser baixados **sem token**.
- Para volumes maiores e/ou campos “caros” (ex.: accuracy), use **token**:  
  `Authorization: Bearer <TOKEN>`
- **Rate limit (boas práticas):** faça **uma** requisição por vez; se receber **HTTP 429**, aguarde **~1 minuto** antes de retomar.

---

## Parâmetros (query)

| Parâmetro              |     Tipo | Descrição                                                                            |
| ---------------------- | -------: | ------------------------------------------------------------------------------------ |
| `max`                  |      int | Máximo de partidas no retorno. Útil para recortes rápidos.                           |
| `since` / `until`      | epoch ms | Janela por **Unix epoch (ms)**. Combine com `max` p/ recortes por período.           |
| `rated`                |     bool | Somente partidas ranqueadas (`true`/`false`).                                        |
| `perfType`             |   string | Modo: `bullet`, `blitz`, `rapid`, `classical`, `ultraBullet`, `correspondence`, etc. |
| `color`                |   string | `white` ou `black`.                                                                  |
| `vs`                   |   string | Filtra por oponente (username).                                                      |
| `analysed`             |     bool | Apenas partidas com análise de engine. **Necessário p/ `accuracy`.**                 |
| `ongoing` / `finished` |     bool | Filtra partidas em andamento / finalizadas.                                          |
| `sort`                 |   string | Ordenação: `dateDesc` (padrão) ou `dateAsc`.                                         |
| `moves`                |     bool | Incluir a string de lances.                                                          |
| `tags`                 |     bool | Incluir cabeçalhos PGN (event, date, result…) quando em PGN.                         |
| `clocks`               |     bool | Incluir tempos de relógio por lance.                                                 |
| `evals`                |     bool | Incluir avaliações da engine por lance.                                              |
| `opening`              |     bool | Incluir nome da abertura detectada.                                                  |
| `accuracy`             |     bool | Incluir _accuracy_ por jogador (**requer** `analysed=true`).                         |
| `lastFen`              |     bool | Incluir FEN da **última** posição (**somente NDJSON**).                              |

> **Observação:** Nem todos os campos aparecem em PGN. Para **accuracy**, use **NDJSON** e garanta `analysed=true`.

---

## Exemplos práticos

### 1) Últimos 10 jogos **blitz**, ranqueados, com abertura, em NDJSON

```bash
curl -L "https://lichess.org/api/games/user/SomeUser\
?max=10&perfType=blitz&rated=true&opening=true" \
  -H "Accept: application/x-ndjson"
```

### 2) Mesmo recorte, mas **com accuracy** (exige jogos analisados)

```bash
curl -L "https://lichess.org/api/games/user/SomeUser\
?max=10&perfType=blitz&rated=true&analysed=true&accuracy=true" \
  -H "Accept: application/x-ndjson"
```

### 3) Janela por período (ex.: de 1º/abr/2025 a 30/abr/2025)

```bash
SINCE=$(( 1711929600000 ))  # 2025-04-01T00:00:00Z em ms
UNTIL=$(( 1714435200000 ))  # 2025-04-30T00:00:00Z em ms
curl -L "https://lichess.org/api/games/user/SomeUser?since=$SINCE&until=$UNTIL&max=200" \
  -H "Accept: application/x-ndjson"
```

### 4) **PGN** com relógios e abertura (para importar em GUI)

```bash
curl -L "https://lichess.org/api/games/user/SomeUser\
?max=50&clocks=true&opening=true" \
  -H "Accept: application/x-chess-pgn" -o games.pgn
```

### 5) Python (requests) lendo **NDJSON streaming**

```python
import requests, json

url = "https://lichess.org/api/games/user/SomeUser"
params = {"max": 25, "analysed": True, "accuracy": True}
headers = {"Accept": "application/x-ndjson"}  # essencial para JSON

with requests.get(url, params=params, headers=headers, stream=True) as r:
    r.raise_for_status()
    for line in r.iter_lines(decode_unicode=True):
        if not line:
            continue
        game = json.loads(line)   # cada linha é um jogo (dict)
        # use game["id"], game["moves"], game["players"], game.get("accuracy"), etc.
```

### 6) Node (fetch) lendo NDJSON linha-a-linha

```js
const res = await fetch(
  "https://lichess.org/api/games/user/SomeUser?max=50&opening=true",
  {
    headers: { Accept: "application/x-ndjson" },
  }
);
const reader = res.body.getReader();
const decoder = new TextDecoder();
let buf = "";
for (;;) {
  const { value, done } = await reader.read();
  if (done) break;
  buf += decoder.decode(value, { stream: true });
  let idx;
  while ((idx = buf.indexOf("\n")) >= 0) {
    const line = buf.slice(0, idx).trim();
    buf = buf.slice(idx + 1);
    if (line) {
      const game = JSON.parse(line);
      // processa game...
    }
  }
}
```

---

## Campos comuns no NDJSON (resumo)

- `id` (string) — ID da partida
- `rated` (bool) — se é ranqueada
- `variant` (string) — `standard`, `atomic`, etc.
- `speed` / `perf` — controle (`blitz`,`rapid`…)
- `createdAt`, `lastMoveAt` — epoch ms
- `status` — `mate`, `resign`, `draw`, etc.
- `players.white|black` — `user` (id/name), `rating`, `ratingDiff`, …
- `moves` — lances em SAN separados por espaço
- `opening` — (quando `opening=true`) nome ECO detectado
- `clock` — `{ initial, increment, totalTime }`
- `accuracy` — (quando `accuracy=true` + `analysed=true`) métricas por jogador

---

## Paginação & estratégia de coleta

- O retorno é por padrão **mais recente primeiro**.
- Use `max` para limitar; combine com `since`/`until` para janelas de tempo.
- Para coleções grandes, itere por **período** (ex.: mês a mês) para evitar rate-limit.

---

## Boas práticas & _gotchas_

- **Header certo para JSON:** use **`Accept: application/x-ndjson`** (não `application/json`).
- **Accuracy só em JSON + analisado:** inclua `analysed=true` e `accuracy=true`.
- **Relógios:** a flag é `clocks` (no plural).
- **Redirects:** alguns clientes precisam de `-L` no `curl`.
- **Rate limit:** 1 req por vez; após **429**, aguarde ~1 min antes de retomar.
- **`lastFen`:** só funciona em **NDJSON**.

---

## JSONs de referência (trechos reais)

> Abaixo, **recortes curtos** de NDJSON público (apenas para ilustrar chaves e formato).

### Trecho 1 — metadados básicos

```json
{
  "id": "yNFRBVc4",
  "rated": true,
  "variant": "atomic",
  "speed": "rapid",
  "perf": "atomic",
  "createdAt": 1579519705716
}
```

### Trecho 2 — início da árvore de `players`

```json
{
  "players": {
    "white": { "user": { "id": "mbellm", "name": "mbellm" }, "rating": 1715 },
    "black": { "rating": 1740 }
  }
}
```

---

## Snippets prontos (cola e usa)

- **Últimas 5 partidas do usuário, com abertura, salvando em arquivo:**

```bash
curl -L "https://lichess.org/api/games/user/SomeUser?max=5&opening=true" \
  -H "Accept: application/x-ndjson" > someuser.ndjson
```

- **Somente contra um oponente específico, partidas finalizadas:**

```bash
curl -L "https://lichess.org/api/games/user/SomeUser?vs=OtherUser&finished=true" \
  -H "Accept: application/x-ndjson"
```

- **PGN com clocks, para importar numa GUI:**

```bash
curl -L "https://lichess.org/api/games/user/SomeUser?max=100&clocks=true" \
  -H "Accept: application/x-chess-pgn" -o someuser_with_clocks.pgn
```

---

## Checklist de integração

- [ ] Escolhi o formato certo para o meu pipeline (**NDJSON** vs **PGN**).
- [ ] Configurei `Accept` corretamente.
- [ ] Usei filtros (`since/until`, `perfType`, `rated`) para reduzir volume.
- [ ] Para _accuracy_, garanti `analysed=true` + NDJSON.
- [ ] Implementei leitura **streaming** (linha-a-linha) no cliente.
- [ ] Respeito rate-limit (1 req/vez; backoff em 429).

---
