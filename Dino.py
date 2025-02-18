import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns

# Load the dataset
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('data.csv')
        if 'length' in df.columns:
            df['length'] = pd.to_numeric(df['length'].astype(str).str.replace('m', '', regex=False), errors='coerce')
        return df
    except Exception as e:
        st.error(f"Oops, the dinos are on strike! Error loading data: {e}")
        return pd.DataFrame()

# Sidebar navigation 
def sidebar_nav():
    st.sidebar.title("Dino Dashboard 🦕✨")
    page = st.sidebar.radio("Choose your adventure:", [
        "🏠 Home", "📊 Dino Stats", "🌍 Dino World Tour", "🍕 Dino Diet Club", "📌 Data Insights"
    ], index=0)
    return page

def show_scatter_plot(df):
    st.subheader("🎨 Dino Scatter Madness!")
    if df.empty:
        st.warning("No data available!")
        return
    
    num_columns = df.select_dtypes(include=['number']).columns.tolist()
    if len(num_columns) < 2:
        st.warning("Not enough numerical columns for scatter plot!")
        return
    
    col1, col2 = st.columns(2)
    with col1:
        x_axis = st.selectbox("Select X-axis", num_columns, index=0)
    with col2:
        y_axis = st.selectbox("Select Y-axis", num_columns, index=1)
    
    fig = px.scatter(df, x=x_axis, y=y_axis, color='diet', hover_data=['name'])
    st.plotly_chart(fig, key="scatter_plot")

def compare_diets(df):
    if 'diet' in df.columns:
        st.subheader("🍽️ Dino Diet Showdown!")
        diet_options = df['diet'].dropna().unique().tolist()
        selected_diets = st.multiselect("Select diets to compare:", diet_options, default=diet_options[:2])
        
        if selected_diets:
            filtered_df = df[df['diet'].isin(selected_diets)]
            diet_counts = filtered_df['diet'].value_counts().reset_index()
            diet_counts.columns = ['diet', 'count']
            
            fig = px.pie(diet_counts, names='diet', values='count', title="Dino Diet Breakdown")
            st.plotly_chart(fig, key="diet_pie_chart")
        else:
            st.warning("Select at least one diet type to compare!")

def show_correlation_heatmap(df):
    st.subheader("📊 Correlation Heatmap")
    num_df = df.select_dtypes(include=['number'])
    if num_df.empty:
        st.warning("No numerical data available!")
        return
    
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(num_df.corr(), annot=True, cmap='coolwarm', fmt='.2f', ax=ax)
    st.pyplot(fig)

def data_insights(df):
    st.title("Deep Dive into Dino Data 📊")
    st.image("https://jonathanemmett.com/wp-content/uploads/2023/08/Tyrannosaurs-Feathers-Glamosaurus.jpg")
    st.write("""Beta, T-Rex padhai kar raha hai—ab toh data bhi hil jayega! Itni mehnat sirf do log karte hain: ek board exam wale bacche, aur ek yeh jo soch raha hai, ‘Agar pehle padh leta toh meteor ka data analyze karke bach jata!’" 😆📚🦖""")
    st.write("Compare two columns and explore their relationship!")
    
    col1, col2 = st.columns(2)
    with col1:
        column1 = st.selectbox("Select first column", df.columns, index=0)
    with col2:
        column2 = st.selectbox("Select second column", df.columns, index=1)
    
    if column1 and column2:
        st.subheader(f"Comparison: {column1} vs {column2}")
        
        st.subheader("Distribution Analysis")
        col1, col2 = st.columns(2)
        with col1:
            fig1 = px.histogram(df, x=column1, title=f"Distribution of {column1}")
            st.plotly_chart(fig1, key="distribution_col1")
        with col2:
            fig2 = px.histogram(df, x=column2, title=f"Distribution of {column2}")
            st.plotly_chart(fig2, key="distribution_col2")

