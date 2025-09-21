import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

# Настройка страницы
st.set_page_config(
    page_title="Анализ очков сотрудников",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Заголовок
st.title("📊 Анализ очков сотрудников")
st.markdown("---")

@st.cache_data
def load_data():
    """Загружает и подготавливает все необходимые данные"""
    
    # Загружаем данные employee_points_daily
    employee_points_daily_january = pd.read_csv('output/employee_points_daily_2025_01.csv')
    employee_points_daily_february = pd.read_csv('output/employee_points_daily_2025_02.csv')
    employee_points_daily_march = pd.read_csv('output/employee_points_daily_2025_03.csv')
    employee_points_daily_april = pd.read_csv('output/employee_points_daily_2025_04.csv')
    employee_points_daily_may = pd.read_csv('output/employee_points_daily_2025_05.csv')
    employee_points_daily_june = pd.read_csv('output/employee_points_daily_2025_06.csv')
    employee_points_daily_july = pd.read_csv('output/employee_points_daily_2025_07.csv')
    employee_points_daily_august = pd.read_csv('output/employee_points_daily_2025_08.csv')

    # Объединяем данные employee_points_daily
    employee_points_daily_full = pd.concat([
        employee_points_daily_january, employee_points_daily_february, employee_points_daily_march, 
        employee_points_daily_april, employee_points_daily_may, employee_points_daily_june, 
        employee_points_daily_july, employee_points_daily_august
    ])

    # Загружаем данные skills_mark
    skills_mark_january = pd.read_csv('output/rating_linear_col9_2025_01.csv')
    skills_mark_february = pd.read_csv('output/rating_linear_col9_2025_02.csv')
    skills_mark_march = pd.read_csv('output/rating_linear_col9_2025_03.csv')
    skills_mark_april = pd.read_csv('output/rating_linear_col9_2025_04.csv')
    skills_mark_may = pd.read_csv('output/rating_linear_col9_2025_05.csv')
    skills_mark_june = pd.read_csv('output/rating_linear_col9_2025_06.csv')
    skills_mark_july = pd.read_csv('output/rating_linear_col9_2025_07.csv')
    skills_mark_august = pd.read_csv('output/rating_linear_col9_2025_08.csv')

    # Объединяем данные skills_mark
    skills_mark_full = pd.concat([
        skills_mark_january, skills_mark_february, skills_mark_march, skills_mark_april,
        skills_mark_may, skills_mark_june, skills_mark_july, skills_mark_august
    ])

    # Загружаем детальные данные по заданиям
    tasks_full_january = pd.read_csv('output/employee_daily_tasks_points_full_2025_01.csv')
    tasks_full_february = pd.read_csv('output/employee_daily_tasks_points_full_2025_02.csv')
    tasks_full_march = pd.read_csv('output/employee_daily_tasks_points_full_2025_03.csv')
    tasks_full_april = pd.read_csv('output/employee_daily_tasks_points_full_2025_04.csv')
    tasks_full_may = pd.read_csv('output/employee_daily_tasks_points_full_2025_05.csv')
    tasks_full_june = pd.read_csv('output/employee_daily_tasks_points_full_2025_06.csv')
    tasks_full_july = pd.read_csv('output/employee_daily_tasks_points_full_2025_07.csv')
    tasks_full_august = pd.read_csv('output/employee_daily_tasks_points_full_2025_08.csv')

    # Объединяем детальные данные
    tasks_full = pd.concat([
        tasks_full_january, tasks_full_february, tasks_full_march, tasks_full_april,
        tasks_full_may, tasks_full_june, tasks_full_july, tasks_full_august
    ])

    # Создаем маппинг ID сотрудника на имя
    employee_name_mapping = skills_mark_full[['id_employee', 'fio_employee']].drop_duplicates()

    # Добавляем имена сотрудников в employee_points_daily_full
    employee_points_daily_full = employee_points_daily_full.merge(
        employee_name_mapping, 
        on='id_employee', 
        how='left'
    )

    # Добавляем имена сотрудников в tasks_full
    tasks_full = tasks_full.merge(
        employee_name_mapping, 
        on='id_employee', 
        how='left'
    )

    # Преобразуем дату в правильный формат
    employee_points_daily_full['date'] = pd.to_datetime(employee_points_daily_full['date'])
    employee_points_daily_full = employee_points_daily_full.sort_values('date')

    tasks_full['date'] = pd.to_datetime(tasks_full['date'])
    tasks_full = tasks_full.sort_values('date')

    # Создаем колонку с датой для skills_mark (первое число месяца)
    skills_mark_full['date'] = pd.to_datetime(skills_mark_full[['year', 'month']].assign(day=1))
    skills_mark_full = skills_mark_full.sort_values('date')

    # Загружаем данные о больничных и отпусках
    calendar_sick_holidays = pd.read_csv('output/calendar_sick_holidays.csv')
    
    # Создаем колонку с датой для calendar_sick_holidays (первое число месяца)
    calendar_sick_holidays['date'] = pd.to_datetime(calendar_sick_holidays[['year', 'month']].assign(day=1))
    calendar_sick_holidays = calendar_sick_holidays.sort_values('date')

    return employee_points_daily_full, skills_mark_full, employee_name_mapping, tasks_full, calendar_sick_holidays

# Загружаем данные
employee_points_daily_full, skills_mark_full, employee_name_mapping, tasks_full, calendar_sick_holidays = load_data()

# Создаем списки для фильтров
employee_data = employee_points_daily_full[['id_employee', 'fio_employee']].drop_duplicates()
# Убираем строки с NaN в fio_employee
employee_data = employee_data.dropna(subset=['fio_employee'])
employee_list = sorted(employee_data.values.tolist())
employee_options = [f"{emp[0]} - {emp[1]}" for emp in employee_list]

# Получаем уникальные месяцы
available_months = sorted(employee_points_daily_full['date'].dt.to_period('M').unique())
month_options = [str(month) for month in available_months]

# Боковая панель с фильтрами
st.sidebar.header("🔧 Фильтры")

# Выбор визуализации
visualization = st.sidebar.selectbox(
    "Выберите визуализацию:",
    [
        "Ежедневные очки (фильтр по сотруднику)",
        "Ежедневные очки по месяцу (фильтр по сотруднику и месяцу)",
        "Месячные средние очки (фильтр по месяцу и сотруднику)", 
        "Skills Mark (фильтр по сотруднику)"
    ]
)

st.markdown(f"## {visualization}")

if visualization == "Ежедневные очки (фильтр по сотруднику)":
    # Фильтр по сотруднику
    selected_employee = st.sidebar.selectbox(
        "Выберите сотрудника:",
        employee_options,
        index=0
    )
    
    # Извлекаем ID сотрудника
    selected_employee_id = int(selected_employee.split(' - ')[0])
    selected_employee_name = selected_employee.split(' - ')[1] if ' - ' in selected_employee else "Неизвестно"
    
    # Фильтруем данные
    filtered_data = employee_points_daily_full[employee_points_daily_full['id_employee'] == selected_employee_id]
    
    # Создаем график
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=filtered_data['date'],
        y=filtered_data['points'],
        mode='lines+markers',
        name=f"ID: {selected_employee_id}",
        line=dict(width=3, color='#1f77b4'),
        marker=dict(size=6),
        hovertemplate=f'<b>ID: {selected_employee_id}</b><br>' +
                     f'<b>Имя: {selected_employee_name}</b><br>' +
                     'Дата: %{x}<br>' +
                     'Очки: %{y}<br>' +
                     '<extra></extra>'
    ))
    
    fig.update_layout(
        title=f'Ежедневная динамика очков: {selected_employee}',
        xaxis_title='Дата',
        yaxis_title='Количество очков',
        width=1200,
        height=600,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Получаем данные о больничных и отпусках за весь период
    sick_holiday_data = calendar_sick_holidays[
        calendar_sick_holidays['id_employee'] == selected_employee_id
    ]
    
    # Извлекаем общее количество больничных и отпуска дней
    total_sick_days = sick_holiday_data['sick_count'].sum() if len(sick_holiday_data) > 0 else 0
    total_holiday_days = sick_holiday_data['holidays_count'].sum() if len(sick_holiday_data) > 0 else 0
    
    # Статистика
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        st.metric("Общее количество очков", f"{filtered_data['points'].sum():.0f}")
    with col2:
        st.metric("Средние очки", f"{filtered_data['points'].mean():.2f}")
    with col3:
        st.metric("Максимальные очки", f"{filtered_data['points'].max():.0f}")
    with col4:
        st.metric("Количество дней", f"{len(filtered_data)}")
    with col5:
        st.metric("Больничные дни (всего)", f"{total_sick_days:.0f}")
    with col6:
        st.metric("Отпускные дни (всего)", f"{total_holiday_days:.0f}")

elif visualization == "Ежедневные очки по месяцу (фильтр по сотруднику и месяцу)":
    # Фильтры
    selected_month = st.sidebar.selectbox(
        "Выберите месяц:",
        month_options,
        index=0
    )
    
    selected_employee = st.sidebar.selectbox(
        "Выберите сотрудника:",
        employee_options,
        index=0
    )
    
    # Извлекаем ID сотрудника
    selected_employee_id = int(selected_employee.split(' - ')[0])
    selected_employee_name = selected_employee.split(' - ')[1] if ' - ' in selected_employee else "Неизвестно"
    
    # Преобразуем выбранный месяц в период
    selected_month_period = pd.to_datetime(selected_month)
    
    # Фильтруем данные по месяцу и сотруднику
    filtered_data = employee_points_daily_full[
        (employee_points_daily_full['id_employee'] == selected_employee_id) &
        (employee_points_daily_full['date'].dt.to_period('M') == selected_month_period.to_period('M'))
    ]
    
    # Создаем график
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=filtered_data['date'],
        y=filtered_data['points'],
        mode='lines+markers',
        name=f"ID: {selected_employee_id}",
        line=dict(width=3, color='#d62728'),
        marker=dict(size=6),
        hovertemplate=f'<b>ID: {selected_employee_id}</b><br>' +
                     f'<b>Имя: {selected_employee_name}</b><br>' +
                     'Дата: %{x}<br>' +
                     'Очки: %{y}<br>' +
                     '<extra></extra>'
    ))
    
    fig.update_layout(
        title=f'Ежедневные очки за {selected_month}: {selected_employee}',
        xaxis_title='Дата',
        yaxis_title='Количество очков',
        width=1200,
        height=600,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Получаем данные о больничных и отпусках за выбранный месяц
    selected_month_period_obj = selected_month_period.to_period('M')
    sick_holiday_data = calendar_sick_holidays[
        (calendar_sick_holidays['id_employee'] == selected_employee_id) &
        (calendar_sick_holidays['date'].dt.to_period('M') == selected_month_period_obj)
    ]
    
    # Извлекаем количество больничных и отпуска дней
    sick_days = sick_holiday_data['sick_count'].sum() if len(sick_holiday_data) > 0 else 0
    holiday_days = sick_holiday_data['holidays_count'].sum() if len(sick_holiday_data) > 0 else 0
    
    # Статистика
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        st.metric("Общее количество очков", f"{filtered_data['points'].sum():.0f}")
    with col2:
        st.metric("Средние очки", f"{filtered_data['points'].mean():.2f}")
    with col3:
        st.metric("Максимальные очки", f"{filtered_data['points'].max():.0f}")
    with col4:
        st.metric("Количество дней", f"{len(filtered_data)}")
    with col5:
        st.metric("Больничные дни", f"{sick_days:.0f}")
    with col6:
        st.metric("Отпускные дни", f"{holiday_days:.0f}")
    
    # Детализация по изделиям за весь месяц
    st.markdown("### 🔍 Детализация по изделиям за весь месяц")
    
    if len(filtered_data) > 0:
        # Получаем детальные данные за весь выбранный месяц
        detailed_data = tasks_full[
            (tasks_full['id_employee'] == selected_employee_id) &
            (tasks_full['date'].dt.to_period('M') == selected_month_period.to_period('M'))
        ]
        
        if len(detailed_data) > 0:
            # Создаем копию данных и форматируем дату
            detailed_data_display = detailed_data.copy()
            detailed_data_display['date_formatted'] = detailed_data_display['date'].dt.date
            
            # Сортируем по дате и очкам
            detailed_data_sorted = detailed_data_display.sort_values(['date', 'points'], ascending=[True, False])
            
            st.markdown(f"**Детализация за {selected_month}:**")
            
            # Показываем таблицу со всеми записями
            st.dataframe(
                detailed_data_sorted[['date_formatted', 'sap_id', 'sap_name', 'points', 'units_made', 'norma_product_adjusted_with_discounts']].head(50),
                use_container_width=True,
                column_config={
                    "date_formatted": "Дата",
                    "sap_id": "SAP ID",
                    "sap_name": "Название изделия",
                    "points": "Очки",
                    "units_made": "Количество",
                    "norma_product_adjusted_with_discounts": "Норма с учетом скидок"
                }
            )
            
            # График по изделиям (агрегируем только для графика)
            grouped_for_chart = detailed_data.groupby(['sap_id', 'sap_name']).agg({
                'points': 'sum'
            }).reset_index().sort_values('points', ascending=False)
            
            if len(grouped_for_chart) > 0:
                fig_products = px.bar(
                    grouped_for_chart.head(10),
                    x='sap_name',
                    y='points',
                    title=f'Топ-10 изделий по общим очкам за {selected_month}',
                    labels={'sap_name': 'Название изделия', 'points': 'Очки'}
                )
                fig_products.update_xaxes(tickangle=45)
                st.plotly_chart(fig_products, use_container_width=True)
        else:
            st.warning(f"Нет детальных данных за {selected_month}")
    else:
        st.warning("Нет данных за выбранный период")

elif visualization == "Месячные средние очки (фильтр по месяцу и сотруднику)":
    # Фильтры
    selected_month = st.sidebar.selectbox(
        "Выберите месяц:",
        month_options,
        index=0
    )
    
    selected_employee = st.sidebar.selectbox(
        "Выберите сотрудника:",
        employee_options,
        index=0
    )
    
    # Извлекаем ID сотрудника
    selected_employee_id = int(selected_employee.split(' - ')[0])
    selected_employee_name = selected_employee.split(' - ')[1] if ' - ' in selected_employee else "Неизвестно"
    
    # Создаем агрегированные данные по месяцам
    monthly_avg = employee_points_daily_full.groupby([
        employee_points_daily_full['date'].dt.to_period('M'), 
        'id_employee'
    ])['points'].mean().reset_index()
    
    # Преобразуем период в дату
    monthly_avg['date'] = monthly_avg['date'].astype(str)
    monthly_avg['date'] = pd.to_datetime(monthly_avg['date'])
    
    # Добавляем имена сотрудников
    monthly_avg = monthly_avg.merge(employee_name_mapping, on='id_employee', how='left')
    
    # Фильтруем данные
    filtered_data = monthly_avg[monthly_avg['id_employee'] == selected_employee_id]
    
    # Создаем график
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=filtered_data['date'],
        y=filtered_data['points'],
        mode='lines+markers',
        name=f"ID: {selected_employee_id}",
        line=dict(width=4, color='#ff7f0e'),
        marker=dict(size=10),
        hovertemplate=f'<b>ID: {selected_employee_id}</b><br>' +
                     f'<b>Имя: {selected_employee_name}</b><br>' +
                     'Месяц: %{x}<br>' +
                     'Средние очки: %{y:.2f}<br>' +
                     '<extra></extra>'
    ))
    
    fig.update_layout(
        title=f'Средние очки по месяцам: {selected_employee}',
        xaxis_title='Месяц',
        yaxis_title='Средние очки за месяц',
        width=1200,
        height=600,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Получаем данные о больничных и отпусках за весь период
    sick_holiday_data = calendar_sick_holidays[
        calendar_sick_holidays['id_employee'] == selected_employee_id
    ]
    
    # Извлекаем общее количество больничных и отпуска дней
    total_sick_days = sick_holiday_data['sick_count'].sum() if len(sick_holiday_data) > 0 else 0
    total_holiday_days = sick_holiday_data['holidays_count'].sum() if len(sick_holiday_data) > 0 else 0
    
    # Статистика
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        st.metric("Средние очки за все месяцы", f"{filtered_data['points'].mean():.2f}")
    with col2:
        st.metric("Максимальные средние очки", f"{filtered_data['points'].max():.2f}")
    with col3:
        st.metric("Минимальные средние очки", f"{filtered_data['points'].min():.2f}")
    with col4:
        st.metric("Количество месяцев", f"{len(filtered_data)}")
    with col5:
        st.metric("Больничные дни (всего)", f"{total_sick_days:.0f}")
    with col6:
        st.metric("Отпускные дни (всего)", f"{total_holiday_days:.0f}")

elif visualization == "Skills Mark (фильтр по сотруднику)":
    # Фильтр по сотруднику
    selected_employee = st.sidebar.selectbox(
        "Выберите сотрудника:",
        employee_options,
        index=0
    )
    
    # Извлекаем ID сотрудника
    selected_employee_id = int(selected_employee.split(' - ')[0])
    selected_employee_name = selected_employee.split(' - ')[1] if ' - ' in selected_employee else "Неизвестно"
    
    # Фильтруем данные
    filtered_data = skills_mark_full[skills_mark_full['id_employee'] == selected_employee_id]
    
    # Создаем график
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=filtered_data['date'],
        y=filtered_data['skills_mark'],
        mode='lines+markers',
        name=f"ID: {selected_employee_id}",
        line=dict(width=4, color='#2ca02c'),
        marker=dict(size=10),
        hovertemplate=f'<b>ID: {selected_employee_id}</b><br>' +
                     f'<b>Имя: {selected_employee_name}</b><br>' +
                     'Месяц: %{x}<br>' +
                     'Skills Mark: %{y}<br>' +
                     '<extra></extra>'
    ))
    
    fig.update_layout(
        title=f'Динамика Skills Mark: {selected_employee}',
        xaxis_title='Месяц',
        yaxis_title='Skills Mark',
        width=1200,
        height=600,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Получаем данные о больничных и отпусках за весь период
    sick_holiday_data = calendar_sick_holidays[
        calendar_sick_holidays['id_employee'] == selected_employee_id
    ]
    
    # Извлекаем общее количество больничных и отпуска дней
    total_sick_days = sick_holiday_data['sick_count'].sum() if len(sick_holiday_data) > 0 else 0
    total_holiday_days = sick_holiday_data['holidays_count'].sum() if len(sick_holiday_data) > 0 else 0
    
    # Статистика
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        st.metric("Средний Skills Mark", f"{filtered_data['skills_mark'].mean():.2f}")
    with col2:
        st.metric("Максимальный Skills Mark", f"{filtered_data['skills_mark'].max():.0f}")
    with col3:
        st.metric("Минимальный Skills Mark", f"{filtered_data['skills_mark'].min():.0f}")
    with col4:
        st.metric("Количество месяцев", f"{len(filtered_data)}")
    with col5:
        st.metric("Больничные дни (всего)", f"{total_sick_days:.0f}")
    with col6:
        st.metric("Отпускные дни (всего)", f"{total_holiday_days:.0f}")

# Информация в футере
st.markdown("---")
st.markdown("### 📈 Информация о данных")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Всего сотрудников", f"{len(employee_list)}")

with col2:
    st.metric("Период данных (очки)", f"{employee_points_daily_full['date'].min().strftime('%Y-%m-%d')} - {employee_points_daily_full['date'].max().strftime('%Y-%m-%d')}")

with col3:
    st.metric("Период данных (Skills Mark)", f"{skills_mark_full['date'].min().strftime('%Y-%m')} - {skills_mark_full['date'].max().strftime('%Y-%m')}")
