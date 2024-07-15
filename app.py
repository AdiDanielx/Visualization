import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

df = pd.read_csv('main_df_subset.csv')

st.set_page_config(
    page_title="Skills Analysis: Job Market Insights",
    page_icon = 'linkedinlogo.gif',
    layout="wide",
    initial_sidebar_state="expanded")

st.markdown(f"## LinkedIn Job Market Dashboard: Skills & Salaries")

df = pd.read_csv('main_df_subset.csv')

state_mapping = {
    'NJ': 'New Jersey', 'IL': 'Illinois', 'NY': 'New York', 'CA': 'California', 'PA': 'Pennsylvania', 
    'WI': 'Wisconsin', 'WA': 'Washington', 'NC': 'North Carolina', 'OH': 'Ohio', 'GA': 'Georgia', 
    'KY': 'Kentucky', 'FL': 'Florida', 'MD': 'Maryland', 'TX': 'Texas', 'VA': 'Virginia', 
    'MI': 'Michigan', 'SD': 'South Dakota', 'IN': 'Indiana', 'NE': 'Nebraska', 'MO': 'Missouri', 
    'MA': 'Massachusetts', 'TN': 'Tennessee', 'LA': 'Louisiana', 'DC': 'District of Columbia', 
    'AR': 'Arkansas', 'OK': 'Oklahoma', 'UT': 'Utah', 'MN': 'Minnesota', 'AZ': 'Arizona', 'CT': 'Connecticut', 
    'RI': 'Rhode Island', 'ME': 'Maine', 'NH': 'New Hampshire', 'CO': 'Colorado', 'AL': 'Alabama', 
    'KS': 'Kansas', 'ID': 'Idaho', 'HI': 'Hawaii', 'OR': 'Oregon', 'NV': 'Nevada', 'NM': 'New Mexico', 
    'VT': 'Vermont', 'IA': 'Iowa', 'SC': 'South Carolina', 'DE': 'Delaware', 'ND': 'North Dakota', 
    'MS': 'Mississippi', 'WY': 'Wyoming', 'MT': 'Montana', 'AK': 'Alaska'
}

# Reverse mapping for filtering purposes
reverse_state_mapping = {v: k for k, v in state_mapping.items()}

df_filtered_state = df.copy()
df_filtered_state['state'] = df_filtered_state['state'].replace(state_mapping)
df_filtered_state = df_filtered_state[df_filtered_state['state'].isin(state_mapping.values())]
df['state_full_name'] = df['state'].replace(state_mapping)
if 'selected_state' not in st.session_state:
    st.session_state.selected_state = 'CA' 
     
# Company size mapping
company_size_mapping = {
    1.0: '2-50 employees',
    2.0: '51-200 employees',
    3.0: '201-500 employees',
    4.0: '501-1000 employees',
    5.0: '1001-5000 employees',
    6.0: '5001-10,000 employees',
    7.0: '10,001+ employees'
    }
df['company_size_label'] = df['company_size'].map(company_size_mapping)
df['company_size_label'] = pd.Categorical(df['company_size_label'], categories=[
    '2-50 employees', '51-200 employees', '201-500 employees', '501-1000 employees',
    '1001-5000 employees', '5001-10,000 employees', '10,001+ employees'], ordered=True)

########################Side Bar#################################

with st.sidebar:
    st.sidebar.title("Search Filters")
    unique_skill_names = df['skill_name'].dropna().unique()
    selected_skill_name = st.sidebar.selectbox('Select Skill:', unique_skill_names, key='skill_select')
    unique_states = list(state_mapping.keys())
    selected_state_abbreviation = st.sidebar.selectbox(
        "Select a State",
        unique_states,
        index=unique_states.index(st.session_state.selected_state),
        key='state_select'
    )
    st.session_state.selected_state = selected_state_abbreviation
    selected_state_full_name = state_mapping[selected_state_abbreviation]


filtered_df_skill_state = df[(df['skill_name'] == selected_skill_name) & (df['state'] == selected_state_abbreviation)]

if not filtered_df_skill_state.empty:
    min_salary = filtered_df_skill_state['min_salary'].min()
    max_salary = filtered_df_skill_state['max_salary'].max()
    avg_salary = (filtered_df_skill_state['min_salary'] + filtered_df_skill_state['max_salary']).mean() / 2

    st.sidebar.subheader('Salary Statistics')
    st.sidebar.write(f"Minimum Salary: ${min_salary:,.2f}")
    st.sidebar.write(f"Average Salary: ${avg_salary:,.2f}")
    st.sidebar.write(f"Maximum Salary: ${max_salary:,.2f}")

    num_job_postings = filtered_df_skill_state.shape[0]  # Counting rows which gives number of job postings
    st.sidebar.subheader('Number of Job Postings')
    st.sidebar.write(f"Total: {num_job_postings}")  
    top_5_companies = filtered_df_skill_state['company_name'].value_counts().head(5)
    
    st.sidebar.subheader('Top Companies in State for Skill')
    for company, count in top_5_companies.items():
        st.sidebar.write(f"{company}: {count} job postings")

