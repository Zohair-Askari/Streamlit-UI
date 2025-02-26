import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import time
import base64

st.set_page_config(
    page_title="DinoPedia",
    layout="wide",
    page_icon="🦖"
)

# Set the background and text colors
st.markdown("""
<style>
    [data-testid="stAppViewContainer"] {
        background-color: #0f172a;
        color: #f8fafc;
    }
    h1, h2, h3 {
        color: #2dd4bf;
        font-family: Arial, sans-serif;
        border-bottom: 2px solid #2dd4bf;
        padding-bottom: 0.3rem;
    }
    [data-testid="stSidebar"] {
        background-color: #1e293b !important;
    }
    .stButton>button {
        background-color: #2dd4bf !important;
        color: #0f172a !important;
    }
    .stTextInput>div>div>input {
        background-color: #1e293b !important;
        color: white !important;
    }
    .stSelectbox>div>div>div {
        background-color: #1e293b !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

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

def sidebar_nav():
    st.sidebar.title("Dino-Pedia")
    page = st.sidebar.radio("Choose your adventure:", [
        "🏠 Home", "📊 Dino Stats", "🌍 Dino World Tour", 
        "🍕 Dino Diet Club", "📌 Data Insights"
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

def search_dinosaurs_textual(df, selected_column):
    st.subheader("🔍 Dino Search Results")
    if selected_column not in df.columns:
        st.error("Invalid column selection!")
        return ""

    unique_values = df[selected_column].dropna().unique().tolist()
    selected_value = st.selectbox(f"Select a value from {selected_column}:", sorted(unique_values), index=0)

    results = df[df[selected_column].astype(str).str.lower() == str(selected_value).lower()]

    if results.empty:
        return "🦕 No dinos found for the selected criteria! Try searching 'Saraikimasaurus' 🇵🇰"

    output = []
    for _, row in results.iterrows():
        dino_info = f"""
        ### {row.get('name', 'Unknown')}
        **📏 Length:** {row.get('length', 'Unknown')}m  
        **🍽️ Diet:** {row.get('diet', 'Unknown')}  
        **⏳ Period:** {row.get('period', 'Unknown')}  
        **🌍 Location:** {row.get('lived_in', 'Unknown')}  
        **🔍 Discoverer:** {row.get('named_by', 'Unknown')}  
        """
        output.append(dino_info)

    return "\n\n".join(output)

def search_and_highlight_map(df):
    st.subheader("🌍 Dino Map Search")
    search_category = st.selectbox("Search by:", df.columns.tolist(), index=0)

    filtered_df = df.copy()
    pakistan_alert = False

    
    if pd.api.types.is_numeric_dtype(df[search_category]):
        search_term = st.number_input(f"Enter {search_category}:",
                                      value=float(df[search_category].min()))
        filter_condition = (df[search_category] == search_term)
    else:
        unique_values = df[search_category].dropna().unique().tolist()
        selected_terms = st.multiselect(
            f"Select {search_category}(s):",
            options=unique_values,
            default=unique_values
        )
        filter_condition = df[search_category].isin(selected_terms)

    
        if 'lived_in' in search_category.lower() and any('pakistan' in str(x).lower() for x in selected_terms):
            pakistan_alert = True

    if st.button("Update Map") or not pd.api.types.is_numeric_dtype(df[search_category]):
        if not pd.api.types.is_numeric_dtype(df[search_category]) and len(selected_terms) == 0:
            st.warning("Yo fam, pick at least one value! 😂")
            return

        
        if pakistan_alert:
           st.markdown("""
🚨 **BREAKING NEWS FROM THE FOSSIL FRONT** 🚨

🎬 *Lahore Jurassic Park* production stuck — rumor has it, the squad’s just one Pakistani fossil short from a Netflix deal! 💀✨ 

🦴 **Sir Abbass Abbassi**: The “KFC bone specialist” — claims it’s “finger-lickin’ research.” 🍗💀 “Bro out here confusing zinger bones for dino fossils. Jurassic Park delayed ‘cause sir’s chasing extra crispy ‘evidence.’ Someone get him a paleontology degree with a side of fries. 🤡🍟”

💅 **Miss Mustabshira**: Mehndi fossil influencer — leaves dino-sized handprints at shaadis. 🎨💃 “Serving fossil-core realness — mehndi so ancient, even velociraptors RSVP’d. Wedding or prehistoric exhibit? Spielberg can’t tell. 💀✨”

🏏 **Anas Ahmad**: Fossil-for-PSL trader — caught swapping trilobites for PSL tickets. 🏟️🤣 “Bro said, ‘Extinction who? PSL front row or bust!’ Trading fossils faster than crypto, fr. 🦕💸”

🕒 *Word on the street: Squad too busy chasing Pakistani dinos to complete their collection — just one fossil short of premiering* **“Jurassic Park: Lahore Drift.”** 💀😂

""", unsafe_allow_html=True)


        filtered_df = df[filter_condition]

        if not filtered_df.empty:
            st.write(f"📌 Showing {len(filtered_df)} matching specimens — certified dino drip! 🦕✨")

            country_counts = filtered_df.groupby('lived_in')['name'].agg(
                lambda x: ', '.join(x)).reset_index()
            country_counts['Count'] = country_counts['name'].apply(lambda x: len(x.split(',')))

            title_term = (f"{search_category} = {search_term}" if pd.api.types.is_numeric_dtype(df[search_category])
                          else f"{search_category} in {', '.join(selected_terms)}")

            fig = px.choropleth(country_counts,
                                locations="lived_in",
                                locationmode='country names',
                                color="Count",
                                hover_name="lived_in",
                                hover_data={"name": True},
                                title=f"🦖 Dino Distribution: {title_term}",
                                color_continuous_scale=px.colors.sequential.Plasma)

            fig.update_layout(
                geo=dict(bgcolor='rgba(0,0,0,0)'),
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("🕵️ No fossils found — maybe they're ghosting us? LOL 👻🥟")

    if pd.api.types.is_numeric_dtype(df[search_category]) and not st.session_state.get('map_initialized'):
        country_counts = df.groupby('lived_in')['name'].agg(
            lambda x: ', '.join(x)).reset_index()
        country_counts['Count'] = country_counts['name'].apply(lambda x: len(x.split(',')))

        fig = px.choropleth(country_counts,
                            locations="lived_in",
                            locationmode='country names',
                            color="Count",
                            hover_name="lived_in",
                            hover_data={"name": True},
                            title="🌎 Global Dino Drip Distribution",
                            color_continuous_scale=px.colors.sequential.Plasma)

        fig.update_layout(
            geo=dict(bgcolor='rgba(0,0,0,0)'),
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white'
        )
        st.plotly_chart(fig, use_container_width=True)
        st.session_state.map_initialized = True

def main():
    df = load_data()
    page = sidebar_nav()

    if page == "🏠 Home":
        st.title("Welcome to DinoPedia! 🦖")
        st.write("""🔥 Dragons? Overrated. They breathe fire, hoard gold, and worst of all—completely made up! 🐉🚫

🦕 Dinosaurs? Absolute legends. They actually existed, ruled the Earth for millions of years, and didn’t need wings to be terrifying! Whether they were stomping around as the size of buses or running at speeds that’d make a cheetah jealous, these prehistoric titans were the real deal.

So if you’re here looking for dragons… sorry, we only deal in hardcore, scientifically verified awesomeness.

Welcome to DinoPedia—where every fossil tells a story! 🦴📖""")
        st.image(
    r"https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.wallpaperflare.com%2Fhumor-dinosaur-wallpaper-congj&psig=AOvVaw0cxUyJLKmK7FF15_FOwAKp&ust=1740663658280000&source=images&cd=vfe&opi=89978449&ved=0CBQQjRxqFwoTCNC539K74YsDFQAAAAAdAAAAABAE",
    caption="🎧 Dino Vibes Only",
    use_container_width=True 
)

        selected_column = st.selectbox("Select a column to explore:", df.columns, index=0)
        if selected_column:
            search_results = search_dinosaurs_textual(df, selected_column)
            if search_results:
                st.markdown(search_results, unsafe_allow_html=True)

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

            sized_dinos = df[df['length'].between(*length_range)]

            if not sized_dinos.empty:
                st.write(f"Found {len(sized_dinos)} dinos between {length_range[0]}m and {length_range[1]}m! 🚀")
                col_a, col_b, col_c = st.columns([1, 1, 1], gap="large")
                chunk_size = (len(sized_dinos) + 2) // 3

                for i, column in enumerate([col_a, col_b, col_c]):
                    for _, row in sized_dinos.iloc[i * chunk_size:(i + 1) * chunk_size].iterrows():
                        dino_info = f"**{row['name']}**: {row['length']} meters"
                        column.markdown(dino_info)
            else:
                st.info("No dinos found in this length range. Try adjusting the slider! 🦖")

            fig = px.histogram(
                df, 
                x='length', 
                title='Dino Length Distribution',
                labels={'length': 'Length (meters)'},
                nbins=20,
                color_discrete_sequence=['lightgray']
            )

            fig.add_trace(
                px.histogram(
                    sized_dinos, 
                    x='length', 
                    nbins=20,
                    color_discrete_sequence=['#FF4B4B']
                ).data[0]
            )

            fig.add_vline(x=length_range[0], line_dash="dash", line_color="green")
            fig.add_vline(x=length_range[1], line_dash="dash", line_color="green")
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

            if not sized_dinos.empty:
                st.success(f"Currently showing {len(sized_dinos)} dinos in the {length_range[0]}m–{length_range[1]}m range. Totally dino-mite! 🌟")
            else:
                st.warning("Uh-oh! No dinos here. Adjust that slider, explorer! 🦖✨")
        
    elif page == "🌍 Dino World Tour":
        st.title("Global Dino Explorer 🌍")
        st.write("""Aur yeh dekho irony—dinos bina passport kay abroad ghoom rahay thay, aur mai passport hote huay bhi Pakistan mai phansa hua hoon. 🤡✈️""")
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
