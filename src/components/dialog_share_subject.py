import streamlit as st
import segno
import io


@st.dialog("Share Class Link")
def share_subject_dialog(subject_name, subject_code):

    join_url = f"https://snapclass-main.streamlit.app/?join-code={subject_code}"

    st.header("Scan to Join")

    # QR Code
    qr = segno.make(join_url)

    out = io.BytesIO()
    qr.save(out, kind="png", scale=10, border=1)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Copy Link")

        st.code(join_url)

        st.link_button(
            "Open Class Link",
            join_url,
            width="stretch"
        )

        st.code(subject_code)

    with col2:
        st.markdown("### Scan to Join")

        st.image(
            out.getvalue(),
            caption="QR Code for class joining"
        )