#########################COL########################
row1_col1, row1_col2 = st.columns(2)

#########################COL 1########################

with row1_col1:
########################MAP PLOT#################################

    filtered_df = df[df['skill_name'] == selected_skill_name]

    state_job_counts = filtered_df.groupby('state')['job_id'].count().reset_index()
    state_job_counts.columns = ['state', 'job_count']

    min_job_count = state_job_counts['job_count'].min()
    max_job_count = state_job_counts['job_count'].max()
    num_bins = 3
    if max_job_count == min_job_count:
        max_job_count += 1
    color_ranges = pd.cut(state_job_counts['job_count'], bins=num_bins, retbins=True)[1]

    def format_label(value):
        if value >= 1000:
            return f'{int(round(value/1000))}K'
        else:
            return f'{int(value)}'
        
    labels = [f'{(format_label(color_ranges[i]))} - {(format_label(color_ranges[i+1]))}' for i in range(len(color_ranges) - 1)]
    state_job_counts['color_label'] = pd.cut(state_job_counts['job_count'],
                                            bins=color_ranges,
                                            labels=labels,
                                            include_lowest=True)
    colors = [ '#93C6E7', '#E8A0BF','#AEE2FF',
    ]
    color_map = {label: colors[i] for i, label in enumerate(labels)}

    state_job_counts['color'] = state_job_counts['color_label'].map(color_map)

    ticktext = labels
    tickvals = list(range(len(labels)))

    fig = px.choropleth(
        state_job_counts,
        locations='state',
        locationmode='USA-states',
        color='color_label', 
        scope='usa',
        color_discrete_map=color_map,  
        labels={'job_count': 'Job Count', 'color_label': 'Job Count Range'},  
        category_orders={"color_label": labels}  
    )
    fig.update_geos(projection_type="albers usa")
    fig.update_traces(
        hovertemplate='<b>%{location}</b><br>Job Count=%{customdata[0]}<extra></extra>',
        customdata=state_job_counts[['job_count', 'state']]
    )

    fig.update_layout(coloraxis_colorbar=dict(
        title="Open Jobs",
        tickvals=tickvals,
        ticktext=ticktext,
        lenmode="pixels", len=300, yanchor="top", y=1,
        ticks="outside"
    ))
    st.markdown(f'##### Skill Distribution in Job Postings for {selected_skill_name} across the USA')

    st.plotly_chart(fig)

########################SNAKEY PLOT#######################
with row1_col2:
    state_filtered = df[df['state'] == selected_state_abbreviation]
    top_skills = state_filtered['skill_name'].value_counts()
    top_skills = top_skills[top_skills.index != 'other'].head(5).index.tolist()
    state_filtered = state_filtered[state_filtered['skill_name'].isin(top_skills)]
    all_labels = list(set(state_filtered['skill_name']).union(set(state_filtered['formatted_experience_level'])))
    label_to_index = {label: i for i, label in enumerate(all_labels)}
    source = []
    target = []
    value = []
    skills_to_exp = state_filtered.groupby(['skill_name', 'formatted_experience_level']).size().reset_index(name='count')
    for _, row in skills_to_exp.iterrows():
        source.append(label_to_index[row['skill_name']])
        target.append(label_to_index[row['formatted_experience_level']])
        value.append(row['count'])
    skill_colors = ['#93C6E7 ', '#8EA7E9 ', '#AEE2FF', '#E8A0BF', '#CAB8FF']
    skill_color_map = {skill: skill_colors[i] for i, skill in enumerate(top_skills)}
    node_colors = []
    for label in all_labels:
        if label in skill_color_map:
            node_colors.append(skill_color_map[label])
        else:
            node_colors.append("rgba(0, 0, 0, 0.1)")  # Light grey for other nodes
    link_colors = []
    for _, row in skills_to_exp.iterrows():
        link_colors.append(skill_color_map[row['skill_name']])
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=all_labels,
            color=node_colors
        ),
        link=dict(
            source=source,
            target=target,
            value=value,
            color=link_colors
        )
    )])
    st.markdown(f"##### Skill Distribution in Job Postings for {selected_skill_name} in {selected_state_full_name}")


    st.plotly_chart(fig)


