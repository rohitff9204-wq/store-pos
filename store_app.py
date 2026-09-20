import datetime
import os
import pandas as pd
from PIL import Image
import streamlit as st

# 1. Pehle image file ko load karein (Is line ko st.set_page_config ke upar dalein)
logo_image = Image.open('store_logo.png')

# 2. Fir page icon mein us variable ko daal dein
st.set_page_config(
    page_title='Meridukan', 
    page_icon=logo_image, 
    layout='wide'
)

st.markdown("""
<style>

/* Hide Streamlit footer */
footer {
    display: none !important;
    visibility: hidden !important;
}

/* Hide bottom decoration */
[data-testid="stDecoration"] {
    display: none !important;
}

/* Hide Streamlit toolbar */
[data-testid="stToolbar"] {
    display: none !important;
}

/* Hide fullscreen button */
button[title="View fullscreen"] {
    display: none !important;
}

/* Hide element toolbar */
[data-testid="stElementToolbar"] {
    display: none !important;
}

/* Hide status widget */
[data-testid="stStatusWidget"] {
    display: none !important;
}

</style>
""", unsafe_allow_html=True)
st.markdown("<p style='font-size: 13px; color: gray; margin-bottom: 0px;'>Created by: <a href='https://instagram.com' target='_blank' style='color: #E1306C; text-decoration: none; font-weight: bold;'><img src='https://wikimedia.org' width='13' style='vertical-align: middle; margin-right: 4px;'>@rohitx_844</a></p>", unsafe_allow_html=True)
# Custom PWA Manifest aur Icon Injector for Mobile/Desktop Install Prompt
st.markdown(
    """
    <link rel="manifest" href="/manifest.json">
    <meta name="theme-color" content="#000000">
    <script>
        // Dynamically inject manifest link if missing
        if (!document.querySelector('link[rel="manifest"]')) {
            const link = document.createElement('link');
            link.rel = 'manifest';
            link.href = '/manifest.json';
            document.head.appendChild(link);
        }
    </script>
""",
    unsafe_allow_html=True,
)
# PWA Manifest aur Custom Icon injector for Mobile/Desktop Install
st.markdown(
    """
    <link rel="manifest" href="/manifest.json">
    <meta name="theme-color" content="#000000">
""",
    unsafe_allow_html=True,
)

# Files to save data permanently
DATA_FILE = 'dukan_stock.csv'
SALES_FILE = 'dukan_sales.csv'
UDHAAR_FILE = 'dukan_udhaar.csv'
CONFIG_FILE = 'dukan_config.csv'


@st.cache_data
def load_data():
  try:
    return pd.read_csv(DATA_FILE)
  except FileNotFoundError:
    df = pd.DataFrame(
        {
            'Product Name': ['Aata (10kg)', 'Chawal (5kg)', 'Cheeni (1kg)'],
            'Price (₹)': [350.0, 250.0, 45.0],
            'Quantity': [20, 15, 3],
        }
    )
    df.to_csv(DATA_FILE, index=False)
    return df


def load_sales():
  try:
    return pd.read_csv(SALES_FILE)
  except FileNotFoundError:
    return pd.DataFrame(columns=['Date', 'Product', 'Quantity', 'Total Price'])


def load_udhaar():
  try:
    return pd.read_csv(UDHAAR_FILE)
  except FileNotFoundError:
    return pd.DataFrame(
        columns=[
            'Date',
            'Customer Name',
            'Phone Number',
            'Udhaar Amount (₹)',
            'Status',
        ]
    )


def load_config():
  try:
    cfg = pd.read_csv(CONFIG_FILE)
    return cfg.iloc[0]['StoreName'], cfg.iloc[0]['OwnerName']
  except FileNotFoundError:
    return 'Smart Kirana Store', 'Dukaan Malik'


# Load State
if 'inventory' not in st.session_state:
  st.session_state.inventory = load_data()

if 'cart' not in st.session_state:
  st.session_state.cart = []

if 'last_bill' not in st.session_state:
  st.session_state.last_bill = ''

