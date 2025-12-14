import flet as ft
import time
from collections import deque
import threading
import os

# ========================================================================
# THUẬT TOÁN DFS/BFS VÀ TÌM ĐƯỜNG
# ========================================================================

adj = {}
visited = {}
a = []
n, m = 0, 0
dx = [-1, 0, 0, 1]
dy = [0, -1, 1, 0]


def dfs_graph(u, callback=None):
    global visited, adj
    if callback:
        callback(u, 'visit')
    visited[u] = True
    for v in adj[u]:
        if not visited[v]:
            dfs_graph(v, callback)


def bfs_graph(u, callback=None):
    global visited, adj
    q = deque()
    q.append(u)
    visited[u] = True
    while q:
        v = q.popleft()
        if callback:
            callback(v, 'visit')
        for x in adj[v]:
            if not visited[x]:
                q.append(x)
                visited[x] = True


def dfs_matrix(i, j, callback=None):
    global a, n, m, dx, dy
    if callback:
        callback(i, j, 'visit')
    a[i][j] = 2
    for k in range(4):
        i1 = i + dx[k]
        j1 = j + dy[k]
        if 0 <= i1 < n and 0 <= j1 < m and a[i1][j1] == 0:
            dfs_matrix(i1, j1, callback)


def bfs_matrix(i, j, callback=None):
    global a, n, m, dx, dy
    q = deque()
    q.append((i, j))
    a[i][j] = 2
    if callback:
        callback(i, j, 'visit')
    while q:
        top = q.popleft()
        for k in range(4):
            i1 = top[0] + dx[k]
            j1 = top[1] + dy[k]
            if 0 <= i1 < n and 0 <= j1 < m and a[i1][j1] == 0:
                if callback:
                    callback(i1, j1, 'visit')
                q.append((i1, j1))
                a[i1][j1] = 2


def find_shortest_path(start_i, start_j, end_i, end_j, callback=None):
    global a, n, m, dx, dy
    
    d = [[-1] * m for _ in range(n)]
    q = deque()
    q.append((start_i, start_j))
    d[start_i][start_j] = 0
    a[start_i][start_j] = 0 
    
    found = False
    while q and not found:
        top = q.popleft()
        ci, cj = top
        if callback:
            callback(ci, cj, 'explore')
        if ci == end_i and cj == end_j:
            found = True
            break
        for k in range(4):
            ni = ci + dx[k]
            nj = cj + dy[k]
            if (0 <= ni < n and 0 <= nj < m and 
                d[ni][nj] == -1 and a[ni][nj] != 1):
                d[ni][nj] = d[ci][cj] + 1
                q.append((ni, nj))
    
    if not found or d[end_i][end_j] == -1:
        return None, 0
    
    path = []
    ci, cj = end_i, end_j
    path.append((ci, cj))
    
    while ci != start_i or cj != start_j:
        for k in range(4):
            ni = ci + dx[k]
            nj = cj + dy[k]
            if 0 <= ni < n and 0 <= nj < m:
                if d[ni][nj] == d[ci][cj] - 1:
                    ci, cj = ni, nj
                    path.append((ci, cj))
                    break
    
    path.reverse()
    return path, len(path) - 1


# ========================================================================
# FLET APP
# ========================================================================

