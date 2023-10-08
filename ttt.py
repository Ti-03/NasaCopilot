try:
    from enum import Enum
    from io import BytesIO, StringIO
    from typing import Union
 
    import pandas as pd
    import streamlit as st
except Exception as e:
    print(e)
 
STYLE = """
<style>
img {
    max-width: 100%;
}
</style>
"""
 
def main():
    """Run this function to display the Streamlit app"""
    st.info(_doc_)
    st.markdown(STYLE, unsafe_allow_html=True)
 
    file = st.file_uploader("Upload file", type=["csv", "png", "jpg"])
    show_file = st.empty()
 
    if not file:
        show_file.info("Please upload a file of type: " + ", ".join(["csv", "png", "jpg"]))
        return
 
    content = file.getvalue()
 
    if isinstance(file, BytesIO):
        show_file.image(file)
    else:
        data = pd.read_csv(file)
        st.dataframe(data.head(10))
    file.close()
 
main()