#########################COL 2########################
row2_col1, row2_col2 = st.columns(2)
######################## BAR CHART #######################
with row2_col2:

    col1, col2 = st.columns([4, 1])
    filtered_df_skill = df[df['skill_name'] == selected_skill_name]

    filtered_df_state = filtered_df_skill[filtered_df_skill['state'] == selected_state_abbreviation]

    available_work_types = filtered_df_state['formatted_work_type'].unique()
    if 'selected_work_type' not in st.session_state:
        st.session_state.selected_work_type = available_work_types[0] if available_work_types.size > 0 else None

    with col2:
        selected_work_type = st.radio(
            "Select Work Type",
            available_work_types,
            index=0 if st.session_state.selected_work_type is None else available_work_types.tolist().index(st.session_state.selected_work_type)
        )

        st.session_state.selected_work_type = selected_work_type

    selected_work_type = st.session_state.selected_work_type

    with col1:
        filtered_df = filtered_df_state[filtered_df_state['formatted_work_type'].isin([selected_work_type])]
        company_experience_data = filtered_df.groupby(['company_name', 'formatted_experience_level']).size().reset_index(name='job_count')

        top_5_companies = company_experience_data.groupby('company_name')['job_count'].sum().nlargest(5).index
        top_5_data = company_experience_data[company_experience_data['company_name'].isin(top_5_companies)]

        top_5_data = top_5_data.sort_values('job_count', ascending=False)
        color_map = {
            "Internship": "#93C6E7 ",
            "Entry level": "#8EA7E9 ",
            "Associate": "#AEE2FF ",
            "Mid-Senior level": "#E8A0BF  ",
            "Director": "#CAB8FF",
            "Executive": "#F0E4D7"
        }

        fig3 = px.bar(
            top_5_data,
            x='company_name',
            y='job_count',
            color='formatted_experience_level',
            labels={'job_count': 'Job Count', 'company_name': 'Company', 'formatted_experience_level': 'Experience Level'},
            barmode='stack',
            color_discrete_map=color_map,
            hover_data={'company_name': False}
        )

        fig3.update_layout(
            xaxis=dict(
                title='Company',
                tickangle=-45,
                automargin=True,
            ),
            yaxis=dict(
                title='Job Count',
                range=[0, top_5_data['job_count'].max() + 10]
            )
            
        )

        st.markdown(f"##### Top Companies for {selected_skill_name} in {selected_state_full_name}: Distribution by Experience Level of {selected_work_type}")
        st.plotly_chart(fig3, use_container_width=True)
        
    
########################BOX PLOT #######################
with row2_col1:

    def box_plot(df, selected_skill_name):
        filter_box = df[df['skill_name'] == selected_skill_name]
        filter_box['salary'] = df.apply(lambda row: [row['min_salary'], row['max_salary']], axis=1)
        df_expanded = filter_box.explode('salary')
        df_expanded['salary'] = pd.to_numeric(df_expanded['salary'], errors='coerce')
        df_expanded['applies'] = pd.to_numeric(df_expanded['applies'], errors='coerce')
        df_expanded = df_expanded.dropna(subset=['salary', 'applies'])
                
        applies_description = df_expanded['applies'].describe()
        
        def categorize_applies(x):
            if x == 0:
                return 'No\nApplications'
            elif x <= applies_description['50%']:
                return 'Below Average\nApplications'
            elif x <= applies_description['75%']:
                return 'Average\nApplications'
            else:
                return 'Above Average\nApplications'
        
        df_expanded['applies_category'] = df_expanded['applies'].apply(categorize_applies)
        df_expanded = df_expanded[df_expanded['skill_name'].str.contains(selected_skill_name, case=False, na=False)]
            
        fig = px.box(df_expanded, x='company_size_label', y='salary', color='applies_category',
                    labels={'company_size_label': 'Company Size', 'salary': 'Salary', 'applies_category': 'Applies Category'},
                    color_discrete_map={
                        'No\nApplications': '#93C6E7',  
                        'Below Average\nApplications': '#8EA7E9',   
                        'Average\nApplications': '#AEE2FF', 
                        'Above Average\nApplications': '#E8A0BF'   
                    },
                    category_orders={
                        'company_size_label': ['2-50 employees', '51-200 employees', '201-500 employees', '501-1000 employees', 
                                               '1001-5000 employees', '5001-10,000 employees', '10,001+ employees'],
                        'applies_category': ['No Applications', 'Below Average Applications', 'Average Applications', 'Above Average Applications']
                    },
                    points=False)  
        fig.update_layout(
            xaxis_title='Company Size',
            yaxis_title='Salary',
            xaxis_tickangle=-45,
            showlegend=True,
            height=600,
            width=800,
            yaxis_range=[0, df_expanded['salary'].max() + 20000]  
        )
        
        st.markdown(f"##### Salary Distribution by Company Size for {selected_skill_name}")

        st.plotly_chart(fig)

    if selected_skill_name:
        box_plot(df, selected_skill_name)