store_name, owner_name = load_config()

# --- CSS FOR CIRCLE IMAGE STYLING ---
st.markdown(
    """
    <style>
    .owner-circle-img {
        border-radius: 50%;
        width: 100px;
        height: 100px;
        object-fit: cover;
        border: 3px solid #ff4b4b;
        display: block;
        margin-left: auto;
        margin-right: auto;
    }
    
    /* Keep sidebar visible */
[data-testid="stSidebar"] {
    display: block !important;
    visibility: visible !important;
    min-width: 280px !important;
    width: 280px !important;
}

[data-testid="stSidebarContent"] {
    visibility: visible !important;
    display: block !important;
}
    </style>
""",
    unsafe_allow_html=True,
)

# --- SIDEBAR ---
st.sidebar.title('🏪 Dukaan Control Panel')

# Sidebar Navigation
menu = st.sidebar.selectbox(
    'Dukan Menu',
    [
        '🧾 Cart & Billing Counter',
        '📊 Stock & Low Stock Alert',
        '➕ Naya Saaman Jodein',
        '✏️ Product Edit / Update',
        '🗑️ Saaman Hatayein',
        '📖 Udhaar Khata (Credit Book)',
        '📈 Sales Report & Analytics',
        '⚙️ Store & Profile Settings',
    ],
)

# App Header
st.title(f'🛒 {store_name}')
st.caption(f'Sanchalak (Owner): {owner_name} | Smart Management & POS System')


# ==========================================
# 1. BILLING & CART COUNTER (MANUAL & FLEXIBLE)
# ==========================================
if menu == '🧾 Cart & Billing Counter':
  st.header('🧾 Grahak Bill Banayein (Manual Entry)')

  col1, col2 = st.columns(2)

  with col1:
    st.subheader('Saman Jodein')
    
    # User khud naam aur quantity type karega
    item_name = st.text_input('Grahak Name')
    item_name = st.text_input('Saman ka Naam')
    item_qty = st.text_input('Wajan ya Quantity')
    item_price = st.number_input('Is saaman ka Price (₹)', min_value=0.0, step=1.0)

    if st.button('Cart Me Jodein'):
      if item_name and item_qty and item_price > 0:
        st.session_state.cart.append({
            'Product': item_name,
            'Quantity': item_qty,
            'Total': float(item_price),
        })
        st.success(f"'{item_name}' cart me jud gaya!")
        # Clear fields (Streamlit re-runs, inputs will reset to default)
      else:
        st.error('Kripya Saman ka naam, quantity aur price sahi bharein.')

  with col2:
    st.subheader('🛒 Current Cart')
    if len(st.session_state.cart) > 0:
      cart_df = pd.DataFrame(st.session_state.cart)
      st.dataframe(cart_df, use_container_width=True)

      grand_total = cart_df['Total'].sum()
      st.markdown(f'### 💰 Grand Total: ₹ {grand_total}')

      st.markdown('---')
      # Payment and Balance Calculation
      paid_amount = st.number_input('Grahak ne kitna paisa diya? (Paid ₹)', min_value=0.0, step=10.0)
      balance_amount = grand_total - paid_amount

      if balance_amount > 0:
        st.warning(f'⚠️ **Baki (Due): ₹ {balance_amount}**')
      elif balance_amount < 0:
        st.info(f'🔄 **Grahak ko wapas karein: ₹ {abs(balance_amount)}**')
      else:
        st.success('✅ **Poora Paisa Mil Gaya (No Due)**')

      if st.button('Bill Generate Karein'):
        current_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        sales_records = []
        
        # Bill Formatting
        bill_text = f"==========================\n"
        bill_text += f"       {store_name}       \n"
        bill_text += f"==========================\n"
        bill_text += f"📅 Date: {current_date}\n"
        bill_text += f"--------------------------\n"
        
        for item in st.session_state.cart:
          p_name = item['Product']
          q_sold = item['Quantity']
          t_price = item['Total']

          sales_records.append({
              'Date': current_date,
              'Product': p_name,
              'Quantity': q_sold,
              'Total Price': t_price,
          })
          bill_text += f"• {p_name} ({q_sold}) = ₹{t_price}\n"

        bill_text += f"--------------------------\n"
        bill_text += f" KUL RAKAM (TOTAL) : ₹{grand_total}\n"
        bill_text += f" MILA (PAID)       : ₹{paid_amount}\n"
        
        if balance_amount > 0:
          bill_text += f" BAKI (DUE)        : ₹{balance_amount}\n"
        
        bill_text += f"==========================\n"
        bill_text += f"   Dhanyawad! Phir Aayiyega 🙏\n"
        
        st.session_state.last_bill = bill_text

        # Sales file me update karein
        sales_df = load_sales()
        updated_sales = pd.concat(
            [sales_df, pd.DataFrame(sales_records)], ignore_index=True
        )
        updated_sales.to_csv(SALES_FILE, index=False)

        st.session_state.cart = []  # Cart khali kar do
        st.balloons()
        st.success('Bill safaltapoorvak generate ho gaya hai! Niche dekhein.')

    else:
      st.info('Cart khali hai. Pehle saaman jodein.')

  # Show generated bill and Download button
