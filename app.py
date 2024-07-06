import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns


# Page configuration

st.set_page_config(
    page_title="Top Skills in Job Posts",
    page_icon = "💼",
    layout="wide",
    initial_sidebar_state="expanded")


# Load your dataset
df = pd.read_csv('Datasets\main_df.csv')

#SideBar
with st.sidebar:
    st.sidebar.title("Skills")
    unique_skill_names = df['skill_name'].dropna().unique()
    selected_skill_name = st.sidebar.selectbox('Select Skill:', unique_skill_names)


def create_skill_map(df, selected_skill_name):
    filtered_data = df[df['skill_name'] == selected_skill_name]
    aggregated_data = filtered_data.groupby(['state', 'company_name']).agg({
        'job_id': 'count',
        'min_salary': 'min'
    }).reset_index()
    aggregated_data.columns = ['state', 'company_name', 'job_count', 'min_salary']
    top_companies_per_state = aggregated_data.sort_values(['state', 'job_count'], ascending=[True, False]).groupby('state').head(3)
    aggregated_data = aggregated_data.groupby('state').agg({
        'job_count': 'sum',
        'min_salary': 'min'
    }).reset_index()
    hover_data = []
    for state in aggregated_data['state']:
        top_companies = top_companies_per_state[top_companies_per_state['state'] == state]
        companies_str = "<br>".join([f"{row['company_name']}: {row['job_count']}" for _, row in top_companies.iterrows()])
        hover_data.append(companies_str)

    aggregated_data['top_companies'] = hover_data
    hover_template = (
        "<b>State:</b> %{hovertext}<br>"
        "<b>Number of Jobs:</b> %{customdata[0]}<br>"
        "<b>Minimum Salary:</b> $%{customdata[1]:,.2f}<br>"
        "<b>Top Companies Hiring:</b><br>%{customdata[2]}"
    )
    fig = px.choropleth(
        aggregated_data,
        locations='state',
        locationmode="USA-states", 
        color='job_count',  
        hover_name='state',
        hover_data={
            'job_count': True,
            'min_salary': True,
            'top_companies': True
        },
        scope="usa", 
        # title=f'Number of Jobs for "{selected_skill_name}" by State',
        labels={'job_count': 'Number of Jobs'},
        color_continuous_scale=px.colors.sequential.Blues  
    )
    fig.update_traces(
        hovertemplate=hover_template,
        customdata=aggregated_data[['job_count', 'min_salary', 'top_companies']].values,
        hovertext=aggregated_data['state']
    )

    return fig

def create_visualization(page, skill_data_page1, skill_data_page2, experience_skill_data):
    if page == "Page 1: Top Skills by Job Postings Count":
        # Format the job_count to include commas
        skill_data_page1['formatted_job_count'] = skill_data_page1['job_count'].apply(lambda x: f"{x:,}")

        # Bar plot for job count
        fig1 = px.bar(
            skill_data_page1,
            x='skill_name',
            y='job_count',
            text='formatted_job_count',
            title='Top Skills by Job Postings Count',
            labels={'job_count': 'Number of Job Postings', 'skill_name': 'Skill'}
        )

        # Update the text position and template to include commas
        fig1.update_traces(textposition='outside', texttemplate='%{text}')

        # Add scrollbar functionality to the x-axis
        fig1.update_layout(
            xaxis=dict(
                title='Skill',
                tickangle=-45,
                automargin=True,
                rangeslider=dict(
                    visible=True
                ),
                range=[0, 8]  # Initially show only a part of the data
            ),
            yaxis=dict(
                title='Number of Job Postings',
                range=[0, 55000]  
            ),
            height=700,  # Adjust height to make the plot bigger
            margin=dict(l=20, r=20, t=30, b=20)  # Adjust margins to use space better
        )

        return fig1

    elif page == "Page 2: Average Salary by Skill":
        # Line plot for average salary
        fig2 = go.Figure()

        fig2.add_trace(
            go.Scatter(
                x=skill_data_page1['skill_name'],
                y=skill_data_page1['average_salary'],
                name='Average Max Salary ($)',
                mode='lines+markers',
                hoverinfo='y',
                hovertemplate='<b>%{y:$,.2f}</b><extra></extra>',
                line=dict(color='#9d65f5')  # Specify color for the max salary line
            )
        )

        fig2.add_trace(
            go.Scatter(
                x=skill_data_page1['skill_name'],
                y=skill_data_page1['average_min_salary'],
                name='Average Min Salary ($)',
                mode='lines+markers',
                hoverinfo='y',
                hovertemplate='<b>%{y:$,.2f}</b><extra></extra>',
                line=dict(color='#658df5')  # Specify color for the min salary line
            )
        )

        fig2.update_layout(
            title='Average Salary by Skill',
            xaxis=dict(
                title='Skill',
                tickangle=-45,
                automargin=True,
                rangeslider=dict(
                    visible=True
                ),
                range=[0, 8]  # Initially show only a part of the data
            ),
            yaxis=dict(
                title='Average Salary ($)',
                tickformat='$,.0f'
            ),
            legend=dict(
                title='Legend',
                itemsizing='constant'
            ),
            height=700,  # Adjust height to make the plot bigger
            margin=dict(l=20, r=20, t=30, b=20)  # Adjust margins to use space better
        )

        return fig2

    elif page == "Page 3: Skills and Experience Levels":
        # Define a consistent color map for experience levels
        color_map = {
            "Internship": "#77dd77",   # Pastel green
            "Entry level": "#ff6961",  # Pastel red
            "Associate": "#779ecb",    # Pastel blue
            "Mid-Senior level": "#cfcfc4",  # Pastel gray
            "Director": "#ffb347",     # Pastel orange
            "Executive": "#ffb3ba",    # Pastel pink
            "Not Specified": "#b19cd9" # Pastel purple
        }

        # Create stacked bar chart
        fig3 = px.bar(
            experience_skill_data,
            x='skill_name',
            y='job_count',
            color='formatted_experience_level',
            title='Stacked Bar Chart of Skills and Experience Levels',
            labels={'job_count': 'Job Count', 'skill_name': 'Skill', 'formatted_experience_level': 'Experience Level'},
            barmode='stack',
            color_discrete_map=color_map  # Apply color map
        )

        # Add scrollbar functionality to the x-axis
        fig3.update_layout(
            xaxis=dict(
                title='Skill',
                tickangle=-45,
                automargin=True,
                rangeslider=dict(
                    visible=True
                ),
                range=[0, 8]  # Initially show only a part of the data
            ),
            yaxis=dict(
                title='Job Count',
                range=[0, 55000] 
            ),
            height=700,  # Adjust height to make the plot bigger
            margin=dict(l=20, r=20, t=30, b=20)  # Adjust margins to use space better
        )

        return fig3
    
