"""Streamlit Phase 2 chat app on top of the existing Phase 1 backend workflow."""

from __future__ import annotations

from pathlib import Path
import json

import streamlit as st

from src.chat_orchestrator import ChatOrchestrator, ConversationState
from src.response_formatter import format_error_message


def _init() -> tuple[ChatOrchestrator, ConversationState]:
    orchestrator = ChatOrchestrator()

    if "conversation_state" not in st.session_state:
        state = orchestrator.init_state()
        st.session_state.conversation_state = state
        st.session_state.chat_history = [
            (
                "assistant",
                "Hello! Describe your HE evidence request in natural language, and upload a rationale .docx when ready.",
            )
        ]
    else:
        state = st.session_state.conversation_state

    return orchestrator, state


def _render_chat_history() -> None:
    for role, msg in st.session_state.chat_history:
        with st.chat_message(role):
            st.markdown(msg)


def _append_chat(role: str, content: str) -> None:
    st.session_state.chat_history.append((role, content))


def main() -> None:
    st.set_page_config(page_title="Phase 2 HE Chat", layout="wide")
    st.title("Phase 2: Conversational HE Parameter Prep")

    orchestrator, conv_state = _init()

    left_col, right_col = st.columns([2, 1])

    with left_col:
        _render_chat_history()

        user_message = st.chat_input("Describe your evidence search request...")
        if user_message:
            _append_chat("user", user_message)
            assistant_reply = orchestrator.handle_user_message(conv_state, user_message)
            _append_chat("assistant", assistant_reply)
            st.rerun()

        uploaded = st.file_uploader(
            "Upload rationale .docx",
            type=["docx"],
            accept_multiple_files=False,
            key="rationale_uploader",
        )
        if uploaded is not None and uploaded.size > 0:
            assistant_reply = orchestrator.handle_rationale_upload(
                conv_state,
                file_name=uploaded.name,
                file_bytes=uploaded.getvalue(),
            )
            _append_chat("assistant", assistant_reply)
            st.rerun()

        run_clicked = st.button("Run Phase 1 Workflow", type="primary")
        if run_clicked:
            try:
                reply, publications, output_path = orchestrator.run_workflow(conv_state)
                _append_chat("assistant", reply)
                if publications:
                    _append_chat(
                        "assistant",
                        "Top selected publications:\n" + "\n".join(
                            [
                                f"- {row['Publication Citation']} (Ranking: {row['Ranking']})"
                                for row in publications[:5]
                            ]
                        ),
                    )
                st.session_state.publications = publications
                st.session_state.output_path = str(output_path) if output_path else ""
            except Exception as exc:
                _append_chat("assistant", format_error_message(exc))
            st.rerun()

    with right_col:
        st.subheader("Structured Task Fields")
        st.json(conv_state.task)

        st.subheader("Session")
        st.write(f"Session ID: `{conv_state.session_id}`")
        st.write(f"Rationale uploaded: `{conv_state.has_rationale}`")
        if conv_state.rationale_path:
            st.write(f"Rationale path: `{conv_state.rationale_path}`")

        st.subheader("Latest Result Metadata")
        if conv_state.latest_result:
            st.json(conv_state.latest_result)
        else:
            st.caption("No workflow run yet.")

        publications = st.session_state.get("publications", [])
        if publications:
            st.subheader("Selected Publications")
            st.dataframe(publications, use_container_width=True)

        output_path_str = st.session_state.get("output_path", "")
        if output_path_str:
            output_path = Path(output_path_str)
            if output_path.exists():
                st.download_button(
                    label="Download Excel Output",
                    data=output_path.read_bytes(),
                    file_name=output_path.name,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )

        with st.expander("Debug: Raw conversation state"):
            st.code(json.dumps(conv_state.__dict__, indent=2), language="json")


if __name__ == "__main__":
    main()