def main(page: ft.Page):
    page.title = "Trình Duyệt Đồ Thị & Mê Cung"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    page.bgcolor = "#0f172a"
    
    # State variables
    app_state = {
        'mode': 'graph',
        'algorithm': 'dfs',
        'is_running': False,
        'nodes': [],
        'edges': [],
        'selected_node': None,
        'visited_nodes': [],
        'current_node': None,
        'cell_buttons': [],
        'start_point': None,
        'end_point': None,
        'selecting_mode': None,
        'cell_size': 40,
        'canvas_width': 1200,
        'canvas_height': 650,
    }
    
    # UI Components
    graph_canvas = ft.Stack([], expand=True)
    matrix_container_content = ft.Column([], scroll=ft.ScrollMode.AUTO, spacing=0)
    
    def show_message(title, message):
        def close_dlg(e):
            dlg.open = False
            page.update()
        
        dlg = ft.AlertDialog(
            title=ft.Text(title),
            content=ft.Text(message),
            actions=[ft.TextButton("OK", on_click=close_dlg)],
        )
        page.dialog = dlg
        dlg.open = True
        page.update()
    
    # Graph functions
    def draw_graph():
        graph_canvas.controls.clear()
        
        # Draw edges using multiple small circles to form a line
        for edge in app_state['edges']:
            try:
                from_node = next(n for n in app_state['nodes'] if n[0] == edge[0])
                to_node = next(n for n in app_state['nodes'] if n[0] == edge[1])
                
                x1, y1 = from_node[1], from_node[2]
                x2, y2 = to_node[1], to_node[2]
                
                # Calculate number of points based on distance
                import math
                distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                num_points = int(distance / 3)  # One point every 3 pixels
                
                if num_points > 0:
                    for i in range(num_points + 1):
                        t = i / num_points
                        x = x1 + (x2 - x1) * t
                        y = y1 + (y2 - y1) * t
                        
                        point = ft.Container(
                            width=4,
                            height=4,
                            bgcolor="#94a3b8",
                            border_radius=2,
                            left=x - 2,
                            top=y - 2
                        )
                        graph_canvas.controls.append(point)
            except StopIteration:
                continue
        
        # Draw nodes
        for node in app_state['nodes']:
            node_id, x, y = node
            
            if app_state['current_node'] == node_id:
                color = "#ef4444"
            elif node_id in app_state['visited_nodes']:
                color = "#10b981"
            else:
                color = "#3b82f6"
            
            def make_click_handler(nid):
                def handler(e):
                    on_node_click(nid)
                return handler
            
            node_widget = ft.Container(
                content=ft.Stack([
                    ft.Container(
                        width=50, height=50,
                        border_radius=25,
                        bgcolor=color,
                        border=ft.border.all(3, "#0b1220")
                    ),
                    ft.Container(
                        content=ft.Text(str(node_id), color="white", size=16, weight=ft.FontWeight.BOLD),
                        width=50, height=50,
                        alignment=ft.alignment.center
                    )
                ]),
                left=x-25, top=y-25,
                on_click=make_click_handler(node_id)
            )
            graph_canvas.controls.append(node_widget)
        
        page.update()
    
    def on_canvas_click(e: ft.TapEvent):
        if app_state['is_running'] or app_state['mode'] != 'graph':
            return
        
        x, y = e.local_x, e.local_y
        
        # Check if clicked on existing node
        clicked_on_node = False
        for node in app_state['nodes']:
            node_id, nx, ny = node
            if ((nx - x) ** 2 + (ny - y) ** 2) ** 0.5 < 25:
                clicked_on_node = True
                break
        
        if not clicked_on_node:
            new_id = len(app_state['nodes']) + 1
            app_state['nodes'].append((new_id, x, y))
            graph_help_label.value = f"✅ Đã tạo đỉnh {new_id}! Tiếp tục click để tạo thêm đỉnh hoặc click vào 2 đỉnh để nối"
            graph_help_label.color = "#10b981"
            draw_graph()
            # Reset về ghi chú mặc định sau 2 giây
            def reset_label():
                time.sleep(2)
                if app_state['mode'] == 'graph':
                    graph_help_label.value = "💡 Click vào canvas để tạo đỉnh • Click vào 2 đỉnh liên tiếp để nối cạnh"
                    graph_help_label.color = "#fbbf24"
                    page.update()
            threading.Thread(target=reset_label, daemon=True).start()
    
    def on_node_click(node_id):
        if app_state['is_running']:
            return
        
        if app_state['selected_node'] is None:
            app_state['selected_node'] = node_id
            graph_help_label.value = f"✅ Đã chọn đỉnh {node_id}! Bây giờ click vào đỉnh khác để nối cạnh"
            graph_help_label.color = "#10b981"
            page.update()
        elif app_state['selected_node'] != node_id:
            edge_exists = any((e[0] == app_state['selected_node'] and e[1] == node_id) or
                            (e[0] == node_id and e[1] == app_state['selected_node'])
                            for e in app_state['edges'])
            if not edge_exists:
                app_state['edges'].append((app_state['selected_node'], node_id))
                graph_help_label.value = f"✅ Đã nối cạnh giữa đỉnh {app_state['selected_node']} và {node_id}!"
                graph_help_label.color = "#10b981"
                draw_graph()
            else:
                graph_help_label.value = f"⚠️ Cạnh giữa đỉnh {app_state['selected_node']} và {node_id} đã tồn tại!"
                graph_help_label.color = "#f59e0b"
                page.update()
            app_state['selected_node'] = None
            # Reset về ghi chú mặc định sau 2 giây
            def reset_label():
                time.sleep(2)
                if app_state['mode'] == 'graph':
                    graph_help_label.value = "💡 Click vào canvas để tạo đỉnh • Click vào 2 đỉnh liên tiếp để nối cạnh"
                    graph_help_label.color = "#fbbf24"
                    page.update()
            threading.Thread(target=reset_label, daemon=True).start()
    
    # Matrix functions
    def init_matrix(rows, cols):
        global n, m, a
        n, m = rows, cols
        a = [[0 for _ in range(m)] for _ in range(n)]
        app_state['cell_buttons'] = []
        app_state['start_point'] = None
        app_state['end_point'] = None
        
        # Tính kích thước ô lớn hơn
        available_width = 1150
        available_height = 600
        cell_w = available_width // m if m > 0 else 50
        cell_h = available_height // n if n > 0 else 50
        cell_size = min(cell_w, cell_h, 80)  # Tăng từ 60 lên 80
        cell_size = max(cell_size, 25)  # Tăng từ 20 lên 25
        app_state['cell_size'] = cell_size
        
        draw_matrix()
    
    def draw_matrix():
        matrix_container_content.controls.clear()
        app_state['cell_buttons'] = []
        
        for i in range(n):
            row = ft.Row([], spacing=1, tight=True)
            row_buttons = []
            for j in range(m):
                def make_click_handler(ri, rj):
                    def handler(e):
                        on_cell_click(ri, rj)
                    return handler
                
                color = get_cell_color(i, j)
                
                cell = ft.Container(
                    width=app_state['cell_size'],
                    height=app_state['cell_size'],
                    bgcolor=color,
                    border=ft.border.all(1, "#cbd5e1"),
                    on_click=make_click_handler(i, j)
                )
                row.controls.append(cell)
                row_buttons.append(cell)
            
            app_state['cell_buttons'].append(row_buttons)
            matrix_container_content.controls.append(row)
        
        page.update()
    
    def get_cell_color(i, j):
        if (i, j) == app_state['start_point']:
            return "#3b82f6"
        elif (i, j) == app_state['end_point']:
            return "#ef4444"
        elif a[i][j] == 1:
            return "#0b1220"
        elif a[i][j] == 2:
            return "#10b981"
        else:
            return "white"
    
    def on_cell_click(i, j):
        global a
        if app_state['is_running']:
            return
        
        if app_state['algorithm'] == 'path' and app_state['selecting_mode']:
            select_point(i, j)
        else:
            toggle_cell(i, j)
    
    def select_point(i, j):
        global a
        if a[i][j] == 1:
            show_message("Cảnh báo", "Không thể chọn ô tường làm điểm bắt đầu/kết thúc!")
            return
        
        if app_state['selecting_mode'] == 'start':
            if app_state['start_point'] and app_state['start_point'] != app_state['end_point']:
                old_i, old_j = app_state['start_point']
                a[old_i][old_j] = 0
            
            app_state['start_point'] = (i, j)
            a[i][j] = 0
            app_state['selecting_mode'] = None
            help_label.value = "✅ Đã chọn điểm bắt đầu! Bây giờ chọn điểm kết thúc hoặc nhấn Chạy"
            
        elif app_state['selecting_mode'] == 'end':
            if (i, j) == app_state['start_point']:
                show_message("Cảnh báo", "Điểm kết thúc không thể trùng với điểm bắt đầu!")
                return
            
            if app_state['end_point'] and app_state['end_point'] != app_state['start_point']:
                old_i, old_j = app_state['end_point']
                a[old_i][old_j] = 0
            
            app_state['end_point'] = (i, j)
            a[i][j] = 0
            app_state['selecting_mode'] = None
            help_label.value = "✅ Đã chọn điểm kết thúc! Nhấn Chạy để tìm đường đi ngắn nhất"
        
        draw_matrix()
    
    def toggle_cell(i, j):
        global a
        if (i, j) == app_state['start_point'] or (i, j) == app_state['end_point']:
            return
        
        if a[i][j] == 0:
            a[i][j] = 1
        elif a[i][j] in [1, 2]:
            a[i][j] = 0
        
        app_state['cell_buttons'][i][j].bgcolor = get_cell_color(i, j)
        page.update()
    
    # Algorithm execution
    def run_algorithm(e):
        if app_state['is_running']:
            return
        
        app_state['is_running'] = True
        app_state['visited_nodes'] = []
        app_state['current_node'] = None
        
        thread = threading.Thread(target=execute_algorithm)
        thread.daemon = True
        thread.start()
    
    def execute_algorithm():
        global adj, visited, a, n, m
        
        try:
            if app_state['mode'] == 'graph':
                if not app_state['nodes']:
                    show_message("Cảnh báo", "Vui lòng thêm ít nhất một đỉnh!")
                    app_state['is_running'] = False
                    return
                
                adj = {node[0]: [] for node in app_state['nodes']}
                visited = {node[0]: False for node in app_state['nodes']}
                
                for edge in app_state['edges']:
                    adj[edge[0]].append(edge[1])
                    adj[edge[1]].append(edge[0])
                
                u = app_state['nodes'][0][0]
                
                def callback(node, action):
                    if node not in app_state['visited_nodes']:
                        app_state['visited_nodes'].append(node)
                    app_state['current_node'] = node
                    draw_graph()
                    time.sleep(0.35)
                
                if app_state['algorithm'] == 'dfs':
                    dfs_graph(u, callback)
                else:
                    bfs_graph(u, callback)
            
            else:  # matrix mode
                if app_state['algorithm'] == 'path':
                    if not app_state['start_point'] or not app_state['end_point']:
                        show_message("Cảnh báo", "Vui lòng chọn điểm bắt đầu và điểm kết thúc!")
                        app_state['is_running'] = False
                        return
                    
                    for i in range(n):
                        for j in range(m):
                            if a[i][j] == 2:
                                a[i][j] = 0
                    
                    si, sj = app_state['start_point']
                    ei, ej = app_state['end_point']
                    a[si][sj] = 0
                    a[ei][ej] = 0
                    
                    def callback(i, j, action):
                        if (i, j) != app_state['start_point'] and (i, j) != app_state['end_point']:
                            if i < len(app_state['cell_buttons']) and j < len(app_state['cell_buttons'][i]):
                                app_state['cell_buttons'][i][j].bgcolor = "#fbbf24"
                                page.update()
                        time.sleep(0.03)
                    
                    path, distance = find_shortest_path(si, sj, ei, ej, callback)
                    
                    if path:
                        time.sleep(0.3)
                        for pi, pj in path:
                            if (pi, pj) != app_state['start_point'] and (pi, pj) != app_state['end_point']:
                                if pi < len(app_state['cell_buttons']) and pj < len(app_state['cell_buttons'][pi]):
                                    app_state['cell_buttons'][pi][pj].bgcolor = "#10b981"
                                    page.update()
                                    time.sleep(0.05)
                        
                        show_message("Kết quả", 
                                   f"✅ Tìm thấy đường đi!\nĐộ dài đường đi: {distance} bước\nSố ô đi qua: {len(path)} ô")
                    else:
                        show_message("Kết quả", "❌ Không tìm thấy đường đi!")
                
                else:  # DFS/BFS
                    start_i, start_j = -1, -1
                    for i in range(n):
                        for j in range(m):
                            if a[i][j] == 0:
                                start_i, start_j = i, j
                                break
                        if start_i != -1:
                            break
                    
                    if start_i == -1:
                        show_message("Cảnh báo", "Vui lòng thêm ít nhất một ô đường đi!")
                        app_state['is_running'] = False
                        return
                    
                    def callback(i, j, action):
                        if i < len(app_state['cell_buttons']) and j < len(app_state['cell_buttons'][i]):
                            app_state['cell_buttons'][i][j].bgcolor = "#10b981"
                            page.update()
                        time.sleep(0.06)
                    
                    if app_state['algorithm'] == 'dfs':
                        dfs_matrix(start_i, start_j, callback)
                    else:
                        bfs_matrix(start_i, start_j, callback)
        
        finally:
            app_state['is_running'] = False
            app_state['current_node'] = None
            if app_state['mode'] == 'graph':
                draw_graph()
    
    def reset(e):
        global visited, adj, a, n, m
        
        if app_state['mode'] == 'graph':
            app_state['nodes'] = []
            app_state['edges'] = []
            app_state['selected_node'] = None
            graph_canvas.controls.clear()
            adj = {}
            visited = {}
            page.update()
        else:
            app_state['start_point'] = None
            app_state['end_point'] = None
            app_state['selecting_mode'] = None
            try:
                rows = int(row_input.value)
                cols = int(col_input.value)
                init_matrix(rows, cols)
            except:
                init_matrix(12, 16)
        
        app_state['visited_nodes'] = []
        app_state['current_node'] = None
        app_state['is_running'] = False
    
    # UI Event Handlers
    def change_mode(mode):
        app_state['mode'] = mode
        reset(None)
        
        if mode == 'graph':
            graph_btn.bgcolor = "#1e40af"
            matrix_btn.bgcolor = "#0f172a"
            graph_container.visible = True
            matrix_container.visible = False
            graph_help_label.value = "💡 Click vào canvas để tạo đỉnh • Click vào 2 đỉnh liên tiếp để nối cạnh"
            graph_help_label.color = "#fbbf24"
        else:
            matrix_btn.bgcolor = "#1e40af"
            graph_btn.bgcolor = "#0f172a"
            graph_container.visible = False
            matrix_container.visible = True
            init_matrix(12, 16)
        
        page.update()
    
    def set_algorithm(algo):
        if app_state['is_running']:
            return
        app_state['algorithm'] = algo
        
        if algo == 'path':
            app_state['start_point'] = None
            app_state['end_point'] = None
            app_state['selecting_mode'] = None
            path_controls.visible = True
            if app_state['mode'] == 'matrix' and len(app_state['cell_buttons']) > 0:
                draw_matrix()
        else:
            path_controls.visible = False
        
        update_algorithm_buttons()
        page.update()
    
    def update_algorithm_buttons():
        selected = "#10b981"
        unselected = "#0b1220"
        
        dfs_btn.bgcolor = selected if app_state['algorithm'] == 'dfs' else unselected
        bfs_btn.bgcolor = selected if app_state['algorithm'] == 'bfs' else unselected
        path_btn.bgcolor = selected if app_state['algorithm'] == 'path' else unselected
        page.update()
    
    def set_selecting_mode(mode):
        if app_state['is_running']:
            return
        app_state['selecting_mode'] = mode
        if mode == 'start':
            help_label.value = "📍 Click vào ô để chọn ĐIỂM BẮT ĐẦU (màu xanh dương)"
        else:
            help_label.value = "🎯 Click vào ô để chọn ĐIỂM KẾT THÚC (màu đỏ)"
        page.update()
    
    def update_matrix_size(e):
        if not app_state['is_running'] and app_state['mode'] == 'matrix':
            try:
                rows = int(row_input.value)
                cols = int(col_input.value)
                if rows > 0 and cols > 0:
                    init_matrix(rows, cols)
            except:
                pass
    
    # Build UI
    graph_btn = ft.ElevatedButton(
        "📊 Đồ Thị",
        on_click=lambda e: change_mode('graph'),
        bgcolor="#1e40af",
        color="white",
        width=130,
        height=40
    )
    
    matrix_btn = ft.ElevatedButton(
        "🧩 Mê Cung",
        on_click=lambda e: change_mode('matrix'),
        bgcolor="#0f172a",
        color="white",
        width=130,
        height=40
    )
    
    dfs_btn = ft.ElevatedButton("DFS", on_click=lambda e: set_algorithm('dfs'), width=90, height=35)
    bfs_btn = ft.ElevatedButton("BFS", on_click=lambda e: set_algorithm('bfs'), width=90, height=35)
    path_btn = ft.ElevatedButton("Tìm Đường", on_click=lambda e: set_algorithm('path'), width=110, height=35)
    
    update_algorithm_buttons()
    
    row_input = ft.TextField(value="12", width=70, text_align=ft.TextAlign.CENTER, on_submit=update_matrix_size)
    col_input = ft.TextField(value="16", width=70, text_align=ft.TextAlign.CENTER, on_submit=update_matrix_size)
    
    help_label = ft.Text("💡 Click ô để chuyển thành tường (đen) hoặc đường đi (trắng)", color="#fbbf24", size=12)
    graph_help_label = ft.Text("💡 Click vào canvas để tạo đỉnh • Click vào 2 đỉnh liên tiếp để nối cạnh", color="#fbbf24", size=13, weight=ft.FontWeight.BOLD)
    
    path_controls = ft.Row([
        ft.ElevatedButton("📍 Chọn Điểm Bắt Đầu", on_click=lambda e: set_selecting_mode('start'), bgcolor="#3b82f6", color="white", height=35),
        ft.ElevatedButton("🎯 Chọn Điểm Kết Thúc", on_click=lambda e: set_selecting_mode('end'), bgcolor="#ef4444", color="white", height=35),
    ], visible=False, alignment=ft.MainAxisAlignment.CENTER)
    
    # Graph container
    graph_container = ft.Container(
        content=ft.Column([
            ft.Container(
                content=graph_help_label,
                bgcolor="#1e293b",
                padding=10,
                border_radius=5,
                alignment=ft.alignment.center
            ),
            ft.Container(
                content=ft.GestureDetector(
                    content=graph_canvas,
                    on_tap_down=on_canvas_click
                ),
                bgcolor="#e6eef8",
                expand=True
            )
        ], spacing=8),
        expand=True,
        visible=True,
        padding=10
    )
    
    # Matrix container
    matrix_container = ft.Container(
        content=ft.Column([
            ft.Container(
                content=ft.Row([
                    ft.Text("Kích thước mê cung:", color="white", weight=ft.FontWeight.BOLD, size=13),
                    ft.Text("Hàng:", color="white", size=12),
                    row_input,
                    ft.Text("Cột:", color="white", size=12),
                    col_input,
                    ft.ElevatedButton("Cập nhật", on_click=update_matrix_size, height=35, bgcolor="#3b82f6", color="white")
                ], alignment=ft.MainAxisAlignment.CENTER),
                bgcolor="#1e293b",
                padding=10,
                border_radius=5
            ),
            help_label,
            path_controls,
            ft.Container(
                content=ft.Container(
                    content=matrix_container_content,
                    alignment=ft.alignment.center,
                ),
                bgcolor="#e6eef8",
                padding=15,
                expand=True,
                border_radius=5
            )
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
        visible=False,
        expand=True,
        padding=10
    )
    
    page.add(
        ft.Column([
            ft.Container(
                content=ft.Text("🔍 Trình Duyệt Đồ Thị & Mê Cung + Tìm Đường", 
                               size=22, weight=ft.FontWeight.BOLD, color="white"),
                bgcolor="#0b1220",
                padding=15,
                alignment=ft.alignment.center
            ),
            ft.Container(
                content=ft.Row([
                    ft.Row([
                        graph_btn, 
                        matrix_btn,
                    ], spacing=10),
                    ft.Container(width=30),
                    ft.Row([
                        ft.Text("Thuật toán:", color="white", size=13, weight=ft.FontWeight.BOLD),
                        dfs_btn, bfs_btn, path_btn
                    ], spacing=8),
                    ft.Container(expand=True),
                    ft.Row([
                        ft.ElevatedButton("▶ Chạy", on_click=run_algorithm, bgcolor="#059669", color="white", width=130, height=45),
                        ft.ElevatedButton("🔄 Reset", on_click=reset, bgcolor="#dc2626", color="white", width=130, height=45),
                    ], spacing=10),
                ], alignment=ft.MainAxisAlignment.START),
                bgcolor="#071028",
                padding=15
            ),
            ft.Container(
                content=ft.Stack([graph_container, matrix_container]),
                expand=True,
                padding=5
            )
        ], spacing=0, expand=True)
    )


# ========================================================================
# MAIN - WEB DEPLOYMENT CONFIG
# ========================================================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    ft.app(
        target=main, 
        port=port,
        host="0.0.0.0",
        view=ft.AppView.WEB_BROWSER
    )