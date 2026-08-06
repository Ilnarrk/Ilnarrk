import random

def generate_animated_snake_svg(weeks=52, filename="snake.svg"):
    cols, rows = weeks, 7
    cell_size = 12
    cell_step = 16  # 12px ячейка + 4px отступ

    margin_left = 40    # место под дни недели слева
    margin_top = 28     # место под месяцы сверху
    margin_right = 10
    margin_bottom = 38  # место под легенду Less/More снизу

    grid_width = cols * cell_step
    grid_height = rows * cell_step

    total_width = margin_left + grid_width + margin_right
    total_height = margin_top + grid_height + margin_bottom

    border_color = "#1b1f230a"
    c_empty = "#ebedf0"
    c_levels = ["#ebedf0", "#9be9a8", "#40c463", "#30a14e", "#216e39"]
    snake_color = "purple"

    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    days = {0: "Mon", 2: "Wed", 4: "Fri"}  # как на GitHub — через строку

    # Атрибуты текста прямо в разметке (не зависят от <style>)
    label_attrs = 'font-family="Helvetica, Arial, sans-serif" font-size="10" fill="#57606a"'

    # 1. Генерация связного пути с ИНЕРЦИЕЙ
    random.seed(42)
    path_len = cols * rows

    current_x, current_y = 0, 0
    current_dir = (1, 0)
    path = [(current_x, current_y)]
    visited = set(path)

    for _ in range(path_len - 1):
        possible_moves = []
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = current_x + dx, current_y + dy
            if 0 <= nx < cols and 0 <= ny < rows and (nx, ny) not in visited:
                possible_moves.append((nx, ny, dx, dy))

        if not possible_moves:
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = current_x + dx, current_y + dy
                if 0 <= nx < cols and 0 <= ny < rows:
                    possible_moves.append((nx, ny, dx, dy))

        weighted_moves = []
        for nx, ny, dx, dy in possible_moves:
            weight = 15 if (dx, dy) == current_dir else 1
            weighted_moves.extend([(nx, ny, dx, dy)] * weight)

        next_move = random.choice(weighted_moves)
        nx, ny, dx, dy = next_move

        current_dir = (dx, dy)
        current_x, current_y = nx, ny
        path.append((nx, ny))
        visited.add((nx, ny))

    step_time = 100
    steps = len(path)
    anim_duration = steps * step_time

    snake_segments = [
        {"id": "s0", "size": 14.4, "rx": 4.5, "offset": 0.8, "delay_steps": 0}, # ГОЛОВА
        {"id": "s1", "size": 12.3, "rx": 4.1, "offset": 1.8, "delay_steps": 1},
        {"id": "s2", "size": 10.8, "rx": 3.6, "offset": 2.6, "delay_steps": 2},
        {"id": "s3", "size": 9.9,  "rx": 3.3, "offset": 3.0, "delay_steps": 3}, # ХВОСТ
    ]

    svg = []
    svg.append(f'<svg viewBox="0 0 {total_width} {total_height}" width="{total_width}" height="{total_height}" xmlns="http://www.w3.org/2000/svg">')
    svg.append('  <style>')
    svg.append(f'    :root {{ --cb:{border_color}; --cs:{snake_color}; --ce:{c_empty}; }}')
    svg.append(f'    .c {{ shape-rendering: geometricPrecision; fill: var(--ce); stroke-width: 1px; stroke: var(--cb); animation: none {anim_duration}ms linear infinite; width: {cell_size}px; height: {cell_size}px; rx: 2px; ry: 2px; }}')
    svg.append(f'    .s {{ shape-rendering: geometricPrecision; fill: var(--cs); animation: none {anim_duration}ms linear infinite; }}')

    # 2. Кейфреймы змейки (координаты УЖЕ с учетом полей)
    for seg in snake_segments:
        s_id = seg["id"]
        delay_steps = seg["delay_steps"]

        svg.append(f'    @keyframes {s_id} {{')
        for idx in range(steps):
            pct = round((idx / (steps - 1)) * 100, 2)
            path_idx = max(0, idx - delay_steps)
            c, r = path[path_idx]

            x = margin_left + c * cell_step
            y = margin_top + r * cell_step
            svg.append(f'      {pct}% {{ transform: translate({x}px, {y}px); }}')

        svg.append('    }')
        svg.append(f'    .s.{s_id} {{ animation-name: {s_id}; }}')

    # 3. Анимация съедения коммитов
    grid_matrix = {}
    for w in range(cols):
        for d in range(rows):
            weights = [0.50, 0.25, 0.13, 0.08, 0.04]
            level = random.choices(range(5), weights=weights)[0]
            grid_matrix[(w, d)] = level

            if level > 0:
                color = c_levels[level]
                eat_step = next((i for i, step in enumerate(path) if step == (w, d)), -1)

                if eat_step >= 0:
                    pct_eat = round((eat_step / (steps - 1)) * 100, 2)
                    pct_after = min(round(pct_eat + 0.1, 2), 100)
                    anim_name = f'c-{w}-{d}'

                    svg.append(f'    @keyframes {anim_name} {{')
                    svg.append(f'      0%, {pct_eat}% {{ fill: {color}; }}')
                    svg.append(f'      {pct_after}%, 100% {{ fill: var(--ce); }}')
                    svg.append('    }')
                    svg.append(f'    .cell-{w}-{d} {{ fill: {color}; animation-name: {anim_name}; }}')

    svg.append('  </style>')

    # 4. Месяцы сверху: Jan..Dec, равномерно по 52 неделям
    for i, name in enumerate(months):
        x = margin_left + round(i * cols / 12) * cell_step
        svg.append(f'  <text {label_attrs} x="{x}" y="{margin_top - 10}">{name}</text>')

    # 5. Дни недели слева (строго в своей колонке, не заезжая на сетку)
    for r, name in days.items():
        y = margin_top + r * cell_step + 11
        svg.append(f'  <text {label_attrs} x="2" y="{y}">{name}</text>')

    # 6. Клетки фона и коммитов (с полями)
    for w in range(cols):
        for d in range(rows):
            x = margin_left + w * cell_step + 2
            y = margin_top + d * cell_step + 2
            level = grid_matrix[(w, d)]

            if level > 0 and (w, d) in path:
                svg.append(f'  <rect class="c cell-{w}-{d}" x="{x}" y="{y}" />')
            else:
                fill_attr = f' fill="{c_levels[level]}"' if level > 0 else ''
                svg.append(f'  <rect class="c" x="{x}" y="{y}"{fill_attr} />')

    # 7. Змейка (x/y = offset, т.к. поля уже добавлены в translate-кейфреймы)
    for seg in snake_segments:
        s_id = seg["id"]
        size = seg["size"]
        offset = seg["offset"]
        rx = seg["rx"]
        svg.append(f'  <rect class="s {s_id}" x="{offset}" y="{offset}" width="{size}" height="{size}" rx="{rx}" ry="{rx}" />')

    # 8. Легенда Less / More внизу справа, квадратики тех же тонов, что и коммиты
    sq_size = 10
    sq_gap = 3
    sq_y = margin_top + grid_height + 14
    text_y = sq_y + 9

    right_edge = total_width - margin_right
    squares_width = 5 * sq_size + 4 * sq_gap
    squares_start = right_edge - 30 - squares_width   # 30px под слово "More"
    less_x = squares_start - 6

    svg.append(f'  <text {label_attrs} text-anchor="end" x="{less_x}" y="{text_y}">Less</text>')
    for i in range(5):
        x = squares_start + i * (sq_size + sq_gap)
        svg.append(f'  <rect x="{x}" y="{sq_y}" width="{sq_size}" height="{sq_size}" rx="2" ry="2" fill="{c_levels[i]}" stroke="{border_color}" stroke-width="1" />')
    svg.append(f'  <text {label_attrs} text-anchor="end" x="{right_edge}" y="{text_y}">More</text>')

    svg.append('</svg>')

    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))

    return filename

generate_animated_snake_svg(weeks=52)