def search_dinosaurs(df, search_term, search_category):
    if search_category == "Name":
        return df[df['name'].str.contains(search_term, case=False, na=False)]
    elif search_category == "Length":
        try:
            length_val = float(search_term)
            return df[df['length'] == length_val]
        except ValueError:
            return pd.DataFrame()
    elif search_category == "Named By":
        return df[df['named_by'].str.contains(search_term, case=False, na=False)]
    elif search_category == "Period Lived In":
        return df[df['period'].str.contains(search_term, case=False, na=False)]
    return pd.DataFrame()

def search_and_highlight_map(df):
    st.subheader("🌍 Dino Map Search")
    
    # Dynamically generate search options based on all columns in the dataset
    search_category = st.selectbox("Search by:", df.columns.tolist(), index=0)
    
    # Generate search term input based on the selected column's data type
    if pd.api.types.is_numeric_dtype(df[search_category]):
        search_term = st.number_input(f"Enter {search_category}:", value=float(df[search_category].min()))
    else:
        unique_values = df[search_category].dropna().unique().tolist()
        search_term = st.selectbox(f"Select {search_category}:", unique_values, index=0)
    
    if st.button("Search"): 
        filtered_df = pd.DataFrame()
        
        # Filter the DataFrame based on the selected column and search term
        if pd.api.types.is_numeric_dtype(df[search_category]):
            filtered_df = df[df[search_category] == search_term]
        else:
            filtered_df = df[df[search_category].astype(str).str.contains(str(search_term), case=False, na=False)]
        
        if not filtered_df.empty:
            st.write(f"Found {len(filtered_df)} matching dinosaurs!")
            
            # Group by 'lived_in' and aggregate dinosaur names
            country_counts = filtered_df.groupby('lived_in')['name'].agg(lambda x: ', '.join(x)).reset_index()
            country_counts['Count'] = country_counts['name'].apply(lambda x: len(x.split(',')))
            
            # Create a choropleth map
            fig = px.choropleth(country_counts, 
                                locations="lived_in",
                                locationmode='country names',
                                color="Count",
                                hover_name="lived_in",
                                hover_data={"name": True},
                                title=f"Dino Distribution Map ({search_category}: {search_term})")
            st.plotly_chart(fig, key="search_highlight_map")
        else:
            st.warning("No matching results found!")

