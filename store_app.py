import datetime
import os
import pandas as pd
from PIL import Image
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title='Smart Kirana POS & Manager', page_icon='🛒', layout='wide'
)

# Files to save data permanently
DATA_FILE = 'dukan_stock.csv'
SALES_FILE = 'dukan_sales.csv'
UDHAAR_FILE = 'dukan_udhaar.csv'
CONFIG_FILE = 'dukan_config.csv'
STORE_LOGO_PATH = 'store_logo.png'
OWNER_PIC_PATH = 'owner_pic.png'


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
    /* Owner image ko circle banane ke liye CSS */
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
    </style>
""",
    unsafe_allow_html=True,
)

# --- SIDEBAR & DUAL PHOTOS SECTION ---
st.sidebar.title('🏪 Dukaan Control Panel')

# 1. Dukan ki Photo (Square shape)
if os.path.exists(STORE_LOGO_PATH):
  st.sidebar.image(
      STORE_LOGO_PATH, width=200, caption=f'🏪 {store_name} (Square Board)'
  )
else:
  st.sidebar.info('🖼️ Dukaan ka square logo upload nahi hai.')

st.sidebar.markdown('---')

# 2. Malik ki Photo (Circle shape)
if os.path.exists(OWNER_PIC_PATH):
  # Display using HTML/CSS for perfect circle crop
  st.sidebar.markdown(
      f"<h4 style='text-align: center; color: #31333F;'>👤 {owner_name}</h4>",
      unsafe_allow_html=True,
  )
  st.sidebar.image(OWNER_PIC_PATH, width=120, caption='Malik (Owner)')
else:
  st.sidebar.info("👤 Malik ki circle photo upload nahi hai.")

st.sidebar.markdown('---')

# Sidebar Navigation
menu = st.sidebar.selectbox(
    'Dukan Menu',
    [
        '🧾 Cart & Billing Counter',
        '📊 Stock & Low Stock Alert',
        '➕ Naya Saaman Jodein',
        '✏️ Product Edit / Update (Name & Price)',
        '🗑️ Saaman Hatayein (Delete)',
        '📖 Udhaar Khata (Credit Book)',
        '📈 Sales Report & Analytics',
        '⚙️ Store & Profile Photos Settings',
    ],
)

# App Header with dynamic store name
st.title(f'🛒 {store_name}')
st.caption(f'Sanchalak (Owner): {owner_name} | Smart Management & POS System')

# 1. BILLING & CART COUNTER
if menu == '🧾 Cart & Billing Counter':
  st.header('🧾 Grahak Ka Cart & Bill Banayein')

  df = st.session_state.inventory
  if df.empty:
    st.warning('Pehle stock me saman jodein!')
  else:
    col1, col2 = st.columns(2)

    with col1:
      st.subheader('Saaman Chunein')

      search_query = st.text_input(
          '🔍 Product Search Karein (Naam likhein)'
      ).lower()
      if search_query:
        filtered_list = df[
            df['Product Name'].str.lower().str.contains(search_query)
        ]['Product Name'].tolist()
      else:
        filtered_list = df['Product Name'].tolist()

      if not filtered_list:
        st.error('Aisa koi product nahi mila!')
      else:
        selected_product = st.selectbox(
            'Product Select Karein', filtered_list
        )

        prod_row = df.loc[df['Product Name'] == selected_product].iloc[0]
        available_qty = int(prod_row['Quantity'])
        price = float(prod_row['Price (₹)'])

        st.info(
            f'Available Stock: **{available_qty} units** | Price:'
            f' **₹{price}/unit**'
        )

        buy_qty = st.number_input(
            'Quantity', min_value=1, max_value=max(1, available_qty), step=1
        )

        if st.button('Cart Me Jodein'):
          if available_qty >= buy_qty:
            item_exists = False
            for item in st.session_state.cart:
              if item['Product'] == selected_product:
                item['Quantity'] += buy_qty
                item['Total'] = item['Quantity'] * price
                item_exists = True
                break

            if not item_exists:
              st.session_state.cart.append({
                  'Product': selected_product,
                  'Price': price,
                  'Quantity': buy_qty,
                  'Total': buy_qty * price,
              })
            st.success(f"'{selected_product}' cart me jud gaya!")
          else:
            st.error('Stock me itna saaman nahi hai!')

    with col2:
      st.subheader('🛒 Current Cart')
      if len(st.session_state.cart) > 0:
        cart_df = pd.DataFrame(st.session_state.cart)
        st.dataframe(cart_df, use_container_width=True)

        grand_total = cart_df['Total'].sum()
        st.markdown(f'### Grand Total: ₹ {grand_total}')

        if st.button('Bill Finalize Karein & Stock Update Karein'):
          current_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
          sales_records = []
          bill_text = f'🛒 *{store_name}* \n📅 Date: {current_date}\n------------------\n'

          for item in st.session_state.cart:
            p_name = item['Product']
            q_sold = item['Quantity']
            t_price = item['Total']

            st.session_state.inventory.loc[
                st.session_state.inventory['Product Name'] == p_name, 'Quantity'
            ] -= q_sold

            sales_records.append({
                'Date': current_date,
                'Product': p_name,
                'Quantity': q_sold,
                'Total Price': t_price,
            })
            bill_text += f'• {p_name} x {q_sold} = ₹{t_price}\n'

          bill_text += (
              f'------------------\n*TOTAL AMOUNT: ₹{grand_total}*\nDhanyawad'
              ' Phir Aayiyega! 🙏'
          )
          st.session_state.last_bill = bill_text

          st.session_state.inventory.to_csv(DATA_FILE, index=False)

          sales_df = load_sales()
          updated_sales = pd.concat(
              [sales_df, pd.DataFrame(sales_records)], ignore_index=True
          )
          updated_sales.to_csv(SALES_FILE, index=False)

          st.session_state.cart = []
          st.balloons()
          st.success('Bill ban gaya aur stock update ho gaya!')
          st.rerun()

        if st.button('Cart Khali Karein'):
          st.session_state.cart = []
          st.rerun()
      else:
        st.info('Cart khali hai.')

  if st.session_state.last_bill:
    st.markdown('---')
    st.subheader('📱 Aakhri Grahak ka WhatsApp Bill Message')
    st.text_area(
        'Yeh text copy karke customer ko WhatsApp par bhej sakte hain:',
        st.session_state.last_bill,
        height=150,
    )

# 2. STOCK & LOW STOCK ALERT VIEW
elif menu == '📊 Stock & Low Stock Alert':
  st.header('📊 Dukaan ka Current Stock & Assets')

  if st.button('Stock Refresh Karein'):
    st.session_state.inventory = load_data()

  df_stock = st.session_state.inventory

  if not df_stock.empty:
    df_stock['Total Value (₹)'] = df_stock['Price (₹)'] * df_stock['Quantity']
    total_inventory_worth = df_stock['Total Value (₹)'].sum()
    st.info(
        f'📦 **Dukaan ke kul stock ki keemat (Total Assets):**'
        f' **₹{total_inventory_worth}**'
    )

  low_stock_items = df_stock[df_stock['Quantity'] <= 5]
  if not low_stock_items.empty:
    st.warning(
        '⚠️ **Alert:** Neeche diye gaye items khatam hone wale hain, inka stock'
        ' jaldi bharein!'
    )
    st.dataframe(low_stock_items, use_container_width=True)

  st.subheader('Poora Stock Table')
  st.dataframe(df_stock, use_container_width=True)

# 3. NAYA SAAMAN ADD KARNA
elif menu == '➕ Naya Saaman Jodein':
  st.header('📦 Inventory Me Naya Product Jodein')

  with st.form('add_form'):
    p_name = st.text_input('Product Ka Naam (Jaise: Oil, Dal, Biscuit)')
    p_price = st.number_input('Price (₹ me)', min_value=1.0, format='%.2f')
    p_qty = st.number_input('Kitni Quantity/Packet hai?', min_value=1, step=1)
    submit = st.form_submit_button('Stock Me Save Karein')

    if submit and p_name:
      if p_name in st.session_state.inventory['Product Name'].values:
        st.error(
            'Ye product pehle se stock me hai! Uska price ya naam badalne ke'
            ' liye "Product Edit / Update" menu ka use karein.'
        )
      else:
        new_row = pd.DataFrame(
            {
                'Product Name': [p_name],
                'Price (₹)': [p_price],
                'Quantity': [p_qty],
            }
        )
        st.session_state.inventory = pd.concat(
            [st.session_state.inventory, new_row], ignore_index=True
        )
        st.session_state.inventory.to_csv(DATA_FILE, index=False)
        st.success(f"'{p_name}' dukan ke stock me jud gaya hai!")

# 4. EDIT / UPDATE PRODUCT NAME & PRICE
elif menu == '✏️ Product Edit / Update (Name & Price)':
  st.header('✏️ Product Ka Naam ya Price Badlein')
  df = st.session_state.inventory

  if df.empty:
    st.info('Stock me koi product nahi hai.')
  else:
    selected_prod = st.selectbox(
        'Jis product ko change karna hai use chunein', df['Product Name'].tolist()
    )

    current_row = df.loc[df['Product Name'] == selected_prod].iloc[0]
    current_price = float(current_row['Price (₹)'])

    with st.form('edit_form'):
      new_name = st.text_input('Naya Naam (Agar badalna ho)', value=selected_prod)
      new_price = st.number_input(
          'Naya Price (₹)',
          min_value=1.0,
          value=current_price,
          format='%.2f',
      )
      update_btn = st.form_submit_button('Changes Save Karein')

      if update_btn:
        st.session_state.inventory.loc[
            st.session_state.inventory['Product Name'] == selected_prod,
            'Product Name',
        ] = new_name
        st.session_state.inventory.loc[
            st.session_state.inventory['Product Name'] == new_name, 'Price (₹)'
        ] = new_price

        st.session_state.inventory.to_csv(DATA_FILE, index=False)
        st.success('Product details successfully update ho gayi hain!')
        st.rerun()

# 5. DELETE PRODUCT FROM INVENTORY
elif menu == '🗑️ Saaman Hatayein (Delete)':
  st.header('🗑️ Stock Se Product Hatayein')
  df = st.session_state.inventory
  if df.empty:
    st.info('Stock khali hai.')
  else:
    del_product = st.selectbox(
        'Hataney ke liye Product Chunein', df['Product Name'].tolist()
    )
    if st.button('Ye Product Delete Karein'):
      st.session_state.inventory = st.session_state.inventory[
          st.session_state.inventory['Product Name'] != del_product
      ]
      st.session_state.inventory.to_csv(DATA_FILE, index=False)
      st.success(f"'{del_product}' ko stock se hata diya gaya hai!")
      st.rerun()

# 6. UDHAAR KHATA (CREDIT BOOK)
elif menu == '📖 Udhaar Khata (Credit Book)':
  st.header('📖 Grahak ka Udhaar Khata (Credit Ledger)')

  tab1, tab2 = st.tabs(['Naya Udhaar Jodein', 'Udhaar List & Wasooli'])

  with tab1:
    with st.form('udhaar_form'):
      c_name = st.text_input('Grahak Ka Naam')
      c_phone = st.text_input('Mobile Number')
      c_amount = st.number_input(
          'Kitna Paisa Udhaar hai? (₹)', min_value=1.0, format='%.2f'
      )
      submit_udhaar = st.form_submit_button('Udhaar Darj Karein')

      if submit_udhaar and c_name:
        current_date = datetime.datetime.now().strftime('%Y-%m-%d')
        new_udhaar_row = pd.DataFrame({
            'Date': [current_date],
            'Customer Name': [c_name],
            'Phone Number': [c_phone],
            'Udhaar Amount (₹)': [c_amount],
            'Status': ['Pending'],
        })

        udhaar_df = load_udhaar()
        updated_udhaar = pd.concat(
            [udhaar_df, new_udhaar_row], ignore_index=True
        )
        updated_udhaar.to_csv(UDHAAR_FILE, index=False)
        st.success(
            f"'{c_name}' ka ₹{c_amount} ka udhaar successfully save ho gaya hai!"
        )

  with tab2:
    st.subheader('Saare Pending Udhaar')
    udhaar_df = load_udhaar()
    if udhaar_df.empty:
      st.info('Koi udhaar record nahi hai.')
    else:
      st.dataframe(udhaar_df, use_container_width=True)
      total_udhaar = udhaar_df[udhaar_df['Status'] == 'Pending'][
          'Udhaar Amount (₹)'
      ].sum()
      st.warning(f'⚠️ **Kul Baaki Udhaar Market Me:** ₹ {total_udhaar}')

      selected_cust = st.selectbox(
          'Jis grahak ne paisa de diya uska naam chunein',
          udhaar_df['Customer Name'].tolist(),
      )
      if st.button('Udhaar Chukta / Paid Karein'):
        udhaar_df = udhaar_df[udhaar_df['Customer Name'] != selected_cust]
        udhaar_df.to_csv(UDHAAR_FILE, index=False)
        st.success(
            f"'{selected_cust}' ka udhaar chukta ho gaya aur list se hata"
            ' diya gaya!'
        )
        st.rerun()

# 7. SALES REPORT & ANALYTICS
elif menu == '📈 Sales Report & Analytics':
  st.header('📈 Bikri (Sales) Ki Report & Analytics')
  sales_data = load_sales()
  if sales_data.empty:
    st.info('Abhi tak koi bikri nahi hui hai.')
  else:
    st.dataframe(sales_data, use_container_width=True)
    total_revenue = sales_data['Total Price'].sum()
    st.markdown(f'### 💰 Total Kamai (Revenue): ₹ {total_revenue}')

# 8. STORE SETTINGS & PROFILE PHOTOS SETTINGS
elif menu == '⚙️ Store & Profile Photos Settings':
  st.header('⚙️ Dukaan ka Naam aur Dono Photos Upload Karein')

  with st.form('config_form'):
    new_store_name = st.text_input('Dukaan Ka Naam', value=store_name)
    new_owner_name = st.text_input('Dukaan Malik Ka Naam', value=owner_name)
    save_config_btn = st.form_submit_button('Naam Save Karein')

    if save_config_btn:
      cfg_df = pd.DataFrame(
          {'StoreName': [new_store_name], 'OwnerName': [new_owner_name]}
      )
      cfg_df.to_csv(CONFIG_FILE, index=False)
      st.success('Dukaan ka naam update ho gaya!')
      st.rerun()

  st.markdown('---')
  col_s1, col_s2 = st.columns(2)

  with col_s1:
    st.subheader('🏪 1. Dukaan ka Square Logo')
    store_file = st.file_uploader(
        'Square Board/Shop Photo Upload Karein',
        type=['jpg', 'jpeg', 'png'],
        key='store_up',
    )
    if store_file is not None:
      img_store = Image.open(store_file)
      img_store.save(STORE_LOGO_PATH)
      st.success('Dukaan ka square logo save ho gaya!')
      st.image(STORE_LOGO_PATH, width=150)
      st.rerun()

  with col_s2:
    st.subheader('👤 2. Malik ki Circle Photo')
    owner_file = st.file_uploader(
        'Malik ki Face Photo Upload Karein',
        type=['jpg', 'jpeg', 'png'],
        key='owner_up',
    )
    if owner_file is not None:
      img_owner = Image.open(owner_file)
      img_owner.save(OWNER_PIC_PATH)
      st.success('Malik ki circle photo save ho gayi!')
      st.image(OWNER_PIC_PATH, width=120)
      st.rerun()