if st.session_state.last_bill:
    st.markdown('---')
    st.subheader('🧾 Aapka Pukka Bill')
    
    # WhatsApp पर कॉपी करने के लिए टेक्स्ट एरिया
    st.text_area('WhatsApp Par Bhejne ke liye copy karein:', st.session_state.last_bill, height=200)
    
    # --- टेक्स्ट को इमेज (फोटो) में बदलने का लॉजिक ---
    from PIL import Image, ImageDraw
    import io
    import datetime
    
    # बिल के टेक्स्ट को लाइनों में तोड़ें और इमेज साइज तय करें
    lines = st.session_state.last_bill.split('\n')
    line_height = 25
    img_height = max(200, len(lines) * line_height + 40)
    
    # सफेद बैकग्राउंड वाली इमेज बनाएं
    bill_image = Image.new("RGB", (600, img_height), "white")
    draw = ImageDraw.Draw(bill_image)
    
    # इमेज पर ब्लैक कलर से टेक्स्ट लिखें
    y = 20
    for line in lines:
        draw.text((20, y), line, fill="black")
        y += line_height
        
    # स्क्रीन पर बिल की फोटो डिस्प्ले करें
    st.image(bill_image, caption="Generated Bill Preview", use_container_width=True)
    
    # इमेज को डाउनलोड करने के लिए बाइट्स में बदलें
    buf = io.BytesIO()
    bill_image.save(buf, format="PNG")
    byte_im = buf.getvalue()
    
    # इमेज का नाम डेट और टाइम के साथ रखें
    file_name_str = f"Bill_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    
    # बिल को फोटो के रूप में डाउनलोड करने का बटन
    st.download_button(
        label="🖼️ Bill ko Photo me Download Karein",
        data=byte_im,
        file_name=file_name_str,
        mime="image/png"
    )

# ==========================================
# (REST OF THE MENUS REMAIN UNCHANGED)
# ==========================================

elif menu == '📊 Stock & Low Stock Alert':
  st.header('📊 Dukaan ka Current Stock')
  df_stock = st.session_state.inventory
  st.dataframe(df_stock, use_container_width=True)

elif menu == '➕ Naya Saaman Jodein':
  st.header('📦 Inventory Me Naya Product Jodein')
  with st.form('add_form'):
    p_name = st.text_input('Product Ka Naam')
    p_price = st.number_input('Price (₹ me)', min_value=1.0, format='%.2f')
    p_qty = st.number_input('Quantity', min_value=1, step=1)
    if st.form_submit_button('Save Karein') and p_name:
      new_row = pd.DataFrame({'Product Name': [p_name], 'Price (₹)': [p_price], 'Quantity': [p_qty]})
      st.session_state.inventory = pd.concat([st.session_state.inventory, new_row], ignore_index=True)
      st.session_state.inventory.to_csv(DATA_FILE, index=False)
      st.success(f"'{p_name}' jud gaya!")