# Main App 
def main():
    st.set_page_config(page_title="DinoPedia", layout="wide", page_icon="🦕")
    df = load_data()
    page = sidebar_nav()
    
    if page == "🏠 Home":
        st.title("Welcome to DinoPedia! 🦖")
        st.write("""🔥 Dragons? Overrated. They breathe fire, hoard gold, and worst of all—completely made up! 🐉🚫

🦕 Dinosaurs? Absolute legends. They actually existed, ruled the Earth for millions of years, and didn’t need wings to be terrifying! Whether they were stomping around as the size of buses or running at speeds that’d make a cheetah jealous, these prehistoric titans were the real deal.

So if you’re here looking for dragons… sorry, we only deal in hardcore, scientifically verified awesomeness.

Welcome to DinoPedia—where every fossil tells a story! 🦴📖""")
        st.image("https://c4.wallpaperflare.com/wallpaper/365/413/124/humor-dinosaur-wallpaper-preview.jpg")
        
        if st.checkbox("Peek at raw dino data 👀"):
            st.dataframe(df)
        
        search_category = st.selectbox("Search by:", ["Name", "Length", "Named By", "Period Lived In"], index=0)
        search_term = st.text_input("Enter your search term:")
        if st.button("Search"):
            results = search_dinosaurs(df, search_term, search_category)
            if not results.empty:
                st.write(f"Found {len(results)} matching dinosaurs:")
                st.dataframe(results)
            else:
                st.warning("No matching results found!")
        
    elif page == "📊 Dino Stats":
        st.title("Dino-mite Statistics! 📈")
        st.subheader("Size-o-saurus Selector 🔍")
        st.write("""🦕 Big dino? Small dino? YOLO, let’s find out!

Listen, size totally mattered in the dino world. Some were chonksters the size of buses, while others were basically prehistoric chickens. Whether you’re looking for absolute units like the Argentinosaurus or tiny dudes who could sneak into your backpack (not recommended 🫠), we got you covered.

🔎 Pick your size range below, and let’s see which Jurassic MVPs fit your vibe.

Because let’s be real—if dinosaurs still existed, some of y’all would try to put one on a leash. 💀😂""")
        st.image("https://i.ytimg.com/vi/kuB7QN4EJdY/maxresdefault.jpg")
        st.write("""Swipe left for danger, swipe right for dino-mite! Meet T-Rex—the original 'big bite, no chill' legend. If he had a dating profile, his bio would be: ‘Short arms, big appetite, and absolutely no table manners.’" 😆""")
        
        if 'length' in df.columns:
            min_length, max_length = df['length'].min(), df['length'].max()
            length_range = st.slider("Select dino length range (meters):", 
                                      min_value=min_length, 
                                      max_value=max_length, 
                                      value=(min_length, max_length))
            
            # Filter dinosaurs based on selected range
            sized_dinos = df[df['length'].between(*length_range)]
            
            # Create comparison visualization
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.write(f"Found {len(sized_dinos)} dinos in this range!")
                st.dataframe(sized_dinos[['name', 'length']])
            
            
                
                # Create figure with two histograms
                fig = px.histogram(
                    df, 
                    x='length', 
                    title='Dino Length Distribution',
                    labels={'length': 'Length (meters)'},
                    nbins=20,
                    color_discrete_sequence=['lightgray']
                )
                
                # Add filtered data as overlay
                fig.add_trace(
                    px.histogram(
                        sized_dinos, 
                        x='length', 
                        nbins=20,
                        color_discrete_sequence=['#FF4B4B']
                    ).data[0]
                )
                
                # Add range lines
                fig.add_vline(x=length_range[0], line_dash="dash", line_color="green")
                fig.add_vline(x=length_range[1], line_dash="dash", line_color="green")
                
                # Update layout
                fig.update_layout(
                    bargap=0.1,
                    showlegend=False,
                    annotations=[
                        dict(
                            x=0.5,
                            y=-0.2,
                            showarrow=False,
                            text="Gray = Full dataset | Red = Selected range",
                            xref="paper",
                            yref="paper"
                        )
                    ]
                )
        
            st.plotly_chart(fig)
        
    elif page == "🌍 Dino World Tour":
        st.title("Global Dino Explorer 🌍")
        st.write("""Shayad dinos ko Pakistan ki load shedding pasand nahi thi, tabhi aik bhi yahan nahi aya—yeh data bhi confirm karta hai! 🤯💡  
Aur yeh dekho irony—dinos bina passport kay abroad ghoom rahay thay, aur mai passport hote huay bhi Pakistan mai phansa hua hoon. 🤡✈️""")
        st.image("https://images.liverpoolmuseums.org.uk/styles/focal_point_2_1/public/2020-04/dinosaur-tour.jpg")
        st.text("""Behold our ancient VIPs—these dino skeletons be like family antiques! They stomped around Earth so long ago that even your great-great-great-great dadaji would’ve said, ‘Wah beta, purane din yaad aa gaye!’" 😆""")
        search_and_highlight_map(df)

    elif page == "🍕 Dino Diet Club":
        st.title("Prehistoric Food Court 🍔")
        st.write("""🍕 Dino Diet Club – Where Every Bite is Prehistoric!**  

So apparently, some dinos were strict vegetarians (gym bros of the past 🥦💪), some were full-time meat lovers (OG BBQ fans 🍗🔥), and a few just ate whatever they found (the ‘jo milay wo khalo’ gang 🍕🍔).  

Meanwhile, hum humans? Ek din diet pe, aglay din ‘bas aaj cheat day hai’ mode on. 🤡😂""")
        st.image("https://st2.depositphotos.com/1036149/6066/i/450/depositphotos_60667353-stock-photo-fun-dinosaur-with-burger.jpg")
        st.text("""Yeh dino bas Jurassic nahi, zara zyada hi classic nikla! Burger haath mein, glasses aankhon pe—lagta hai KFC ka secret recipe chupa ke laya hai! Shhh… Colonel Sanders sun lega toh bucket nahi, case milega!" 😆🍔🦖""")
        compare_diets(df)

    elif page == "📌 Data Insights":
        data_insights(df)

if __name__ == "__main__":
    main()