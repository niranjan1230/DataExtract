import streamlit as st
import PyPDF2
import pdfplumber
import pandas as pd
import re

# Function to extract text from PDF using PyPDF2
def extract_text_with_pypdf2(pdf_file):
    try:
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        st.write(f"PyPDF2 extraction failed: {e}")
        return None

# Function to extract text from PDF using pdfplumber
def extract_text_with_pdfplumber(pdf_file):
    try:
        text = ""
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text
    except Exception as e:
        st.write(f"pdfplumber extraction failed: {e}")
        return None

# Function to extract name and PAN using regex
def extract_pan_details(text):
    # Adjust the regex to remove spaces from PAN and handle multiple lines
    # Find the PAN number (5 letters, 4 digits, 1 letter), possibly with spaces
    pan = re.search(r'[A-Z]{5}\s?[0-9]{4}\s?[A-Z]', text)
    
    # Find the name (usually appears near "Name")
    name = re.search(r'Name\s*([A-Za-z\s]+)', text)
    
    # Extract name and PAN, strip any extra spaces from the PAN
    extracted_name = name.group(1).strip() if name else "Not found"
    extracted_pan = pan.group(0).replace(" ", "").strip() if pan else "Not found"
    
    return extracted_name, extracted_pan

# Streamlit app
st.title("PDF PAN Card Extractor")

# File uploader
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    st.write("PDF file uploaded successfully!")

    # Try extracting text with PyPDF2 first
    text = extract_text_with_pypdf2(uploaded_file)

    # If PyPDF2 fails, fall back to pdfplumber
    if not text:
        st.write("Trying pdfplumber for text extraction...")
        text = extract_text_with_pdfplumber(uploaded_file)

    # If text was extracted
    if text:
        st.write("Text extraction successful!")
        
        # Extract PAN details
        name, pan = extract_pan_details(text)
        
        # Show extracted details
        st.write(f"Name: {name}")
        st.write(f"Permanent Account Number (PAN): {pan}")
        
        # Convert to DataFrame for CSV download
        data = {'Name': [name], 'PAN': [pan]}
        df = pd.DataFrame(data)
        
        # Download CSV
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download as CSV",
            data=csv,
            file_name='pan_details.csv',
            mime='text/csv',
        )
    else:
        st.write("Text extraction failed. Please try another PDF or check the file format.")
else:
    st.write("Please upload a PDF file to start extraction.")
