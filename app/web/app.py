import base64
import io
import pandas as pd
import json
from dash import Dash, dcc, html, Input, Output, State, ctx, ALL, no_update
import plotly.graph_objs as go
from dash.exceptions import PreventUpdate

# Цвета радуги
RAINBOW_COLORS = ['red', 'orange', 'yellow', 'green', 'blue', 'indigo', 'violet']

app = Dash(__name__, suppress_callback_exceptions=True)

app.layout = html.Div([
    # Загрузка файла
    dcc.Upload(
        id='upload-data',
        children=html.Div(['Drag and Drop or ', html.A('Select CSV File')]),
        style={'width': '100%', 'height': '60px', 'lineHeight': '60px',
               'borderWidth': '1px', 'borderStyle': 'dashed', 'borderRadius': '5px',
               'textAlign': 'center', 'margin': '10px'},
        multiple=False
    ),
    # Имя файла и кнопка открепить
    html.Div(id='file-info', style={'margin': '10px 0'}),
    # Выбор разделителя
    html.Div([
        html.Label('CSV Separator:'),
        dcc.Input(id='csv-separator', value=',', type='text', style={'width': '50px'})
    ], style={'margin': '10px 0'}),
    # Выбор колонок
    html.Div(id='column-select-container', style={'display': 'none'}, children=[
        html.Label('Select X axis column:'),
        dcc.Dropdown(id='xaxis-column'),
        html.Label('Select Y axis column:'),
        dcc.Dropdown(id='yaxis-column'),
        html.Label('Select color column:'),
        dcc.Dropdown(id='color-column'),
    ]),
    # Модуль редактирования условий
    html.Div(id='color-condition-module', style={'display': 'none'}),
    html.Button('Plot Graph', id='plot-button', n_clicks=0, style={'margin': '10px 0'}),
    dcc.Graph(id='graph'),
    html.Div(id='error-message', style={'color': 'red'}),
    dcc.Store(id='stored-df'),
    dcc.Store(id='color-conditions', data=[]),
])


# Парсинг CSV с учётом разделителя
def parse_contents(contents, separator):
    if contents is None:
        return None
        
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')), sep=separator)
        return df
    except Exception as e:
        print(f"Error parsing CSV: {str(e)}")
        return None


# Отображение имени файла и кнопки открепить
@app.callback(
    Output('file-info', 'children'),
    Input('upload-data', 'filename'),
    prevent_initial_call=True
)
def show_file_info(filename):
    if filename:
        return html.Div([
            html.Span(f'Файл: {filename}', style={'fontWeight': 'bold'}),
            html.Button('Открепить', id='detach-file', n_clicks=0, style={'marginLeft': '10px'})
        ])
    return ""

# Сброс состояния при откреплении файла
@app.callback(
    Output('upload-data', 'contents', allow_duplicate=True),
    Output('upload-data', 'filename', allow_duplicate=True),
    Output('file-info', 'children', allow_duplicate=True),
    Output('column-select-container', 'style', allow_duplicate=True),
    Output('stored-df', 'data', allow_duplicate=True),
    Output('error-message', 'children', allow_duplicate=True),
    Output('color-condition-module', 'style', allow_duplicate=True),
    Input('detach-file', 'n_clicks'),
    prevent_initial_call=True
)
def detach_file(n):
    if n:
        return None, None, "", {'display': 'none'}, None, "", {'display': 'none'}
    raise PreventUpdate

# Основной колбэк для обработки файла и разделителя
@app.callback(
    Output('column-select-container', 'style'),
    Output('xaxis-column', 'options'),
    Output('yaxis-column', 'options'),
    Output('color-column', 'options'),
    Output('stored-df', 'data', allow_duplicate=True),
    Output('error-message', 'children', allow_duplicate=True),
    Input('upload-data', 'contents'),
    Input('csv-separator', 'value'),
    State('upload-data', 'filename'),
    prevent_initial_call=True
)
def update_dropdowns(contents, separator, filename):
    if contents is None:
        return {'display': 'none'}, [], [], [], None, ""
    
    try:
        df = parse_contents(contents, separator)
        if df is None or df.empty:
            return {'display': 'none'}, [], [], [], None, "Ошибка парсинга файла. Проверьте разделитель."
        
        options = [{'label': col, 'value': col} for col in df.columns]
        return {'display': 'block'}, options, options, options, df.to_json(date_format='iso', orient='split'), ""
    
    except Exception as e:
        print(f"Error in update_dropdowns: {str(e)}")
        return {'display': 'none'}, [], [], [], None, f"Ошибка: {str(e)}"

