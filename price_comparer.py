import streamlit as st
import requests
from bs4 import BeautifulSoup

headers = {'User-Agent': 'Mozilla/5.0'}

# Function to clean the price (remove currency symbol and convert to float)
def clean_price(price):
    if price:
        return float(price.replace('₹', '').replace(',', '').strip())  # Remove symbols, commas, and convert to float
    return None

# Function to fetch BigBasket price
def get_bigbasket_price(product_name):
    try:
        url = f"https://www.bigbasket.com/ps/?q={product_name.replace(' ', '%20')}"
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        product = soup.select_one('div.ProductCard__cardWrapper')
        
        if not product:
            return None, None
        
        title = product.select_one('div.ProductCard__name')
        price = product.select_one('span.DiscountedPrice')
        
        # Debug: Print raw HTML (optional)
        # print(soup.prettify())
        
        return (title.text.strip() if title else None, price.text.strip() if price else None)
    
    except Exception as e:
        st.error(f"Error fetching BigBasket price: {e}")
        return None, None

# Function to fetch KPN Fresh price
def get_kpn_price(product_name):
    try:
        url = f"https://www.kpnfresh.com/catalogsearch/result/?q={product_name.replace(' ', '+')}"
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        product = soup.select_one('li.item.product.product-item')
        
        if not product:
            return None, None
        
        title = product.select_one('strong.product.name.product-item-name a')
        price = product.select_one('span.price')
        
        return (title.text.strip() if title else None, price.text.strip() if price else None)
    
    except Exception as e:
        st.error(f"Error fetching KPN Fresh price: {e}")
        return None, None

# Streamlit UI
st.title("🛒 Real-time Fruit & Vegetable Price Comparator")
product_input = st.text_input("Enter a product name (e.g., carrot, tomato)")

if product_input:
    st.write(f"🔍 Searching for **{product_input}**...")
    bb_title, bb_price = get_bigbasket_price(product_input)
    kpn_title, kpn_price = get_kpn_price(product_input)

    st.subheader("BigBasket")
    if bb_title and bb_price:
        st.write(f"**{bb_title}** – {bb_price}")
    else:
        st.write("❌ Product not found.")

    st.subheader("KPN Fresh")
    if kpn_title and kpn_price:
        st.write(f"**{kpn_title}** – {kpn_price}")
    else:
        st.write("❌ Product not found.")

    # Price comparison logic
    if bb_price and kpn_price:
        bb_val = clean_price(bb_price)
        kpn_val = clean_price(kpn_price)
        
        if bb_val is not None and kpn_val is not None:
            st.subheader("💰 Price Comparison")
            if bb_val < kpn_val:
                st.success("BigBasket is cheaper.")
            elif kpn_val < bb_val:
                st.success("KPN Fresh is cheaper.")
            else:
                st.info("Both have the same price.")
        else:
            st.warning("⚠️ Couldn't clean price properly.")
