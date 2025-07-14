import langchain_helper as lch
import streamlit as st

st.title("Pet's Name Generator")

animal_type = st.sidebar.selectbox("What is your pet", ("Cat", "Dog", "Cow", "Dinosaur"))


pet_color = st.sidebar.text_area(f"What color is your {animal_type}?", max_chars=15)



if pet_color:
    response = lch.generate_pet_name(animal_type, pet_color)
    st.text(response)