# Генерация условия
# @app.callback(
#     Output('color-condition-module', 'children'),
#     Output('color-condition-module', 'style'),
#     Output('color-conditions', 'data'),
#     Input('color-column', 'value'),
#     State('stored-df', 'data'),
#     prevent_initial_call=True
# )
# def generate_conditions(color_col, df_json):
    if not color_col or not df_json:
        return "", {'display': 'none'}, []
    
    try:
        # Чтение данных из JSON
        df = pd.read_json(io.StringIO(df_json), orient='split')
        
        # Получение уникальных значений
        unique_vals = df[color_col].astype(str).unique()
        
        # Ограничение до 7 значений
        if len(unique_vals) > 7:
            unique_vals = unique_vals[:7]
            message = html.Div("Отображаются первые 7 уникальных значений", style={'color': 'orange', 'margin': '10px 0'})
        else:
            message = None
        
        # Создание условий и компонентов интерфейса
        conditions = []
        condition_components = []
        
        for i, val in enumerate(unique_vals):
            condition = {
                'value': val,
                'color': RAINBOW_COLORS[i % len(RAINBOW_COLORS)]
            }
            conditions.append(condition)
            
            condition_components.append(
                html.Div([
                    dcc.Input(
                        value=val,
                        id={'type': 'condition-input', 'index': i},
                        style={
                            'marginRight': '10px', 
                            'width': '200px',
                            'border': f'2px solid {condition["color"]}'
                        },
                        readOnly=True
                    ),
                    html.Span(
                        f"Цвет: {condition['color']}",
                        style={
                            'color': condition['color'], 
                            'marginLeft': '10px',
                            'fontWeight': 'bold'
                        }
                    )
                ], style={'margin': '10px 0'})
            )
        
        # Собираем полный интерфейс модуля
        children = [
            html.Label('Условия окраски (автоматически сгенерированы):'),
            message,
            html.Div(condition_components, id='condition-list'),
            html.Div([
                html.Button('Сохранить конфигурацию', id='save-config', n_clicks=0, style={'marginRight': '10px'}),
                dcc.Upload(id='load-config', children=html.Button('Загрузить конфигурацию', n_clicks=0)),
            ], style={'marginTop': '20px'})
        ]
        
        return children, {'display': 'block'}, conditions
    
    except Exception as e:
        print(f"Error generating conditions: {str(e)}")
        return "", {'display': 'none'}, []

