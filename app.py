import streamlit as st
import requests

# Function to fetch a random recipe
def fetch_random_recipe():
    try:
        response = requests.get('https://www.themealdb.com/api/json/v1/1/random.php')
        response.raise_for_status()
        data = response.json()
        meal = data['meals'][0]
        return meal
    except requests.RequestException as e:
        st.error("Failed to fetch a random recipe. Please try again later.")
        st.error(f"Error: {e}")
        return None

# Function to fetch recipes based on ingredients
def fetch_recipes_by_ingredients(ingredients):
    try:
        ingredient_list = [ingredient.strip() for ingredient in ingredients.split(',') if ingredient.strip()]
        if not ingredient_list:
            st.warning("Please enter at least one ingredient.")
            return []

        # Initialize a set to store common recipes
        common_recipes = None

        for ingredient in ingredient_list:
            response = requests.get(f'https://www.themealdb.com/api/json/v1/1/filter.php?i={ingredient}')
            response.raise_for_status()
            data = response.json()
            meals = data.get('meals')
            if meals:
                meal_names = set(meal['strMeal'] for meal in meals)
                if common_recipes is None:
                    common_recipes = meal_names
                else:
                    common_recipes = common_recipes.intersection(meal_names)
            else:
                st.warning(f"No recipes found with the ingredient: {ingredient}")
                return []

        if common_recipes:
            recipes = []
            for recipe_name in common_recipes:
                response = requests.get(f'https://www.themealdb.com/api/json/v1/1/search.php?s={recipe_name}')
                response.raise_for_status()
                data = response.json()
                meal = data['meals'][0]
                recipes.append(meal)
            return recipes
        else:
            st.warning("No recipes found with the specified ingredients.")
            return []
    except requests.RequestException as e:
        st.error("Failed to fetch recipes based on ingredients. Please try again later.")
        st.error(f"Error: {e}")
        return []

# Function to display a single recipe
def display_recipe(meal):
    if not meal:
        return

    st.image(meal['strMealThumb'], use_column_width=True)
    st.title(meal['strMeal'])

    st.subheader("Ingredients:")
    ingredients = []
    for i in range(1, 21):
        ingredient = meal.get(f'strIngredient{i}')
        measure = meal.get(f'strMeasure{i}')
        if ingredient and ingredient.strip():
            ingredients.append(f"{measure.strip()} {ingredient.strip()}")
    st.write(", ".join(ingredients))

    st.subheader("Instructions:")
    st.write(meal['strInstructions'])

    if meal.get('strSource'):
        st.markdown(f"[View Full Recipe]({meal['strSource']})")
    elif meal.get('strYoutube'):
        st.markdown(f"[Watch on YouTube]({meal['strYoutube']})")

# App Header
st.title("🍽️ Recipe of the Day")

# User Choice
choice = st.radio("Do you want a random recipe?", ("Yes", "No"))

if choice == "Yes":
    meal = fetch_random_recipe()
    display_recipe(meal)
else:
    ingredients = st.text_input("Enter the ingredients you have (separated by commas):", "")
    if st.button("Find Recipes"):
        recipes = fetch_recipes_by_ingredients(ingredients)
        if recipes:
            st.success(f"Found {len(recipes)} recipe(s) matching your ingredients:")
            for meal in recipes:
                st.markdown("---")
                display_recipe(meal)
