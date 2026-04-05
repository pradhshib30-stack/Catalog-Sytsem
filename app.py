# ============================================================
# OptiCatalog — Automation in Catalogue Quality Validation
# Developed for Outzidr D2C Fashion E-Commerce
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
import pickle
import io
from datetime import datetime

# ============================================================
# PAGE CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="OptiCatalog",
    page_icon="🗂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CUSTOM CSS STYLING — Sage & White Theme
# ============================================================
st.markdown("""
    <style>
    .main { background-color: #FFFFFF; }
    [data-testid="stSidebar"] {
        background-color: #F5F7F5;
        border-right: 1px solid #DCE8E4;
    }
    .app-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #4A7C6F;
        text-align: center;
        padding: 1rem 0;
        letter-spacing: 2px;
    }
    .app-subtitle {
        font-size: 1rem;
        color: #888888;
        text-align: center;
        margin-bottom: 2rem;
        letter-spacing: 1px;
    }
    .section-header {
        font-size: 1.3rem;
        font-weight: 600;
        color: #4A7C6F;
        border-bottom: 2px solid #DCE8E4;
        padding-bottom: 0.5rem;
        margin-bottom: 1rem;
    }
    .card {
        background-color: #F5F7F5;
        border: 1px solid #DCE8E4;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    .success-msg {
        background-color: #E8F5F2;
        border-left: 4px solid #6BAE9A;
        border-radius: 5px;
        padding: 1rem;
        color: #2D2D2D;
        margin-bottom: 1rem;
    }
    .warning-msg {
        background-color: #FDF6EC;
        border-left: 4px solid #E8B86D;
        border-radius: 5px;
        padding: 1rem;
        color: #2D2D2D;
        margin-bottom: 1rem;
    }
    .error-msg {
        background-color: #FCF0F2;
        border-left: 4px solid #D97A8A;
        border-radius: 5px;
        padding: 1rem;
        color: #2D2D2D;
        margin-bottom: 1rem;
    }
    .info-box {
        background-color: #F5F7F5;
        border: 1px solid #DCE8E4;
        border-radius: 8px;
        padding: 1rem;
        color: #2D2D2D;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #F5F7F5;
        border: 1px solid #DCE8E4;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #4A7C6F;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #888888;
    }
    .stButton > button {
        background-color: #4A7C6F;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-size: 1rem;
        font-weight: 500;
        width: 100%;
    }
    .stButton > button:hover {
        background-color: #3D6B5F;
        color: white;
    }
    hr { border: none; border-top: 1px solid #DCE8E4; margin: 1.5rem 0; }
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# ============================================================
# MASTER REFERENCE DATA
# ============================================================
VALID_CONSTRUCTION = ['woven', 'knit']
VALID_STRETCH = ['low', 'medium', 'high']
VALID_L1 = ['clothing']
VALID_L2 = ['bottom wear', 'top wear', 'co-ord sets', 'outer wear', 'dresses & jumpsuits']
VALID_OCCASIONS = ['casual wear', 'street wear', 'vacay wear', 'formal wear', 'party wear']
VALID_FIT = ['a-line', 'baggy fit', 'bodycon', 'boxy fit', 'fit & flare', 'flared',
             'oversized', 'regular', 'relaxed', 'skinny', 'straight', 'tapered',
             'wide leg', 'skater', 'sheath', 'shift', 'fitted', 'pencil fit', 'peplum']
VALID_INVENTORY = ['hc', 'normal']
VALID_SEASON = ['all round', 'summer', 'winter']

L2_L3_MAPPING = {
    'top wear': ['t-shirt', 'knit tops', 'tanks', 'shirts', 'blouses', 'bodysuits', 'camisoles'],
    'dresses & jumpsuits': ['mini', 'midi', 'maxi', 'knee', 'jumpsuits', 'playsuits/rompers'],
    'bottom wear': ['jeans', 'trousers', 'joggers & sweatpants', 'leggings', 'shorts', 'skirts'],
    'co-ord sets': ['knit co-ords', 'woven co-ords'],
    'outer wear': ['sweaters & cardigans', 'sweatshirts & hoodies', 'jackets', 'coats', 'blazers', 'shrug', 'vest']
}

VALID_APPAREL_SIZES = ['xs', 's', 'm', 'l', 'xl', 'xxl', '3xl', '4xl']
VALID_BOTTOM_SIZES = ['26', '28', '30', '32', '34', '36']

VALID_COLOURS = [
    'black', 'white', 'red', 'blue', 'green', 'yellow', 'orange', 'purple',
    'pink', 'brown', 'magenta', 'mauve', 'navy blue', 'grey', 'beige', 'maroon',
    'peach', 'off white', 'olive', 'multi', 'mustard', 'lavender', 'cream',
    'teal', 'burgundy', 'rust', 'sea green', 'turquoise', 'charcoal', 'khaki',
    'coral', 'gold', 'silver', 'copper', 'bronze', 'nude', 'transparent',
    'metallic', 'lime', 'rose gold', 'ivory', 'dark green', 'wine', 'aqua',
    'fuchsia', 'light blue', 'light green', 'lilac', 'taupe', 'tan', 'mint',
    'champagne', 'light pink', 'royal blue', 'coffee'
]

COLOUR_CODES = {
    'Black': '10', 'White': '11', 'Red': '12', 'Blue': '13', 'Green': '14',
    'Yellow': '15', 'Orange': '16', 'Purple': '17', 'Pink': '18', 'Brown': '19',
    'Magenta': '20', 'Mauve': '21', 'Navy Blue': '22', 'Grey': '23', 'Beige': '24',
    'Maroon': '25', 'Peach': '26', 'Off White': '27', 'Olive': '28', 'Multi': '29',
    'Mustard': '30', 'Lavender': '31', 'Cream': '32', 'Teal': '33', 'Burgundy': '34',
    'Rust': '35', 'Sea Green': '36', 'Turquoise': '37', 'Charcoal': '38', 'Khaki': '39',
    'Coral': '40', 'Gold': '41', 'Silver': '42', 'Copper': '43', 'Bronze': '44',
    'Nude': '46', 'Transparent': '47', 'Metallic': '48', 'Lime': '49', 'Rose Gold': '50',
    'Ivory': '51', 'Dark Green': '52', 'Wine': '53', 'Aqua': '55', 'Fuchsia': '56',
    'Light Blue': '57', 'Light Green': '58', 'Lilac': '59', 'Taupe': '60', 'Tan': '61',
    'Mint': '62', 'Champagne': '63', 'Light Pink': '64', 'Royal Blue': '65', 'Coffee': '66'
}

SIZE_CODES = {
    'XXS': '01', 'XS': '02', 'S': '03', 'M': '04', 'L': '05',
    'XL': '06', 'XXL': '07', '3XL': '08', '4XL': '09', '5XL': '10',
    '26': '26', '28': '28', '30': '30', '32': '32', '34': '34',
    '36': '36', '37': '37', '38': '38', '39': '39', '40': '40',
    'One Size': '99'
}

PRODUCT_TYPE_CODES = {
    'T-Shirt': 'TS', 'Knit Tops': 'KT', 'Tanks': 'TK', 'Shirts': 'ST',
    'Blouses': 'BL', 'Bodysuits': 'BD', 'Camisoles': 'CM', 'Mini': 'MN',
    'Midi': 'MD', 'Maxi': 'MX', 'Knee': 'KN', 'Jumpsuits': 'JS',
    'Playsuits/Rompers': 'PS', 'Jeans': 'JN', 'Trousers': 'TR',
    'Joggers & Sweatpants': 'JG', 'Leggings': 'LG', 'Shorts': 'SH',
    'Skirts': 'SK', 'Knit Co-Ords': 'KC', 'Woven Co-Ords': 'WC',
    'Sweaters & Cardigans': 'SW', 'Sweatshirts & Hoodies': 'HS',
    'Jackets': 'JK', 'Coats': 'CT', 'Blazers': 'BZ', 'Shrug': 'SG', 'Vest': 'VT'
}

MONTH_CODES = {
    'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
    'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
    'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
}

# ============================================================
# COLUMN NAME STANDARDIZATION
# ============================================================
COLUMN_MAP = {
    'supplier name': 'Supplier Name',
    'style id': 'Style Id',
    'style id 1': 'Style Id 1',
    'style id.1': 'Style Id 1',
    'supplier option id': 'Supplier Option ID',
    'supplier sku code': 'Supplier SKU code',
    'supplier colour': 'Supplier Colour',
    'china buy price': 'China Buy Price',
    'product weight': 'Product Weight',
    'construction technique': 'Construction Technique',
    'stretch': 'Stretch',
    'material / fabric composition': 'Material / Fabric Composition',
    'supplier available sizes': 'Supplier Available Sizes',
    'product id': 'Product ID',
    'product name': 'Product Name',
    'image link': 'Image link',
    'inati colour': 'Inati Colour',
    'l1': 'L1',
    'l2': 'L2',
    'l3': 'L3',
    'inati sizes': 'Inati Sizes',
    'mrp': 'MRP',
    'primary occasion': 'Primary Occasion',
    'secondary occasion': 'Secondary Occasion',
    'product launch month': 'Product Launch Month',
    'launch year': 'Launch year',
    'fit': 'Fit',
    'inventory': 'Inventory',
    'season': 'SEASON'
}

def standardize_columns(df):
    # Standardize column names - case insensitive
    new_columns = {}
    for col in df.columns:
        col_lower = col.strip().lower()
        if col_lower in COLUMN_MAP:
            new_columns[col] = COLUMN_MAP[col_lower]
        else:
            new_columns[col] = col
    df = df.rename(columns=new_columns)
    return df

def standardize_vendor_file(df):
    # First standardize column names
    df = standardize_columns(df)

    # Standardize all text values - case insensitive
    text_cols = [
        'Supplier Name', 'Supplier Colour', 'Construction Technique',
        'Stretch', 'Product Name', 'Inati Colour', 'L1', 'L2', 'L3',
        'Inati Sizes', 'Primary Occasion', 'Secondary Occasion',
        'Product Launch Month', 'Fit', 'SEASON'
    ]
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.title()

    # Special handling for Inventory
    def fix_inventory(val):
        val = str(val).strip().lower()
        if val == 'hc':
            return 'HC'
        else:
            return 'Normal'

    if 'Inventory' in df.columns:
        df['Inventory'] = df['Inventory'].apply(fix_inventory)

    return df

# ============================================================
# VALIDATION FUNCTION
# ============================================================
def validate_vendor_file(df):
    warnings_list = []

    for idx, row in df.iterrows():
        row_num = idx + 2

        # Get values and convert to lowercase for comparison
        construction = str(row.get('Construction Technique', '')).strip().lower()
        stretch = str(row.get('Stretch', '')).strip().lower()

        # Rule 1: Construction vs Stretch swap
        if construction in VALID_STRETCH:
            warnings_list.append({'Row': row_num, 'Column': 'Construction Technique',
                'Warning': f"Incorrect attribute! Stretch value '{construction}' found in Construction Technique column.",
                'Suggestion': "Move this value to the Stretch column and fill Construction Technique with 'Woven' or 'Knit'."})

        if stretch in VALID_CONSTRUCTION:
            warnings_list.append({'Row': row_num, 'Column': 'Stretch',
                'Warning': f"Incorrect attribute! Construction value '{stretch}' found in Stretch column.",
                'Suggestion': "Move this value to the Construction Technique column and fill Stretch with 'Low', 'Medium', or 'High'."})

        # Rule 2: Invalid Construction value
        if construction not in VALID_CONSTRUCTION and construction not in VALID_STRETCH:
            warnings_list.append({'Row': row_num, 'Column': 'Construction Technique',
                'Warning': f"Invalid Construction Technique value '{construction}'.",
                'Suggestion': "Valid values are: Woven, Knit."})

        # Rule 3: Invalid Stretch value
        if stretch not in VALID_STRETCH and stretch not in VALID_CONSTRUCTION:
            warnings_list.append({'Row': row_num, 'Column': 'Stretch',
                'Warning': f"Invalid Stretch value '{stretch}'.",
                'Suggestion': "Valid values are: Low, Medium, High."})

        # Rule 4: Missing MRP
        mrp = row.get('MRP', None)
        if pd.isnull(mrp) or str(mrp).strip() == '':
            warnings_list.append({'Row': row_num, 'Column': 'MRP',
                'Warning': "MRP column is empty.",
                'Suggestion': "Fill in the correct MRP value."})

        # Rule 5: L1 Check
        l1 = str(row.get('L1', '')).strip().lower()
        if l1 not in VALID_L1:
            warnings_list.append({'Row': row_num, 'Column': 'L1',
                'Warning': f"Invalid L1 value '{l1}'.",
                'Suggestion': "L1 must always be 'Clothing'."})

        # Rule 6: L2 Check
        l2 = str(row.get('L2', '')).strip().lower()
        if l2 not in VALID_L2:
            warnings_list.append({'Row': row_num, 'Column': 'L2',
                'Warning': f"Invalid L2 value '{l2}'.",
                'Suggestion': f"Valid L2 values are: {', '.join([v.title() for v in VALID_L2])}."})

        # Rule 7: L3 not valid for L2
        l3 = str(row.get('L3', '')).strip().lower()
        if l2 in L2_L3_MAPPING:
            if l3 not in L2_L3_MAPPING[l2]:
                warnings_list.append({'Row': row_num, 'Column': 'L3',
                    'Warning': f"L3 '{l3}' is not valid for L2 '{l2}'.",
                    'Suggestion': f"Change L3 to one of: {', '.join([v.title() for v in L2_L3_MAPPING[l2]])} or refer to the product image."})

        # Rule 8: Primary Occasion
        occasion = str(row.get('Primary Occasion', '')).strip().lower()
        if occasion not in VALID_OCCASIONS:
            warnings_list.append({'Row': row_num, 'Column': 'Primary Occasion',
                'Warning': f"Invalid Primary Occasion value '{occasion}'.",
                'Suggestion': f"Valid values are: {', '.join([v.title() for v in VALID_OCCASIONS])}."})

        # Rule 9: Fit vs Inventory swap
        fit = str(row.get('Fit', '')).strip().lower()
        inventory = str(row.get('Inventory', '')).strip().lower()

        if fit in VALID_INVENTORY:
            warnings_list.append({'Row': row_num, 'Column': 'Fit',
                'Warning': f"Incorrect attribute! Inventory value '{fit}' found in Fit column.",
                'Suggestion': "Move this value to the Inventory column and fill Fit with a valid fit type."})

        if inventory in VALID_FIT:
            warnings_list.append({'Row': row_num, 'Column': 'Inventory',
                'Warning': f"Incorrect attribute! Fit value '{inventory}' found in Inventory column.",
                'Suggestion': "Move this value to the Fit column and fill Inventory with 'HC' or 'Normal'."})

        # Rule 10: Invalid Fit
        if fit not in VALID_FIT and fit not in VALID_INVENTORY:
            warnings_list.append({'Row': row_num, 'Column': 'Fit',
                'Warning': f"Invalid Fit value '{fit}'.",
                'Suggestion': f"Valid values are: {', '.join([v.title() for v in VALID_FIT])}."})

        # Rule 11: Invalid Inventory
        if inventory not in VALID_INVENTORY and inventory not in VALID_FIT:
            warnings_list.append({'Row': row_num, 'Column': 'Inventory',
                'Warning': f"Invalid Inventory value '{inventory}'.",
                'Suggestion': "Valid values are: 'HC' or 'Normal'."})

        # Rule 12: Season Check
        season = str(row.get('SEASON', '')).strip().lower()
        if season not in VALID_SEASON:
            warnings_list.append({'Row': row_num, 'Column': 'SEASON',
                'Warning': f"Invalid Season value '{season}'.",
                'Suggestion': f"Valid values are: {', '.join([v.title() for v in VALID_SEASON])}."})

        # Rule 13: Inati Colour
        colour = str(row.get('Inati Colour', '')).strip().lower()
        if colour not in VALID_COLOURS:
            warnings_list.append({'Row': row_num, 'Column': 'Inati Colour',
                'Warning': f"Colour '{colour}' is not in the approved Inati colour list.",
                'Suggestion': "Please use an approved Inati colour from the master list."})

        # Rule 14: Inati Sizes
        size = str(row.get('Inati Sizes', '')).strip().lower()
        if l2 == 'bottom wear':
            if size not in VALID_BOTTOM_SIZES:
                warnings_list.append({'Row': row_num, 'Column': 'Inati Sizes',
                    'Warning': f"Size '{size}' is not valid for Bottom Wear.",
                    'Suggestion': f"Valid Bottom Wear sizes are: {', '.join(VALID_BOTTOM_SIZES)}."})
        else:
            if size not in VALID_APPAREL_SIZES:
                warnings_list.append({'Row': row_num, 'Column': 'Inati Sizes',
                    'Warning': f"Invalid size '{size}' for {l2}.",
                    'Suggestion': f"Valid sizes are: {', '.join([v.upper() for v in VALID_APPAREL_SIZES])}."})

    # Rule 15: Colour inconsistency within variant
    for option_id, group in df.groupby('Supplier Option ID'):
        colours = group['Inati Colour'].str.lower().unique()
        if len(colours) > 1:
            for idx in group.index:
                warnings_list.append({'Row': idx + 2, 'Column': 'Inati Colour',
                    'Warning': f"Colour inconsistency for variant '{option_id}'. Multiple colours found.",
                    'Suggestion': "All rows for the same variant should have the same Inati Colour."})

    # Rule 16: Size issues
    for option_id, group in df.groupby('Supplier Option ID'):
        sizes = list(group['Inati Sizes'].str.lower())
        seen = []
        duplicates = []
        for s in sizes:
            if s in seen:
                duplicates.append(s)
            else:
                seen.append(s)

        if duplicates:
            for idx in group.index:
                warnings_list.append({'Row': idx + 2, 'Column': 'Inati Sizes',
                    'Warning': f"Duplicate size(s) found for variant '{option_id}'.",
                    'Suggestion': "Remove duplicate size entries."})

        if len(sizes) == 1 and sizes[0] != 'one size':
            for idx in group.index:
                warnings_list.append({'Row': idx + 2, 'Column': 'Inati Sizes',
                    'Warning': f"Only one size found for variant '{option_id}'.",
                    'Suggestion': "Check and provide all missing sizes."})

        if 'one size' in sizes:
            for idx in group.index:
                warnings_list.append({'Row': idx + 2, 'Column': 'Inati Sizes',
                    'Warning': f"'One Size' mentioned for variant '{option_id}'.",
                    'Suggestion': "Verify if truly One Size or provide individual sizes."})

    # Rule 17: MRP inconsistency
    for option_id, group in df.groupby('Supplier Option ID'):
        mrp_values = group['MRP'].dropna().unique()
        if len(mrp_values) > 1:
            for idx in group.index:
                warnings_list.append({'Row': idx + 2, 'Column': 'MRP',
                    'Warning': f"MRP inconsistency for variant '{option_id}'.",
                    'Suggestion': "MRP should be same for all sizes of the same variant."})

    # Rule 18: Style ID inconsistency
    if 'Style Id 1' in df.columns and 'Style Id' in df.columns:
        for style_id, group in df.groupby('Style Id 1'):
            style_ids = group['Style Id'].unique()
            if len(style_ids) > 1:
                for idx in group.index:
                    warnings_list.append({'Row': idx + 2, 'Column': 'Style Id',
                        'Warning': f"Style ID inconsistency across colour variants.",
                        'Suggestion': "Style ID should be same for all colour variants."})

    return warnings_list

# ============================================================
# OPTION LEVEL CONVERSION
# ============================================================
def convert_to_option_level(df):
    option_level_data = []
    for option_id, group in df.groupby('Supplier Option ID'):
        def get_val(col):
            return group[col].iloc[0] if col in group.columns else ''
        
        option_data = {
            'Supplier Option ID': option_id,
            'Supplier Name': get_val('Supplier Name'),
            'Style Id': get_val('Style Id'),
            'Style Id 1': get_val('Style Id 1'),
            'Product Name': get_val('Product Name'),
            'Inati Colour': get_val('Inati Colour'),
            'L1': get_val('L1'),
            'L2': get_val('L2'),
            'L3': get_val('L3'),
            'MRP': get_val('MRP'),
            'Construction Technique': get_val('Construction Technique'),
            'Stretch': get_val('Stretch'),
            'Fit': get_val('Fit'),
            'Primary Occasion': get_val('Primary Occasion'),
            'Secondary Occasion': get_val('Secondary Occasion'),
            'Inventory': get_val('Inventory'),
            'SEASON': get_val('SEASON'),
            'Product Launch Month': get_val('Product Launch Month'),
            'Product ID': get_val('Product ID'),
            'Size Count': group['Inati Sizes'].nunique() if 'Inati Sizes' in group.columns else 0,
            'Sizes Available': ', '.join(group['Inati Sizes'].astype(str).tolist()) if 'Inati Sizes' in group.columns else '',
        }
        option_level_data.append(option_data)
    return pd.DataFrame(option_level_data)

# ============================================================
# ID GENERATION
# ============================================================
def generate_ids(df):
    sku_ids = []
    option_ids = []
    for idx, row in df.iterrows():
        gender = 'W'
        l3 = str(row.get('L3', '')).strip().title()
        type_code = PRODUCT_TYPE_CODES.get(l3, 'XX')
        style_id = str(row.get('Style Id 1', '')).strip()
        style_id = style_id.zfill(6)[:6]
        launch_month = str(row.get('Product Launch Month', '')).strip().title()
        month_code = MONTH_CODES.get(launch_month, '00')
        launch_year = str(row.get('Launch year', '')).strip()
        if launch_year == 'nan' or launch_year == '':
            launch_year = str(datetime.now().year)[-2:]
        else:
            launch_year = str(int(float(launch_year)))[-2:]
        colour = str(row.get('Inati Colour', '')).strip().title()
        colour_code = COLOUR_CODES.get(colour, '00')
        size = str(row.get('Inati Sizes', '')).strip().upper()
        size_code = SIZE_CODES.get(size, '00')
        option_id = f"{gender}{type_code}{style_id}{month_code}{launch_year}{colour_code}"
        sku_id = f"{option_id}{size_code}"
        option_ids.append(option_id)
        sku_ids.append(sku_id)
    return option_ids, sku_ids

# ============================================================
# ML MODEL FUNCTIONS
# ============================================================
def load_model():
    with open('risk_model.pkl', 'rb') as f:
        model = pickle.load(f)
    with open('le_vendor.pkl', 'rb') as f:
        le_vendor = pickle.load(f)
    with open('le_colour.pkl', 'rb') as f:
        le_colour = pickle.load(f)
    with open('le_product.pkl', 'rb') as f:
        le_product = pickle.load(f)
    with open('le_price.pkl', 'rb') as f:
        le_price = pickle.load(f)
    return model, le_vendor, le_colour, le_product, le_price

def price_range_encode(mrp):
    if mrp <= 799:
        return 'Budget'
    elif mrp <= 1499:
        return 'Mid'
    else:
        return 'Premium'

def safe_encode(le, value):
    value = str(value).strip().title()
    if value in le.classes_:
        return le.transform([value])[0]
    else:
        return -1

def predict_risk(df_option, image_counts, model, le_vendor, le_colour, le_product, le_price):
    predictions = []
    for _, row in df_option.iterrows():
        option_id = row['Supplier Option ID']
        vendor = str(row['Supplier Name']).strip().title()
        colour = str(row['Inati Colour']).strip().title()
        product = str(row['L3']).strip().title()
        mrp = row['MRP']
        size_count = row['Size Count']
        image_count = image_counts.get(option_id, 1)
        price_range = price_range_encode(mrp)
        vendor_enc = safe_encode(le_vendor, vendor)
        colour_enc = safe_encode(le_colour, colour)
        product_enc = safe_encode(le_product, product)
        price_enc = safe_encode(le_price, price_range)
        feature_row = [[size_count, image_count, vendor_enc, colour_enc, product_enc, mrp, price_enc]]
        risk_label = model.predict(feature_row)[0]
        risk_level = risk_label + 1
        risk_map = {1: '🟢 Low Risk', 2: '🟡 Medium Risk', 3: '🔴 High Risk'}
        risk_text = risk_map[risk_level]
        predictions.append({
            'Supplier Option ID': option_id,
            'Product Name': row['Product Name'],
            'Risk Level': risk_level,
            'Risk Label': risk_text
        })
    return pd.DataFrame(predictions)

# ============================================================
# SESSION STATE
# ============================================================
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'df_vendor' not in st.session_state:
    st.session_state.df_vendor = None
if 'df_option_level' not in st.session_state:
    st.session_state.df_option_level = None
if 'df_corrected' not in st.session_state:
    st.session_state.df_corrected = None
if 'warnings_output' not in st.session_state:
    st.session_state.warnings_output = []
if 'risk_predictions' not in st.session_state:
    st.session_state.risk_predictions = None
if 'run_ml' not in st.session_state:
    st.session_state.run_ml = False

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("""
        <div style='text-align:center; padding: 1rem 0;'>
            <h1 style='color:#4A7C6F; font-size:1.8rem; font-weight:700; letter-spacing:2px;'>
                🗂️ OptiCatalog
            </h1>
            <p style='color:#888888; font-size:0.8rem;'>
                Automation in Catalogue Quality Validation
            </p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    steps = {
        1: "📂 Upload Vendor File",
        2: "🔍 Validation Report",
        3: "📦 Option Level View",
        4: "🤖 Risk Prediction",
        5: "📁 Re-upload Corrected File",
        6: "🆔 ID Generation & Output"
    }

    st.markdown("**Progress:**")
    for step_num, step_name in steps.items():
        if step_num == st.session_state.step:
            st.markdown(f"<div style='background:#4A7C6F; color:white; padding:0.5rem; border-radius:5px; margin:0.2rem 0;'>→ {step_name}</div>", unsafe_allow_html=True)
        elif step_num < st.session_state.step:
            st.markdown(f"<div style='color:#6BAE9A; padding:0.5rem; margin:0.2rem 0;'>✅ {step_name}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='color:#888888; padding:0.5rem; margin:0.2rem 0;'>○ {step_name}</div>", unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<p style='color:#888888; font-size:0.75rem; text-align:center;'>Developed for Outzidr<br>© 2026 OptiCatalog</p>", unsafe_allow_html=True)

# ============================================================
# MAIN CONTENT
# ============================================================
st.markdown("<div class='app-title'>🗂️ OptiCatalog</div>", unsafe_allow_html=True)
st.markdown("<div class='app-subtitle'>Automation in Catalogue Quality Validation Process</div>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

# ============================================================
# STEP 1 — UPLOAD VENDOR FILE
# ============================================================
if st.session_state.step == 1:
    st.markdown("<div class='section-header'>📂 Step 1 — Upload Vendor File</div>", unsafe_allow_html=True)

    st.markdown("""
        <div class='info-box'>
            <b>Instructions:</b><br>
            • Upload the raw vendor file received from your China-based vendor<br>
            • Accepted format: <b>.xlsx</b> (Excel file)<br>
            • The system will automatically validate the file for cataloguing errors
        </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Choose your vendor file", type=['xlsx'])

    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)
        df = standardize_vendor_file(df)
        st.session_state.df_vendor = df

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"<div class='metric-card'><div class='metric-value'>{len(df)}</div><div class='metric-label'>Total SKUs</div></div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div class='metric-card'><div class='metric-value'>{df['Supplier Option ID'].nunique()}</div><div class='metric-label'>Total Products</div></div>", unsafe_allow_html=True)
        with col3:
            st.markdown(f"<div class='metric-card'><div class='metric-value'>{len(df.columns)}</div><div class='metric-label'>Total Columns</div></div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<div class='success-msg'>✅ File uploaded successfully! Click below to run validation.</div>", unsafe_allow_html=True)

        if st.button("Run Validation →"):
            st.session_state.warnings_output = validate_vendor_file(df)
            st.session_state.df_option_level = convert_to_option_level(df)
            st.session_state.step = 2
            st.rerun()

# ============================================================
# STEP 2 — VALIDATION REPORT
# ============================================================
elif st.session_state.step == 2:
    st.markdown("<div class='section-header'>🔍 Step 2 — Validation Report</div>", unsafe_allow_html=True)

    warnings = st.session_state.warnings_output

    if len(warnings) == 0:
        st.markdown("<div class='success-msg'>✅ No issues found! Your vendor file is clean and ready to proceed.</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='warning-msg'>⚠️ <b>{len(warnings)} issue(s) found</b> in your vendor file. Please review and correct them before proceeding.</div>", unsafe_allow_html=True)

        df_warnings = pd.DataFrame(warnings)

        st.markdown("**Issues by Column:**")
        col_summary = df_warnings['Column'].value_counts().reset_index()
        col_summary.columns = ['Column', 'Issue Count']
        st.dataframe(col_summary, use_container_width=True, hide_index=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**Detailed Warnings & Suggestions:**")
        st.dataframe(df_warnings, use_container_width=True, hide_index=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Proceed to Option Level View →"):
        st.session_state.step = 3
        st.rerun()

# ============================================================
# STEP 3 — OPTION LEVEL VIEW
# ============================================================
elif st.session_state.step == 3:
    st.markdown("<div class='section-header'>📦 Step 3 — Option Level Summary</div>", unsafe_allow_html=True)

    df_option = st.session_state.df_option_level
    st.markdown(f"<div class='info-box'>Total unique products at option level: <b>{len(df_option)}</b></div>", unsafe_allow_html=True)
    st.dataframe(df_option, use_container_width=True, hide_index=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Proceed to Risk Prediction →"):
        st.session_state.step = 4
        st.rerun()

# ============================================================
# STEP 4 — ML RISK PREDICTION (OPTIONAL)
# ============================================================
elif st.session_state.step == 4:
    st.markdown("<div class='section-header'>🤖 Step 4 — Risk Prediction (Optional)</div>", unsafe_allow_html=True)

    st.markdown("""
        <div class='info-box'>
            <b>ML Risk Prediction</b> predicts the likelihood of a product being returned.<br><br>
            • 🟢 <b>Low Risk</b> — Return rate less than 15%<br>
            • 🟡 <b>Medium Risk</b> — Return rate between 15% and 25%<br>
            • 🔴 <b>High Risk</b> — Return rate 26% and above
        </div>
    """, unsafe_allow_html=True)

    run_ml = st.radio("Do you want to run Risk Prediction?", ["No", "Yes"])

    if run_ml == "Yes":
        st.session_state.run_ml = True
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**Please enter Image Count for each product:**")

        df_option = st.session_state.df_option_level
        image_counts = {}

        for _, row in df_option.iterrows():
            option_id = row['Supplier Option ID']
            product_name = row['Product Name']
            count = st.number_input(
                f"{product_name} ({option_id})",
                min_value=1, max_value=20, value=1,
                key=f"img_{option_id}"
            )
            image_counts[option_id] = count

        if st.button("Run Risk Prediction →"):
            model, le_vendor, le_colour, le_product, le_price = load_model()
            df_predictions = predict_risk(
                df_option, image_counts, model,
                le_vendor, le_colour, le_product, le_price
            )
            st.session_state.risk_predictions = df_predictions
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("**📊 Risk Prediction Results:**")
            st.dataframe(df_predictions, use_container_width=True, hide_index=True)

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Proceed to Re-upload →"):
                st.session_state.step = 5
                st.rerun()
    else:
        st.session_state.run_ml = False
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Skip & Proceed to Re-upload →"):
            st.session_state.step = 5
            st.rerun()

# ============================================================
# STEP 5 — RE-UPLOAD CORRECTED FILE
# ============================================================
elif st.session_state.step == 5:
    st.markdown("<div class='section-header'>📁 Step 5 — Re-upload Corrected File</div>", unsafe_allow_html=True)

    st.markdown("""
        <div class='info-box'>
            <b>Instructions:</b><br>
            • Please correct all issues flagged in the Validation Report<br>
            • Upload the corrected vendor file below<br>
            • The system will re-validate automatically
        </div>
    """, unsafe_allow_html=True)

    uploaded_corrected = st.file_uploader("Upload corrected vendor file", type=['xlsx'])

    if uploaded_corrected is not None:
        df_corrected = pd.read_excel(uploaded_corrected)
        df_corrected = standardize_vendor_file(df_corrected)
        warnings_corrected = validate_vendor_file(df_corrected)

        if len(warnings_corrected) == 0:
            st.markdown("<div class='success-msg'>✅ No issues found! File is clean and ready for ID generation.</div>", unsafe_allow_html=True)
            st.session_state.df_corrected = df_corrected
            if st.button("Proceed to ID Generation →"):
                st.session_state.step = 6
                st.rerun()
        else:
            st.markdown(f"<div class='error-msg'>⚠️ {len(warnings_corrected)} issue(s) still found! Please fix and re-upload.</div>", unsafe_allow_html=True)
            df_warn = pd.DataFrame(warnings_corrected)
            st.dataframe(df_warn, use_container_width=True, hide_index=True)

# ============================================================
# STEP 6 — ID GENERATION & FINAL OUTPUT
# ============================================================
elif st.session_state.step == 6:
    st.markdown("<div class='section-header'>🆔 Step 6 — ID Generation & Final Output</div>", unsafe_allow_html=True)

    df_corrected = st.session_state.df_corrected
    option_ids, sku_ids = generate_ids(df_corrected)
    df_corrected['Option ID'] = option_ids
    df_corrected['SKU ID'] = sku_ids

    if st.session_state.run_ml and st.session_state.risk_predictions is not None:
        df_corrected = df_corrected.merge(
            st.session_state.risk_predictions[['Supplier Option ID', 'Risk Level', 'Risk Label']],
            on='Supplier Option ID', how='left'
        )

    st.markdown("<div class='success-msg'>✅ Option IDs and SKU IDs generated successfully!</div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{len(df_corrected)}</div><div class='metric-label'>Total SKUs</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{df_corrected['Option ID'].nunique()}</div><div class='metric-label'>Unique Option IDs</div></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{df_corrected['SKU ID'].nunique()}</div><div class='metric-label'>Unique SKU IDs</div></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("**📋 Final Output Preview:**")
    st.dataframe(df_corrected, use_container_width=True, hide_index=True)

    output = io.BytesIO()
    df_corrected.to_excel(output, index=False, engine='openpyxl')
    output.seek(0)

    st.markdown("<br>", unsafe_allow_html=True)
    st.download_button(
        label="⬇️ Download Final Output (Excel)",
        data=output,
        file_name="OptiCatalog_Final_Output.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='success-msg'>🎉 Process Complete! Your file is ready for Shopify cataloguing.</div>", unsafe_allow_html=True)
