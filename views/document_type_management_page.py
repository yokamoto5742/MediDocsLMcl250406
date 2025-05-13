import streamlit as st

from utils.error_handlers import handle_error
from utils.exceptions import AppError
from utils.document_type_manager import get_all_document_types, create_document_type, delete_document_type, update_document_type_order
from ui_components.navigation import change_page


@handle_error
def document_type_management_ui():
    if st.button("作成画面に戻る", key="back_to_main_from_doc_type"):
        change_page("main")
        st.rerun()

    with st.form(key="add_document_type_form"):
        new_doc_type = st.text_input("文書種類", placeholder="追加する文書種類を入力してください", label_visibility="collapsed")
        submit = st.form_submit_button("追加")

        if submit and new_doc_type:
            success, message = create_document_type(new_doc_type)
            if success:
                st.success(message)
            else:
                raise AppError(message)
            st.rerun()

    if "show_move_options_doc" not in st.session_state:
        st.session_state.show_move_options_doc = {}

    document_types = get_all_document_types()

    for i, doc_type in enumerate(document_types):
        col1, col2, col3 = st.columns([4, 1, 1])
        with col1:
            st.write(doc_type)

        with col2:
            if doc_type not in st.session_state.show_move_options_doc:
                if st.button("⇅", key=f"move_doc_{doc_type}"):
                    st.session_state.show_move_options_doc[doc_type] = True
                    st.rerun()
            else:
                move_options_container = st.container()
                with move_options_container:
                    move_col1, move_col2, move_col3 = st.columns(3)

                    with move_col1:
                        if i > 0 and st.button("↑", key=f"up_action_doc_{doc_type}"):
                            success, message = update_document_type_order(doc_type, i - 1)
                            if success:
                                st.success(message)
                                del st.session_state.show_move_options_doc[doc_type]
                            else:
                                raise AppError(message)
                            st.rerun()

                    with move_col2:
                        if i < len(document_types) - 1 and st.button("↓", key=f"down_action_doc_{doc_type}"):
                            success, message = update_document_type_order(doc_type, i + 1)
                            if success:
                                st.success(message)
                                del st.session_state.show_move_options_doc[doc_type]
                            else:
                                raise AppError(message)
                            st.rerun()

                    with move_col3:
                        if st.button("✕", key=f"cancel_move_doc_{doc_type}"):
                            del st.session_state.show_move_options_doc[doc_type]
                            st.rerun()

        with col3:
            if st.button("削除", key=f"delete_doc_{doc_type}"):
                success, message = delete_document_type(doc_type)
                if success:
                    st.success(message)
                else:
                    raise AppError(message)
                st.rerun()