@app.callback(
    Output('color-condition-module', 'children'),
    Output('color-condition-module', 'style'),
    Output('color-conditions', 'data'),
    Input('color-column', 'value'),
    State('stored-df', 'data'),
    prevent_initial_call=True
)
def generate_conditions(color_col, df_json):
    if not color_col or not df_json:
        return "", {'display': 'none'}, []
    
    try:
        # Чтение данных из JSON
        df = pd.read_json(io.StringIO(df_json), orient='split')
        
        # Получение уникальных значений
        unique_vals = df[color_col].astype(str).unique()
        print(unique_vals)
        
        # Создание условий и компонентов интерфейса
        conditions = []
        condition_components = []
        
        for i, val in enumerate(unique_vals[:7]):  # Ограничиваем 7 условиями
            condition = {
                'value': val,
                'color': RAINBOW_COLORS[i % len(RAINBOW_COLORS)],
                'enabled': True  # По умолчанию включено
            }
            conditions.append(condition)
            
            condition_components.append(
                html.Div([
                    # Чекбокс для включения/выключения
                    dcc.Checklist(
                        id={'type': 'condition-enabled', 'index': i},
                        options=[{'label': '', 'value': 'enabled'}],
                        value=['enabled'] if condition['enabled'] else [],
                        style={'display': 'inline-block', 'marginRight': '10px'}
                    ),
                    
                    # Поле значения
                    dcc.Input(
                        value=val,
                        id={'type': 'condition-value', 'index': i},
                        style={
                            'marginRight': '10px', 
                            'width': '150px',
                            'border': f'2px solid {condition["color"]}'
                        },
                        readOnly=True
                    ),
                    
                    # Выбор цвета
                    dcc.Dropdown(
                        id={'type': 'condition-color', 'index': i},
                        options=[{'label': c, 'value': c} for c in RAINBOW_COLORS],
                        value=condition['color'],
                        clearable=False,
                        style={
                            'width': '120px',
                            'display': 'inline-block',
                            'marginRight': '10px'
                        }
                    ),
                    
                    # Кнопка удаления
                    html.Button(
                        '✕', 
                        id={'type': 'remove-cond', 'index': i},
                        style={'color': 'red', 'marginLeft': '5px'}
                    )
                ], style={'margin': '10px 0', 'display': 'flex', 'alignItems': 'center'})
            )
        
        # Собираем полный интерфейс модуля
        children = [
            html.Label('Условия окраски:'),
            html.Div([
                html.Span("Вкл/Выкл", style={'width': '30px', 'display': 'inline-block'}),
                html.Span("Значение", style={'width': '150px', 'display': 'inline-block', 'marginLeft': '10px'}),
                html.Span("Цвет", style={'width': '120px', 'display': 'inline-block', 'marginLeft': '10px'})
            ], style={'fontWeight': 'bold', 'margin': '5px 0'}),
            
            html.Div(condition_components, id='condition-list'),
            
            html.Div([
                html.Button('Сохранить конфигурацию', id='save-config', n_clicks=0, style={'marginRight': '10px'}),
                dcc.Upload(id='load-config', children=html.Button('Загрузить конфигурацию', n_clicks=0)),
            ], style={'marginTop': '20px'})
        ]
        
        return children, {'display': 'block'}, conditions
    
    except Exception as e:
        print(f"Error generating conditions: {str(e)}")
        return "", {'display': 'none'}, []

# Удаление условия
@app.callback(
    Output('color-conditions', 'data', allow_duplicate=True),
    Input({'type': 'remove-cond', 'index': ALL}, 'n_clicks'),
    State('color-conditions', 'data'),
    prevent_initial_call=True
)
def remove_condition(n_clicks_list, conditions):
    if not conditions:
        return conditions
    
    ctx_triggered = ctx.triggered[0]
    if not ctx_triggered or 'index' not in ctx_triggered['prop_id']:
        return conditions
    
    try:
        # Получаем индекс удаляемого условия
        button_id = json.loads(ctx_triggered['prop_id'].split('.')[0])
        idx = button_id['index']
        
        # Создаем новый список без удаляемого элемента
        new_conditions = [val for i, val in enumerate(conditions) if i != idx]
        return new_conditions
    
    except Exception as e:
        print(f"Error in remove_condition: {str(e)}")
        return conditions

# Обновление условий
@app.callback(
    Output('color-conditions', 'data', allow_duplicate=True),
    Input({'type': 'condition-enabled', 'index': ALL}, 'value'),
    Input({'type': 'condition-color', 'index': ALL}, 'value'),
    Input({'type': 'remove-cond', 'index': ALL}, 'n_clicks'),
    State('color-conditions', 'data'),
    prevent_initial_call=True
)
def update_conditions(enabled_values, color_values, remove_clicks, conditions):
    ctx_triggered = ctx.triggered[0] if ctx.triggered else None
    
    if not conditions or not ctx_triggered:
        return conditions
    
    # Обработка удаления условий
    if 'remove-cond' in ctx_triggered['prop_id']:
        try:
            button_id = json.loads(ctx_triggered['prop_id'].split('.')[0])
            idx = button_id['index']
            if idx < len(conditions):
                conditions.pop(idx)
                return conditions
        except:
            return conditions
    
    # Обновление состояния включения
    for i, enabled in enumerate(enabled_values):
        if i < len(conditions):
            conditions[i]['enabled'] = bool(enabled)
    
    # Обновление цветов
    for i, color in enumerate(color_values):
        if i < len(conditions):
            conditions[i]['color'] = color
    
    return conditions

