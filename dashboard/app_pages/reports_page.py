import streamlit as st
import requests
from components.ui_helpers import API_BASE, auth_headers, api_get


def render():
    st.title("Reports")
    st.caption("Download analytics and data reports")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("PDF Report")
        st.markdown("""
        A comprehensive PDF report including:
        - Dataset summary statistics
        - Key Performance Indicators (KPIs)
        - Column analysis
        - Data quality metrics
        """)

        if st.button("Generate & Download PDF", type="primary", use_container_width=True):
            with st.spinner("Generating PDF report..."):
                try:
                    resp = requests.get(
                        f"{API_BASE}/report/pdf",
                        headers=auth_headers(),
                        timeout=30,
                    )
                    if resp.status_code == 200:
                        st.download_button(
                            "Download PDF Report",
                            data=resp.content,
                            file_name="smartdata_report.pdf",
                            mime="application/pdf",
                            use_container_width=True,
                        )
                        st.success("PDF generated successfully!")
                    else:
                        st.error(f"Failed to generate PDF: {resp.text}")
                except requests.exceptions.ConnectionError:
                    st.warning("Backend offline. PDF generation requires a running backend.")

    with col2:
        st.subheader("CSV Export")
        st.markdown("""
        Export your cleaned data as CSV:
        - Fully transformed dataset
        - All ETL operations applied
        - Ready for further analysis
        """)

        if st.button("Export Cleaned CSV", use_container_width=True):
            with st.spinner("Generating CSV..."):
                try:
                    resp = requests.get(
                        f"{API_BASE}/report/csv",
                        headers=auth_headers(),
                        timeout=30,
                    )
                    if resp.status_code == 200:
                        st.download_button(
                            "Download CSV",
                            data=resp.content,
                            file_name="smartdata_cleaned.csv",
                            mime="text/csv",
                            use_container_width=True,
                        )
                        st.success("CSV ready for download!")
                    else:
                        st.error(f"Export failed: {resp.text}")
                except requests.exceptions.ConnectionError:
                    st.warning("Backend offline. CSV export requires a running backend.")

    st.divider()
    st.subheader("Report History")
    st.info("Report metadata is stored in MongoDB. Connect the backend to view history.")

    # Summary KPIs
    st.divider()
    st.subheader("Analytics Summary")
    summary = api_get("analytics/summary")
    if summary and "error" not in str(summary):
        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Total Rows", f"{summary.get('total_rows', 0):,}")
        col_b.metric("Columns", summary.get("total_columns", 0))
        col_c.metric("Missing Values", summary.get("missing_values", 0))

        if summary.get("describe"):
            st.subheader("Statistical Description")
            import pandas as pd
            desc_df = pd.DataFrame(summary["describe"]).T.round(4)
            st.dataframe(desc_df, use_container_width=True)
    else:
        st.info("Upload data to generate analytics summary.")