elif menu == '✏️ Product Edit / Update':
  st.header('✏️ Product Ka Naam ya Price Badlein')
  df = st.session_state.inventory
  if not df.empty:
    selected_prod = st.selectbox('Product Chunein', df['Product Name'].tolist())
    current_price = float(df.loc[df['Product Name'] == selected_prod, 'Price (₹)'].iloc[0])
    with st.form('edit_form'):
      new_name = st.text_input('Naya Naam', value=selected_prod)
      new_price = st.number_input('Naya Price (₹)', value=current_price)
      if st.form_submit_button('Update Karein'):
        df.loc[df['Product Name'] == selected_prod, ['Product Name', 'Price (₹)']] = [new_name, new_price]
        df.to_csv(DATA_FILE, index=False)
        st.success('Update ho gaya!')
        st.rerun()

elif menu == '🗑️ Saaman Hatayein':
  st.header('🗑️ Stock Se Product Hatayein')
  df = st.session_state.inventory
  if not df.empty:
    del_product = st.selectbox('Product Chunein', df['Product Name'].tolist())
    if st.button('Delete Karein'):
      st.session_state.inventory = df[df['Product Name'] != del_product]
      st.session_state.inventory.to_csv(DATA_FILE, index=False)
      st.success('Delete ho gaya!')
      st.rerun()

elif menu == '📖 Udhaar Khata (Credit Book)':
  st.header('📖 Grahak ka Udhaar Khata')
  tab1, tab2 = st.tabs(['Naya Udhaar', 'Wasooli (Recovery)'])
  with tab1:
    with st.form('udhaar_form'):
      c_name = st.text_input('Grahak Ka Naam')
      c_phone = st.text_input('Mobile Number')
      c_amount = st.number_input('Udhaar (₹)', min_value=1.0)
      if st.form_submit_button('Udhaar Darj Karein') and c_name:
        new_row = pd.DataFrame([{'Date': datetime.datetime.now().strftime('%Y-%m-%d'), 'Customer Name': c_name, 'Phone Number': c_phone, 'Udhaar Amount (₹)': c_amount, 'Status': 'Pending'}])
        updated_udhaar = pd.concat([load_udhaar(), new_row], ignore_index=True)
        updated_udhaar.to_csv(UDHAAR_FILE, index=False)
        st.success('Udhaar save ho gaya!')
  with tab2:
    udhaar_df = load_udhaar()
    st.dataframe(udhaar_df)
    if not udhaar_df.empty:
      cust = st.selectbox('Kisko Paid mark karein?', udhaar_df['Customer Name'].tolist())
      if st.button('Udhaar Chukta (Paid)'):
        udhaar_df = udhaar_df[udhaar_df['Customer Name'] != cust]
        udhaar_df.to_csv(UDHAAR_FILE, index=False)
        st.success('Udhaar clear ho gaya!')
        st.rerun()

elif menu == '📈 Sales Report & Analytics':
  st.header('📈 Bikri (Sales) Ki Report')
  sales_data = load_sales()
  st.dataframe(sales_data, use_container_width=True)
  if not sales_data.empty:
    st.markdown(f"### 💰 Total Kamai: ₹ {sales_data['Total Price'].sum()}")

elif menu == '⚙️ Store & Profile Settings':
  st.header('⚙️ Dukaan ka Naam Update Karein')
  with st.form('config_form'):
    new_store_name = st.text_input('Dukaan Ka Naam', value=store_name)
    new_owner_name = st.text_input('Dukaan Malik Ka Naam', value=owner_name)
    if st.form_submit_button('Save Karein'):
      pd.DataFrame({'StoreName': [new_store_name], 'OwnerName': [new_owner_name]}).to_csv(CONFIG_FILE, index=False)
      st.success('Naam update ho gaya! App Refresh ho rahi hai...')
      st.rerun()
