# Исследование методов удаления фона и выбор SOTA-подхода

**Проект:** Triumf Background Remover  
**Дата:** август 2026  
**Цель:** выбрать и обосновать state-of-the-art подход для self-hosted веб-сервиса удаления фона.

---

## 1. Постановка задачи

Удаление фона — это задача **выделения переднего плана (foreground segmentation / matting)** с выходом в формате PNG с alpha-каналом. Для production-сервиса важны:

| Критерий | Описание |
| --- | --- |
| Качество масок | Точные границы, волосы, полупрозрачные области, отверстия |
| Универсальность | Фото, товары, иллюстрации, аниме, портреты |
| Latency | Приемлемое время ответа на CPU (до нескольких секунд) |
| Эксплуатация | Простая установка, ONNX/CPU, без GPU как baseline |
| Лицензия | Возможность self-host без коммерческих ограничений |

Типичные ошибки «плохого» алгоритма:

- захват части объекта как фона (обрезание ушей, конечностей на иллюстрациях);
- включение текстурированного фона в маску;
- артефакты после морфологической постобработки («отклеенный угол», рваные края);
- путаница из-за уже существующего alpha-канала во входном PNG.

---

## 2. Обзор семейств методов

### 2.1. Классические методы

| Метод | Плюсы | Минусы |
| --- | --- | --- |
| Chroma key | Очень быстро, детерминированно | Только контролируемый однотонный фон |
| GrabCut / graph cuts | Хорошо для простых объектов | Нужна инициализация, слаб на волосах |
| Watershed / edge-based | Дёшево, интерпретируемо | Пересегментация на текстурах |
| Trimap matting | Высокая точность при trimap | Trimap нужно получать отдельно |

**Вывод:** классика годится как baseline, но не покрывает произвольные пользовательские загрузки.

### 2.2. Deep learning — основные семейства

| Семейство | Представители | Лучше всего для |
| --- | --- | --- |
| Salient Object Detection (SOD) | U²-Net, IS-Net | Один/несколько объектов на фото |
| Portrait matting | MODNet, P3M-Net | Лица и портреты в реальном времени |
| Dichotomous Image Segmentation (DIS) | IS-Net, BiRefNet, FP-DIS, MVANet | Категорийно-агностичные точные маски |
| Foundation / interactive | SAM, SAMA, ZIM | Promptable workflows, zero-shot |
| Commercial RMBG | BRIA RMBG 1.4/2.0 | E-commerce, mixed content |

---

## 3. SOTA и ключевые публикации (2020–2026)

### U²-Net (2020)
Nested U-structure для salient object detection. Хороший баланс качества и скорости. Широко используется через `rembg` (`u2net`, `u2netp`).

### DIS / IS-Net (2021–2023)
Dichotomous Image Segmentation на датасете DIS5K. Модели `isnet-general-use` и `isnet-anime` в rembg — практичная интеграция IS-Net для фото и **иллюстраций/аниме** соответственно.

### BiRefNet (2024)
Bilateral reference + high-resolution DIS. Модели `birefnet-general`, `birefnet-general-lite`, `birefnet-portrait` — SOTA-уровень на сложных границах, но тяжелее по памяти и latency.

### BRIA RMBG 1.4 / 2.0 (2024–2025)
Коммерчески обученные модели для широкого спектра категорий (товары, люди, графика). `bria-rmbg` в rembg — **лучший универсальный выбор** для mixed uploads на CPU.

### MODNet (2020)
Trimap-free portrait matting, real-time. Отлично для людей, но узкая область применения.

### SAM / SAMA / ZIM (2023–2026)
Foundation segmentation + matting. Высокое качество и гибкость, но высокая стоимость inference и сложнее в self-host.

---

## 4. Сравнительная таблица моделей

| Модель | Качество | Скорость (CPU) | Универсальность | Иллюстрации | Self-host |
| --- | --- | --- | --- | --- | --- |
| GrabCut | ★★☆☆☆ | ★★★★★ | ★★☆☆☆ | ★☆☆☆☆ | ★★★★★ |
| U²-Net (`u2net`) | ★★★☆☆ | ★★★★☆ | ★★★☆☆ | ★★☆☆☆ | ★★★★★ |
| IS-Net general (`isnet-general-use`) | ★★★★☆ | ★★★☆☆ | ★★★★☆ | ★★☆☆☆ | ★★★★★ |
| IS-Net anime (`isnet-anime`) | ★★★★☆ | ★★★☆☆ | ★★☆☆☆ | ★★★★★ | ★★★★★ |
| BiRefNet lite | ★★★★★ | ★★☆☆☆ | ★★★★☆ | ★★★☆☆ | ★★★★☆ |
| BRIA RMBG (`bria-rmbg`) | ★★★★★ | ★★★☆☆ | ★★★★★ | ★★★★☆ | ★★★★☆ |
| MODNet | ★★★★☆ | ★★★★★ | ★★☆☆☆ | ★☆☆☆☆ | ★★★★☆ |
| SAM / ZIM | ★★★★★ | ★☆☆☆☆ | ★★★★★ | ★★★★☆ | ★★☆☆☆ |