# Построение графика
# @app.callback(
#     Output('graph', 'figure'),
#     Output('error-message', 'children', allow_duplicate=True),
#     Input('plot-button', 'n_clicks'),
#     State('stored-df', 'data'),
#     State('xaxis-column', 'value'),
#     State('yaxis-column', 'value'),
#     State('color-column', 'value'),
#     State('color-conditions', 'data'),
#     prevent_initial_call=True
# )
# def update_graph(n_clicks, df_json, x_col, y_col, color_col, conditions):
    if not n_clicks or not df_json:
        return go.Figure(), ""
    
    try:
        df = pd.read_json(df_json, orient='split')
        
        # Проверка выбранных колонок
        if not x_col or not y_col:
            return go.Figure(), "Выберите колонки для осей X и Y"
        
        # Обработка цвета точек
        if color_col and conditions:
            colors = []
            for val in df[color_col]:
                color = 'gray'  # цвет по умолчанию
                for cond in conditions:
                    if str(val) == str(cond['value']):  # сравниваем как строки
                        color = cond['color']
                        break
                colors.append(color)
        else:
            colors = 'blue'
        
        # Создание графика
        fig = go.Figure(data=go.Scatter(
            x=df[x_col],
            y=df[y_col],
            mode='markers',
            marker=dict(color=colors, size=10),
            hovertext=df[color_col] if color_col else None
        ))
        
        fig.update_layout(
            title=f'{y_col} vs {x_col}',
            xaxis_title=x_col,
            yaxis_title=y_col,
            margin=dict(l=40, r=40, t=40, b=40)
        )
        
        return fig, ""
    
    except Exception as e:
        error_msg = f"Ошибка построения графика: {str(e)}"
        print(error_msg)
        return go.Figure(), error_msg

# Обновленный колбэк построения графика
@app.callback(
    Output('graph', 'figure'),
    Output('error-message', 'children', allow_duplicate=True),
    Input('plot-button', 'n_clicks'),
    State('stored-df', 'data'),
    State('xaxis-column', 'value'),
    State('yaxis-column', 'value'),
    State('color-column', 'value'),
    State('color-conditions', 'data'),
    prevent_initial_call=True
)
def update_graph(n_clicks, df_json, x_col, y_col, color_col, conditions):
    if not n_clicks or not df_json:
        return go.Figure(), ""
    
    try:
        df = pd.read_json(io.StringIO(df_json), orient='split')
        
        # Проверка выбранных колонок
        if not x_col or not y_col:
            return go.Figure(), "Выберите колонки для осей X и Y"
        
        # Фильтрация данных
        if color_col and conditions:
            print(color_col)
            print(conditions)
            # Получаем активные условия
            active_conditions = [cond for cond in conditions if cond['enabled']]
            print(active_conditions)
            
            # Если есть активные условия - фильтруем данные
            if active_conditions:
                active_values = [cond['value'] for cond in active_conditions]
                color_map = {cond['value']: cond['color'] for cond in active_conditions}
                
                # Фильтруем DataFrame, оставляя только строки с активными значениями
                filtered_df = df[df[color_col].astype(str).isin(active_values)]
                
                # Создаем список цветов для отфильтрованных точек
                colors = [color_map[str(val)] for val in filtered_df[color_col]]
                
                # Создание графика только с отфильтрованными точками
                fig = go.Figure(data=go.Scatter(
                    x=filtered_df[x_col],
                    y=filtered_df[y_col],
                    mode='markers',
                    marker=dict(color=colors, size=10),
                    hovertext=filtered_df[color_col] if color_col else None
                ))
            else:
                # Если нет активных условий - пустой график
                fig = go.Figure()
                fig.update_layout(
                    annotations=[dict(
                        text="Нет активных условий для отображения",
                        xref="paper", yref="paper",
                        x=0.5, y=0.5, showarrow=False
                    )]
                )
        else:
            # Если не выбрана колонка цвета или нет условий - отображаем все точки синим
            fig = go.Figure(data=go.Scatter(
                x=df[x_col],
                y=df[y_col],
                mode='markers',
                marker=dict(color='blue', size=10),
                hovertext=df[color_col] if color_col else None
            ))
        
            fig.update_layout(
                title=f'{y_col} vs {x_col}',
                xaxis_title=x_col,
                yaxis_title=y_col,
                margin=dict(l=40, r=40, t=40, b=40)
        )
        
        return fig, ""
    
    except Exception as e:
        error_msg = f"Ошибка построения графика: {str(e)}"
        print(error_msg)
        return go.Figure(), error_msg

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)