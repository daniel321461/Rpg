# RPG AI Master (patched)

A local web RPG chat with character sheet, quests, notes, dice, save/load and an OpenAI-compatible model backend.

## Yandex AI Studio (DeepSeek V4.1 Flash) на Railway

Добавьте в Railway → ваш проект → сервис → Variables следующие переменные:

- `YANDEX_API_KEY` — секретная часть API-ключа Yandex AI Studio.
- `YANDEX_FOLDER_ID` — ID каталога, в котором создан сервисный аккаунт/API-ключ.
- `YANDEX_MODEL` — необязательно. По умолчанию используется `gpt://<YANDEX_FOLDER_ID>/deepseek-v4.1-flash`.

Для Yandex используется OpenAI-совместимый endpoint `https://ai.api.cloud.yandex.net/v1`.
Ключ передаётся через переменные окружения; не помещайте его в исходники, README или GitHub.
Если заданы `YANDEX_API_KEY` и `YANDEX_FOLDER_ID`, приложение автоматически выбирает Yandex AI Studio.
Старые переменные `OPENAI_*` оставлены для совместимости с Ollama и другими OpenAI-совместимыми провайдерами.

После добавления переменных перезапустите/redeploy сервис. Проверить состояние можно по `/api/health` — там отображаются провайдер и модель, но не секреты.

## Quick start (Windows)

1. Install Python 3.10+.
2. Open this folder in Terminal / CMD.
3. Install dependencies:
   ```bat
   python -m pip install -r requirements.txt
   ```
4. Set the model connection for the current terminal session.

### Ollama (local model)

Ensure Ollama is running and that your model is downloaded. Example for Qwen 2.5:

```bat
ollama pull qwen2.5:7b
set OPENAI_BASE_URL=http://localhost:11434/v1
set OPENAI_API_KEY=ollama
set OPENAI_MODEL=qwen2.5:7b
python app.py
```

Open `http://127.0.0.1:5000` in your browser.

If using a different Ollama model, replace `OPENAI_MODEL` with the exact model tag from `ollama list`.

### Other OpenAI-compatible providers

Set `OPENAI_BASE_URL`, `OPENAI_API_KEY`, and `OPENAI_MODEL` to the provider's endpoint, key, and model. If `OPENAI_BASE_URL` is unset, the OpenAI API is used.


## Экономия токенов (balanced)

В этой версии оптимизированы фоновые операции без замены основной модели и без изменения игрового системного промпта:

- История больше не пересуммируется на каждом `/api/chat`. Браузер вызывает `/api/compact` только после превышения порога (по умолчанию 24 реплики); после успешного сжатия компактная история сохраняется в localStorage и обычных сохранениях.
- Извлечение листа персонажа выполняется раз в 3 хода либо сразу при явных маркерах изменения состояния (XP, HP, завершение квеста, изменения инвентаря/золота и создание персонажа). XP по явным строкам `+N XP` продолжает обрабатываться сервером на каждом ходе без дополнительного вызова модели.
- Окно диалога для извлечения состояния уменьшено до последних 8 сообщений; мастер по-прежнему получает полный актуальный лист персонажа.
- ID XP-событий теперь не зависит от позиции сообщения в истории, поэтому сжатие истории не должно повторно начислять XP. Старые ID предыдущей версии также распознаются.
- Можно назначить отдельные модели для фоновых задач: `YANDEX_STATE_MODEL` и `YANDEX_SUMMARY_MODEL` (или `STATE_MODEL` / `SUMMARY_MODEL`). Если переменные не заданы, используется основная модель.

### Настройки оптимизации (необязательно)

- `RPG_SUMMARY_THRESHOLD=24` — число диалоговых сообщений до сжатия истории.
- `RPG_KEEP_RECENT_MESSAGES=10` — сколько последних сообщений оставить дословно (допустимый диапазон 4–16).
- `YANDEX_STATE_MODEL` — модель для обновления листа персонажа.
- `YANDEX_SUMMARY_MODEL` — модель для архивирования истории.

Рекомендация: сначала развернуть без дополнительных переменных и проверить игру 20–30 ходов. Затем при желании назначить недорогую совместимую модель только для `YANDEX_STATE_MODEL` и/или `YANDEX_SUMMARY_MODEL`. Обязательно проверьте качество обновления квестов, предметов и NPC перед постоянным использованием.

## Changes in this patched build

- Rolling campaign memory: an existing summary is updated instead of freezing after the first summary.
- Character state is preserved conservatively when the state-extraction model returns incomplete/empty lists.
- XP is applied by the server from explicit `+N XP` lines in new assistant replies, and message event IDs prevent repeat awards.
- Level and next-level XP threshold are derived from XP on the server; level-up choices are left for the player rather than silently applied.
- Current character state is sent to the master as context each turn.
- API failures are shown as system errors and are not stored as master dialogue.
- Saves use atomic writes and keep a `.bak.json` backup of the previous save.
- Save JSON is versioned and malformed saves show a clear error.
- `/api/health` reports the configured model/provider (without exposing credentials).

## Notes

- Level-up HP/stat/ability choices are still handled through the game conversation after the server announces an available level. The engine does not silently choose a stat or ability.
- This is a patched prototype, not a fully deterministic D&D combat engine. Combat, spell effects, NPC motivations and quest logic still depend on the language model unless represented in the character state.
- Back up your `saves/` folder before upgrading the project.

### Управление сохранениями

В боковом меню игры есть пункт **«Управление сохранениями»**. Там можно переименовать сохранение (кнопка с карандашом) или удалить его (кнопка с корзиной). Удаление также удаляет резервную копию `.bak.json` и требует подтверждения. Имена сохранений допускают латинские буквы, цифры, дефис и подчёркивание.


## Аватары персонажей через Perchance

- Автоматическая генерация портрета использует Perchance Image API bridge (`https://perchance.org/perchance-ai-api`) без ключа Yandex и без дополнительных токенов DeepSeek.
- Внешность хранится в поле `appearance`; модуль состояния извлекает только детали, явно указанные игроком. Старые сохранения совместимы: если поля нет, берётся исходное описание игрока из истории.
- В окне портрета можно отредактировать описание на русском и повторно создать изображение. Русский текст передаётся как есть; к нему добавляются инструкции по композиции и качеству на английском.
- Кнопка «Открыть Perchance с описанием» копирует подготовленный промпт и открывает `https://perchance.org/ai-character-generator` для ручной генерации, если автоматический мост недоступен.
- Perchance — сторонний бесплатный веб-сервис; его интерфейс/API может меняться, а доступность генерации зависит от самого Perchance. При сбое приложение не переключается на платный API Яндекса.