---

## 5. Анализ проблемы на реальном примере

На иллюстрации (белый кот на фиолетовом фоне с точками) модель **`isnet-general-use`** дала неудовлетворительный результат:

- обрезаны уши и нижняя часть головы;
- в маску попала только центральная «овал-область» лица;
- морфологическое сглаживание (`post_process_mask`) добавило артефакты.

**Причины:**

1. **Неверный выбор модели** — general-use модель оптимизирована под фото, а не под flat/anime-графику с однотонными заливками.
2. **Агрессивная post-processing** — `MORPH_OPEN` + blur на бинарной маске искажают плоские контуры.
3. **Вход с alpha-каналом** — без flatten RGBA→RGB модель может некорректно интерпретировать прозрачность.

---

## 6. Выбранный SOTA для реализации

### Основной стек

```
rembg + ONNX Runtime + BRIA RMBG (default)
```

### Обоснование выбора

| Решение | Почему |
| --- | --- |
| `rembg` | Зрелая Python-обёртка, 15+ моделей, ONNX, CPU-first |
| `bria-rmbg` по умолчанию | Лучшее универсальное качество для mixed uploads |
| `isnet-anime` для иллюстраций | Специализация под anime/flat art — решает кейс с котом |
| `post_process_mask=false` | Меньше артефактов на иллюстрациях; опционально в UI |
| `prepare_for_inference()` | Flatten RGBA на белый фон перед inference |
| Alpha matting (опционально) | Уточнение краёв на фото с волосами/полупрозрачностью |

### Архитектурный принцип

Порт `BackgroundRemover` изолирует inference от API/UI — модель можно заменить на BiRefNet-full, hosted BRIA 2.0 или GPU-worker без изменения контракта.

---

## 7. Рекомендации по выбору модели (для пользователя)

| Тип изображения | Модель | Настройки |
| --- | --- | --- |
| Фото, товары, mixed | `bria-rmbg` | alpha matting при волосах/мехе |
| Иллюстрации, аниме, стикеры | `isnet-anime` | post_process_mask выключен |
| Сложные границы, детали | `birefnet-general-lite` | медленнее, больше RAM |
| Быстрый preview | `u2net` | минимальные настройки |

---

## 8. Реализованный сервис

### API

- `GET /api/health` — проверка доступности
- `GET /api/models` — каталог моделей
- `POST /api/remove-background?model=&alpha_matting=&post_process_mask=` — обработка

### Pipeline

1. Валидация upload (тип, размер, пиксели)
2. `prepare_for_inference()` — EXIF + RGB flatten
3. Inference через rembg session (кэш per model per process)
4. PNG с alpha, без сохранения на диск

### UI

- Drag & drop, preview, выбор модели, toggles для matting/post-process

---

## 9. Ограничения и дальнейшее развитие

| Ограничение | Mitigation |
| --- | --- |
| CPU latency 2–15 с на больших изображениях | Resize перед inference, GPU worker |
| Память ~500MB–2GB на модель | 1 worker, lazy session load |
| BRIA license для commercial scale | Проверить terms; fallback на IS-Net |
| Нет auto-detect типа изображения | Эвристика или classifier → model routing |

**Roadmap:** auto-routing (photo vs illustration), GPU inference service, async queue для batch.

---

## 10. Источники

- U²-Net: https://huggingface.co/papers/2005.09007
- DIS / DIS5K: https://xuebinqin.github.io/dis/
- BiRefNet: https://github.com/ZhengPeng7/BiRefNet
- BRIA RMBG 1.4: https://huggingface.co/briaai/RMBG-1.4
- BRIA RMBG 2.0: https://huggingface.co/briaai/RMBG-2.0
- MODNet: https://github.com/ZHKKKe/MODNet
- rembg: https://github.com/danielgatis/rembg
- SAMA (AAAI 2026): https://ojs.aaai.org/index.php/AAAI/article/view/37382
- ZIM (ICCV 2025): https://openaccess.thecvf.com/content/ICCV2025/html/Kim_ZIM_Zero-Shot_Image_Matting_for_Anything_ICCV_2025_paper.html