def filter_and_plot(df, selected_skill_name):
    # Filter necessary columns and remove rows with "Not Specified" company size
    df_filtered = df[['views', 'applies', 'company_size', 'skill_name']]
    df_filtered = df_filtered[df_filtered['company_size'] != 'Not Specified']
    
    # Convert 'company_size' to an ordered category
    size_order = ['1.0', '2.0', '3.0', '4.0', '5.0', '6.0']
    df_filtered['company_size'] = pd.Categorical(df_filtered['company_size'], categories=size_order, ordered=True)
    
    # Filter the dataframe based on the selected skill
    df_filtered = df_filtered[df_filtered['skill_name'].str.contains(selected_skill_name, case=False, na=False)]
    
    # Custom color palette
    custom_palette = {
        '1.0': '#F5E800',
        '2.0': '#F59B00',
        '3.0': '#00F570',
        '4.0': '#00C6F5',
        '5.0': '#C600F5',
        '6.0': '#E67185'
    }
    
    # Plot the data
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df_filtered, x='views', y='applies', hue='company_size', palette=custom_palette, alpha=0.7)
    plt.title('Views vs Applications by Company Size')
    plt.xlabel('Number of Views')
    plt.ylabel('Number of Applications')
    plt.legend(title='Company Size')
    
    # Set axis limits
    plt.xlim(0, 100)
    plt.ylim(0, 25)
    
    # Show the plot in Streamlit
    st.pyplot(plt)
col = st.columns((4,5), gap='medium')

# with col[0]:
#     st.markdown('#### Gains/Losses')

with col[0]:
    st.markdown('#### Demand for Skills Across USA State')
    fig = create_skill_map(df, selected_skill_name)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('#### Job Posting Analysis: Views, Applications, and Company Size')
    filter_and_plot(df, selected_skill_name)




with col[1]:
    st.markdown('#### Insights into Job Postings and Skills Demand')

        # Aggregate data by skill_name for page 1
    skill_data_page1 = df.groupby('skill_name').agg(
        job_count=('job_id', 'count'),
        average_salary=('max_salary', 'mean'),
        average_min_salary=('min_salary', 'mean')
    ).reset_index()

    # Replacing NaN values with 0 for average_salary in case some skills do not have salary data
    skill_data_page1['average_salary'].fillna(0, inplace=True)
    skill_data_page1['average_min_salary'].fillna(0, inplace=True)

    # Aggregate data by skill_name for page 2
    skill_data_page2 = df.groupby('skill_name').agg(
        job_count=('job_id', 'count'),
        average_salary=('max_salary', 'mean')
    ).reset_index()

    # Replacing NaN values with 0 for average_salary in case some skills do not have salary data
    skill_data_page2['average_salary'].fillna(0, inplace=True)

    # Aggregate data by skill_name and formatted_experience_level for page 3
    experience_skill_data = df.groupby(['formatted_experience_level', 'skill_name']).size().reset_index(name='job_count')

    # Aggregate total job count by skill_name
    total_job_count_by_skill = experience_skill_data.groupby('skill_name')['job_count'].sum().reset_index()

    # Sort skills by total job count
    sorted_skills = total_job_count_by_skill.sort_values('job_count', ascending=False)['skill_name']

    # Ensure experience_skill_data is sorted by skill_name based on total job count
    experience_skill_data['skill_name'] = pd.Categorical(experience_skill_data['skill_name'], categories=sorted_skills, ordered=True)
    experience_skill_data = experience_skill_data.sort_values('skill_name')

    # Sort data by job count for all pages
    skill_data_page1 = skill_data_page1.sort_values('job_count', ascending=False)
    skill_data_page2 = skill_data_page2.sort_values('job_count', ascending=False)
    experience_skill_data = experience_skill_data.sort_values('job_count', ascending=False)

    # Define the page navigation
    page = st.selectbox("Choose a page:", ["Page 1: Top Skills by Job Postings Count", "Page 2: Average Salary by Skill", "Page 3: Skills and Experience Levels"])

    # Display the selected visualization
    fig = create_visualization(page, skill_data_page1, skill_data_page2, experience_skill_data)
    st.plotly_chart(fig, use_container_width=True)
